"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffleInstore] InstoreRaffleModule.py                      """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/10/2021 20:31:19                                     """
"""   Updated: 03/10/2021 06:49:47                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random

import questionary

from questionary import Choice

from services.notifier.Discord.EnterRaffleNotifier import NotifyEndRaffleEntries, NotifyEnteredAccount, NotifyCourirInstoreEntered
from core.configuration.Configuration import Configuration

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from .InstoreRaffleTask import *

from modules.Raffle.Courir.utils.ScraperUtils import *
from utilities.logger import TaskLogger

class InstoreRaffleModule:
    
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyCourirInstoreEntered(self.module, task, self.raffle, task.walletURL)

    def PromptRaffle(self):

        answer = questionary.text("Enter link here:", default="https://courir.captainwallet.com/fr-fr/enroll/raffle-loyalty").ask()

        try:
            raffle = scrapeRaffle(answer)
        except Exception as error:
            raffle = None
            Logger.error("Error when fetching Raffles!")
            Logger.error(str(error))
            
        return raffle

    def PromptSizeRange(self):

        Choices = []

        for size in self.raffle['sizes'][self.raffle['productId']]:
            label = "{} EU".format(size['label'])

            Choices.append(Choice(
                title=[
                    ("class:purple", label),
                ],
                value={
                    "name": label,
                    "id": size['id'],
                    "pid": size['sneaker_id']
                }
            ))

        answers = questionary.checkbox(
            "Which size(s) do you want to enter?",
            choices=Choices,
            validate=lambda text: True if len(text) > 0 else "You need to select at least one size to enter!"
        ).ask()

        return answers

    def PromptShop(self):

        Choices = []

        for store in self.raffle['stores']:
            Choices.append(Choice(
                title=[
                    ("class:purple", '{message}'.format(message=store['name'])),
                    ("class:text", " ["),
                    ("class:blue", '{message}'.format(message=store['city'])),
                    ("class:text", "]")
                ],
                value={
                    "name": store['name'],
                    "content": store
                }
            ))
        answer = questionary.select(
            "Which store do you want to enter?",
            choices=Choices,
        ).ask()

        return answer
        
    def __init__(self) -> None:
        self.moduleName = "Courir"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "EnterRaffleInstore"

        self.raffle = self.PromptRaffle()

        if self.raffle is None:
            return

        self.sizeRange = self.PromptSizeRange()
        self.shop = self.PromptShop()

        if (self.sizeRange is None or self.shop is None):
            return 

        self.raffle['sizeRange'] = self.sizeRange
        self.raffle['shop'] = self.shop
        
        del self.raffle['sizes']
        del self.raffle['stores']
        
        """ Load Profiles & Proxy """
        ProfilesManager(self.moduleName, self.subModuleName).loadProfiles()
        Profiles = ProfilesManager().getProfiles()

        if Profiles is None:
            return

        ProfileName = ProfilesManager().getProfileName()

        if (Configuration().getConfiguration()['ProxyLess'] == False):
            ProxyManager(self.moduleName)

        profilesNumber = len(Profiles)

        """ UI Utilities """
        DiscordRPC().updateRPC("Running {}".format(self.moduleName))
        setTitle("SourceRaffles [{}] | {}".format(self.moduleName, self.subModuleName))

        """ Logger """
        now = datetime.now()
        self.date = "{:02d}_{:02d}_{:02d}-{:02d}-{:02d}".format(
            now.day, now.month, now.hour, now.minute, now.second
        )
        self.loggerFileName = (
            f"logs/{self.moduleName}/{self.subModuleName}-{self.date}.csv"
        )
        self.TaskLogger = TaskLogger(self.loggerFileName)
        loggerStatus = self.TaskLogger.createLogger(Profiles, ["Product", "Size", "Shop"])

        if loggerStatus == None:
            return

        """ Settings """

        self.threads = PromptThread("1")

        if self.threads == 1:
            self.minDelay, self.maxDelay = PromptDelay("5, 10")
        else:
            self.minDelay = 0
            self.maxDelay = 0

        if self.minDelay == None:
            return

        tasks = []
        successTask: int = 0
        failedTask: int = 0
        runningLoop = True

        for index, profile in enumerate(Profiles):
            if profile["status"] != "PENDING" and profile["status"] != "FAILED":
                Profiles.remove(profile)

        while runningLoop:
            if self.threads > 1:
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    for index, profile in enumerate(Profiles):

                        if (
                            profile["status"] == "PENDING"
                            or profile["status"] == "FAILED"
                        ):
                            tasks.append(
                                executor.submit(
                                    EnterRaffleTask,
                                    index,
                                    profilesNumber,
                                    profile,
                                    self.raffle,
                                )
                            )

                    for task in as_completed(tasks):

                        TaskResult = task.result()

                        if TaskResult.success:
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(
                            f"SourceRaffles - Courir Instore [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )
            else:
                printSeparator()
                for index, profile in enumerate(Profiles):

                    if profile["status"] == "PENDING" or profile["status"] == "FAILED":
                        TaskResult = EnterRaffleTask(
                            index, profilesNumber, profile, self.raffle
                        )

                        if TaskResult.success:
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(
                            f"SourceRaffles - Courir Instore [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )

                        printSeparator()
                        print("")
                        waitUntil(random.randint(self.minDelay, self.maxDelay))
                        print("")

            NotifyEndRaffleEntries(
                self.module,
                profilesNumber,
                failedTask,
                successTask,
                ProfileName,
                self.loggerFileName,
                self.raffle
            )
            
            setTitle(
                f"SourceRaffles - Naked [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}"
            )

            if failedTask > 0:
                runningLoop = questionary.confirm(
                    f"Relaunch failed tasks? ({str(failedTask)} tasks to relaunch)"
                ).ask()

                remaining = failedTask
                failedTask = 0
                successTask = 0

            else:
                runningLoop = False
                Logger.info("No more failed tasks!")
                input("Back to main menu?")

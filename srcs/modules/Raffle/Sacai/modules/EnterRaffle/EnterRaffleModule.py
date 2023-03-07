"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleModule.py                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:14                                     """
"""   Updated: 22/10/2021 14:56:50                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random

import questionary
from questionary import Choice

from services.notifier.Discord.EnterRaffleNotifier import NotifyEndRaffleEntries, NotifyEnteredAccount
from core.configuration.Configuration import Configuration

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from .EnterRaffleTask import EnterRaffleTask

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger

class EnterRaffleModule:
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyEnteredAccount(self.module, task, self.raffle)

    def PromptRaffle(self):

        token = User().getToken()

        response = requests.get(
            f"{getAPI()}/v3/raffles",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "moduleName": self.moduleName
            }
        )

        responseData = response.json()

        if (responseData['status'] is False):
            Logger.error("Error has occured! Open ticket please.")
            Logger.debug(response.text)
            return None

        raffles = [raffle for raffle in responseData['raffles'] if raffle["active"]]

        if len(raffles) == 0:
            Logger.error(
                "No raffles availables.. If you see a live raffle not live here contact the Team!"
            )
            return None

        Choices = []
        for raffle in raffles:
            Choices.append(questionary.Choice(
                title=[
                    ("class:purple", raffle['name']),
                    ("class:text", " [ "),
                    ("class:grey", '{message} successfull entries'.format(message=raffle['entriesCount'])),
                    ("class:text", " ]")
                ],
                value={
                    "raffle": raffle
                }
            ))

        Choices.append(
            questionary.Choice(title=[("class:red", "Exit")], value={"slug": "Exit"})
        )

        answer = questionary.select(
            "Which raffles do you want to run?",
            choices=Choices,
        ).ask()

        if "slug" in answer:
            return None
        else:
            if (len(answer["raffle"]["metadata"]) > 0):
                answer["raffle"]["metadata"] = answer["raffle"]["metadata"][0]
            return answer["raffle"]

    def PromptSizeRange(self):

        Choices = []

        for size in self.raffle['metadata']['sizes']:
            
            Choices.append(Choice(
                title=[
                    ("class:purple", '{message: <8}'.format(message=size['label'])),
                    ("class:text", " ["),
                    ("class:blue", '{message} pairs'.format(message=size['inventory'])),
                    ("class:text", "]")
                ],
                value={
                    "name": size['label'],
                    "id": size['id']
                }
            ))
        answers = questionary.checkbox(
            "Which size(s) do you want to enter?",
            choices=Choices,
            validate=lambda text: True if len(text) > 0 else "You need to select at least one size to enter!"
        ).ask()

        return answers

    def __init__(self) -> None:
        self.moduleName = "Sacai"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "EnterRaffle"

        self.raffle = self.PromptRaffle()

        if self.raffle is None:
            return

        self.sizeRange = self.PromptSizeRange()
        if (self.sizeRange is None):
            return 

        self.raffle['sizeRange'] = self.sizeRange

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
        loggerStatus = self.TaskLogger.createLogger(Profiles, ["Product", "Size"])

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
                            f"SourceRaffles - Sacai [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
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
                            f"SourceRaffles - Sacai [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
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
                f"SourceRaffles - Sacai [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}"
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

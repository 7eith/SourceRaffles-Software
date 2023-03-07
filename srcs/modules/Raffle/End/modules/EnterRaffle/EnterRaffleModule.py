"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleModule.py                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:14                                     """
"""   Updated: 11/09/2021 17:07:33                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
import json
from services.notifier.Discord.EnterRaffleNotifier import NotifyEndRaffleEntries, NotifyEnteredAccount
from core.configuration.Configuration import Configuration
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.Raffle.End.modules.EnterRaffle.EnterRaffleTask import EnterRaffleTask
from modules.Controller import ModuleController
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager
from utilities.logger import TaskLogger


class EnterRaffleModule:
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        for raffleInfo in self.raffleListLog:
            NotifyEnteredAccount(self.module, task, raffleInfo)

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

        Logger.debug(raffles)

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

        try:
            answer = questionary.checkbox(
                "Which raffle(s) do you want to launch?",
                choices=Choices,
            ).ask()
            listRaffle = [raffleInfo["raffle"] for raffleInfo in answer]
        except IndexError:
            Logger.error("Error while choosing raffles, please select with the spacebar then confirm with enter !")
        else:
            return listRaffle

    def __init__(self) -> None:
        self.moduleName = "End"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "EnterRaffle"

        Con = True
        while Con:
            self.raffleList = self.PromptRaffle()
            if self.raffleList != []:
                Con = False
            else:
                Logger.error("Error while choosing raffles, please select with the spacebar then confirm with enter !")
                input("Press to continue ...")

        self.raffleListLog = self.raffleList.copy()
        Logger.debug(self.raffleList)

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
        loggerStatus = self.TaskLogger.createLogger(Profiles, ["Product"])

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
                                    self.raffleList.copy(),
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
                            f"SourceRaffles - End [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )
            else:
                printSeparator()
                for index, profile in enumerate(Profiles):

                    if profile["status"] == "PENDING" or profile["status"] == "FAILED":
                        TaskResult = EnterRaffleTask(
                            index, profilesNumber, profile, self.raffleList.copy()
                        )

                        if TaskResult.success:
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(
                            f"SourceRaffles - End [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
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
                self.raffleList
            )
            
            setTitle(
                f"SourceRaffles - End [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}"
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


if __name__ == '__main__':
    print(EnterRaffleModule().PromptRaffle())
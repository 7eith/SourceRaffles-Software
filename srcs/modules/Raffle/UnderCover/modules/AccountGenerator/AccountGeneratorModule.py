"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorModule.py                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 04/10/2021 06:58:57                                     """
"""   Updated: 22/10/2021 18:41:05                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
from services.notifier.Discord.AccountCreateNotifier import *
from core.configuration.Configuration import Configuration

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from .AccountGeneratorTask import AccountGeneratorTask

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger

class AccountGeneratorModule:
    
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyCreatedAccount(self.module, task)

    def __init__(self) -> None:
        self.moduleName = "UnderCover"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "AccountGenerator"

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
        loggerStatus = self.TaskLogger.createLogger(Profiles)

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


        while runningLoop:
            for index, profile in enumerate(Profiles):
                if profile["status"] != "PENDING" and profile["status"] != "FAILED":
                    Profiles.remove(profile)
                    
            if self.threads > 1:
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    for index, profile in enumerate(Profiles):

                        if (
                            profile["status"] == "PENDING"
                            or profile["status"] == "FAILED"
                        ):
                            tasks.append(
                                executor.submit(
                                    AccountGeneratorTask,
                                    index,
                                    profilesNumber,
                                    profile
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
                            f"SourceRaffles - UnderCover [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )
            else:
                printSeparator()
                for index, profile in enumerate(Profiles):

                    if profile["status"] == "PENDING" or profile["status"] == "FAILED":
                        TaskResult = AccountGeneratorTask(
                            index, profilesNumber, profile
                        )

                        if TaskResult.success:
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(
                            f"SourceRaffles - UnderCover [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )

                        printSeparator()
                        print("")
                        waitUntil(random.randint(self.minDelay, self.maxDelay))
                        print("")

            NotifyEndAccountCreator(
                self.module,
                profilesNumber,
                failedTask,
                successTask,
                ProfileName,
                self.loggerFileName
            )
            
            setTitle(
                f"SourceRaffles - UnderCover [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}"
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

"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorModule.py                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:11                                     """
"""   Updated: 03/10/2021 09:25:42                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from services.notifier.Discord.AccountCreateNotifier import NotifyVerifiedAccount, NotifyEndAccountVerifier

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger
from .AccountVerifierTask import AccountVerifierTask

class AccountVerifierModule():

    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyVerifiedAccount(self.module, task)

    def __init__(self) -> None:
        self.moduleName = "Naked"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "AccountVerifier"

        """ Load Profiles & Proxy """
        ProfilesManager(self.moduleName, self.subModuleName).loadProfiles()
        Profiles = ProfilesManager().getProfiles()

        if (Profiles is None):
            return

        ProfileName = ProfilesManager().getProfileName()
        ProxyManager(self.moduleName)
        
        profilesNumber = len(Profiles)
        
        """ UI Utilities """
        DiscordRPC().updateRPC("Running {}".format(self.moduleName))
        setTitle("SourceRaffles [{}] | {}".format(self.moduleName, self.subModuleName))

        """ Logger """
        now = datetime.now()
        self.date = '{:02d}_{:02d}_{:02d}-{:02d}-{:02d}'.format(now.day, now.month, now.hour, now.minute, now.second)
        self.loggerFileName = f"logs/{self.moduleName}/{self.subModuleName}-{self.date}.csv"
        self.TaskLogger = TaskLogger(self.loggerFileName)
        loggerStatus = self.TaskLogger.createLogger(Profiles)
        
        if (loggerStatus == None):
            return
        
        """ Settings """

        self.threads = PromptThread("5")

        if (self.threads == 1):
            self.minDelay, self.maxDelay = PromptDelay("5, 10")
        else:
            self.minDelay = 0
            self.maxDelay = 0
            
        if (self.minDelay == None):
            return 

        tasks = []
        successTask: int = 0
        failedTask: int = 0
        runningLoop = True

        for index, profile in enumerate(Profiles):
            if (profile['status'] != "PENDING" and profile['status'] != "FAILED"):
                Profiles.remove(profile)

        while runningLoop:
            if (self.threads > 1):
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    for index, profile in enumerate(Profiles):

                        if (profile['status'] == "PENDING" or profile['status'] == "FAILED"):
                            tasks.append(executor.submit(AccountVerifierTask, index, profilesNumber, profile))

                    for task in as_completed(tasks):

                        TaskResult = task.result()

                        if (TaskResult.success):
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(f"SourceRaffles - Naked [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}")
            else:
                printSeparator()
                for index, profile in enumerate(Profiles):

                    if (profile['status'] == "PENDING" or profile['status'] == "FAILED"):
                        TaskResult = AccountVerifierTask(index, profilesNumber, profile)
                        
                        if (TaskResult.success):
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)
                        
                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(f"SourceRaffles - Naked [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}")

                        printSeparator()
                        print("")
                        waitUntil(random.randint(self.minDelay, self.maxDelay))
                        print("")

            NotifyEndAccountVerifier(self.module, profilesNumber, failedTask, successTask, ProfileName, self.loggerFileName)
            setTitle(f"SourceRaffles - Naked [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}")
            
            if (failedTask > 0):
                runningLoop = questionary.confirm(f"Relaunch failed tasks? ({str(failedTask)} tasks to relaunch)").ask()

                remaining = failedTask
                failedTask = 0
                successTask = 0
                        
            else:
                runningLoop = False
                Logger.info("No more failed tasks!")
                input("Back to main menu?")

            
        
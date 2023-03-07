"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorModule.py                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:11                                     """
"""   Updated: 13/11/2021 21:35:47                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from services.notifier.Discord.AccountCreateNotifier import NotifyCreatedAccount, NotifyEndAccountCreator

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger
from .AccountGeneratorTask import AccountGeneratorTask

class AccountGeneratorModule():

    def __init__(self) -> None:
        self.moduleName = "Naked"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "AccountGenerator"

        DiscordRPC().updateRPC("Running {}".format(self.moduleName))
        setTitle("SourceRaffles [{}] | {}".format(self.moduleName, self.subModuleName))

        """ Load Profiles & Proxy """
        ProfilesManager(self.moduleName, self.subModuleName).loadProfiles()
        self.Profiles = ProfilesManager().getProfiles()

        if len(self.Profiles) == 0:
            return

        self.ProfileName = ProfilesManager().getProfileName()

        ProxyManager(self.moduleName)

        """ Logger """
        now = datetime.now()
        self.date = "{:02d}_{:02d}_{:02d}-{:02d}-{:02d}".format(
            now.day, now.month, now.hour, now.minute, now.second
        )
        self.loggerFileName = (
            f"logs/{self.moduleName}/{self.subModuleName}-{self.date}.csv"
        )
        self.TaskLogger = TaskLogger(self.loggerFileName)
        loggerStatus = self.TaskLogger.createLogger(self.Profiles)
        
        if loggerStatus == None:
            return
        
        """ Settings """

        self.threads = PromptThread("1")
        self.minDelay, self.maxDelay = PromptDelay("5, 10")
        self.lock = Semaphore(self.threads)

        runningLoop = True
        profileTasks = []

        for profile in self.Profiles:
            if (profile['status'] != "SUCCESS" and profile['status'] != "CONFIRMED"):
                profileTasks.append(profile)

        Logger.info(f"[Profiles] Removed {len(self.Profiles) - len(profileTasks)} success tasks from Profile.")
        self.profilesNumber = len(profileTasks)

        while runningLoop:

            """
                Clear Tasks with SUCCESS 
                Resetup new batch 
            """

            for index, profile in enumerate(profileTasks):

                if (profile['status'] == "SUCCESS" or profile['status'] == "CONFIRMED"):
                    del profileTasks[index]

            self.profilesNumber = len(profileTasks)
            self.failedTask = 0
            self.successTask = 0

            setTitle(
                f"SourceRaffles - {self.moduleName} [{self.ProfileName}] | Success: {str(self.successTask)} - Failed {str(self.failedTask)} - Remaining {str(self.profilesNumber)}"
            )

            """
                Launch anyways with PoolExecutor
            """
            
            tasks = []
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for index, profile in enumerate(profileTasks):

                    tasks.append(
                        executor.submit(
                            self.runTask, index, profile
                        )
                    )

            NotifyEndAccountCreator(
                self.module,
                self.profilesNumber,
                self.failedTask,
                self.successTask,
                self.ProfileName,
                self.loggerFileName
            )
            
            setTitle(
                f"SourceRaffles - {self.moduleName} [{self.ProfileName}] | Ended! Tasks: {str(self.successTask)}/{str(self.failedTask)}"
            )

            if self.failedTask > 0:
                runningLoop = questionary.confirm(
                    f"Relaunch failed tasks? ({str(self.failedTask)} tasks to relaunch)"
                ).ask()

            else:
                runningLoop = False
                Logger.info(f"[{self.moduleName}] No more failed tasks!")
                input(Logger.formatForInput("Press ENTER to back to the main menu!"))

    def runTask(self, index, profile):
        TaskResult = AccountGeneratorTask(index, self.profilesNumber, profile)

        self.lock.acquire()
        
        if (TaskResult.success):
            self.successTask += 1
        else:
            self.failedTask += 1
        
        remaining = self.profilesNumber - (self.failedTask + self.successTask + 1)
        
        if (remaining == -1):
            remaining = 0

        setTitle(
            f"SourceRaffles - {self.moduleName} [{self.ProfileName}] | Success: {str(self.successTask)} - Failed {str(self.failedTask)} - Remaining {str(remaining)}"
        )

        self.lock.release()

        self.TaskLogger.logTask(TaskResult)
        NotifyCreatedAccount(self.module, TaskResult)

        if (self.maxDelay > 0):
            if (self.threads > 1):
                waitUntil(random.randint(self.minDelay, self.maxDelay), True)
            else:
                printSeparator()
                print("")
                waitUntil(random.randint(self.minDelay, self.maxDelay))
                print("")

        return TaskResult
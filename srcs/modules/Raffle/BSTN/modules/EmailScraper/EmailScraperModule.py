"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorModule.py                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:11                                     """
"""   Updated: 10/09/2021 04:01:43                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from services.notifier.Discord.EmailScraperNotifier import NotifyEndEmailScraper, NotifyScrapedEmail

from modules.Controller import ModuleController

from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger
from .EmailScraperTask import EntryScraperTask
from imap_tools import MailBox, A

class EmailScraperModule:

    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyScrapedEmail(self.module, task)

    def __init__(self) -> None:
        self.moduleName = "BSTN"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "EmailScraper"

        """ Load Profiles """
        ProfilesManager(self.moduleName, self.subModuleName).loadProfiles()
        Profiles = ProfilesManager().getProfiles()

        if (Profiles is None):
            return

        ProfileName = ProfilesManager().getProfileName()
        
        profilesNumber = len(Profiles)
        
        """ UI Utilities """
        DiscordRPC().updateRPC("Running {}".format(self.moduleName))
        setTitle("SourceRaffles [{}] | {}".format(self.moduleName, self.subModuleName))

        """ Logger """
        now = datetime.now()
        self.date = '{:02d}_{:02d}_{:02d}-{:02d}-{:02d}'.format(now.day, now.month, now.hour, now.minute, now.second)
        self.loggerFileName = f"logs/{self.moduleName}/{self.subModuleName}-{self.date}.csv"
        self.TaskLogger = TaskLogger(self.loggerFileName)
        self.loggerPath = f"shops/{self.moduleName}/{self.subModuleName}-{self.date}-links.csv"

        tasks = []
        successTask: int = 0
        failedTask: int = 0
        runningLoop = True

        self.minDelay = 2
        self.maxDelay = 5

        for index, profile in enumerate(Profiles):
            if (profile['status'] != "PENDING" and profile['status'] != "FAILED"):
                Profiles.remove(profile)

        while runningLoop:
            for index, profile in enumerate(Profiles):

                if (profile['status'] == "PENDING" or profile['status'] == "FAILED"):

                    TaskResult = EntryScraperTask(index, profilesNumber, profile, self.loggerPath)

                    if (TaskResult.success):
                        successTask += 1
                    else:
                        failedTask += 1

                    self.endedTask(TaskResult)

                    remaining = profilesNumber - (failedTask + successTask + 1)
                    setTitle(f"SourceRaffles - BSTN [{ProfileName}] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}")

                    printSeparator()
                    print("")
                    waitUntil(random.randint(self.minDelay, self.maxDelay))
                    print("")

            NotifyEndEmailScraper(self.module, profilesNumber, failedTask, successTask, ProfileName, self.loggerPath)
            setTitle(f"SourceRaffles - BSTN [{ProfileName}] | Ended! Tasks: {str(successTask)}/{str(failedTask)}")
            
            if (failedTask > 0):
                runningLoop = questionary.confirm(f"Relaunch failed tasks? ({str(failedTask)} tasks to relaunch)").ask()

                remaining = failedTask
                failedTask = 0
                successTask = 0
                        
            else:
                runningLoop = False
                Logger.info("No more failed tasks!")
                input("Back to main menu?")
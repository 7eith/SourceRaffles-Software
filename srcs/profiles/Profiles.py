"""********************************************************************"""
"""                                                                    """
"""   [profiles] Profiles.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 25/08/2021 14:28:47                                     """
"""   Updated: 10/10/2021 07:58:04                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from core.configuration.Configuration import Configuration
from .TaskChecker import TaskChecker
from modules.Controller.ModuleController import ModuleController
from utilities.files.FileReader import ReadCSV

import questionary
import glob
import random

from questionary import Choice, Separator

from core.singletons.ProfileSingleton import ProfileSingletonMeta
from utilities import Logger, getTime, Colors, ReadFile, ProxySelectorTheme

class ProfilesManager(metaclass=ProfileSingletonMeta):

    def checkFields(self, fields, csvFields):
        missingFields = []

        for field in fields:
            if (field not in csvFields):
                missingFields.append(field)

        return (missingFields)

    def getProfilesFiles(self):

        if (self.directory is None):
            files = glob.glob(f"shops/{self.moduleName}/*.csv")
            
            for file in glob.glob(f"logs/{self.moduleName}/*.csv"):
                files.append(file)
        else:
            files = glob.glob(f"{self.directory}/*.csv")

        Choices = []
        InvalidChoices = []

        separatedLogs = False

        for file in files:

            content = ReadCSV(file)
            tasks = []
            headerStatus = None

            fields = self.subModule['fields']

            try:
                csvFields = list(content[0].keys())
                missingFields = self.checkFields(fields, csvFields)

                Logger.debug(f"fields={fields}")
                Logger.debug(f"csvFields={csvFields}")
                Logger.debug(f"diffs={missingFields}")
                
                if (len(missingFields) > 0):
                    headerStatus = "Missings fields: {}".format(", ".join(missingFields))

                if (headerStatus is None):
                    for task in content:
                        tasks.append(task)

                taskSize = len(tasks)

                if (headerStatus == None and taskSize > 0):
                    if (file.startswith("logs") and separatedLogs is False):
                        Choices.append(Separator("       -------- Logs ----------"))
                        separatedLogs = True
                        
                if (headerStatus == None and taskSize > 0):
                    Choices.append(Choice(
                        title=[
                            ("class:purple", '{message: <16}'.format(message=file.split("\\")[-1])),
                            ("class:text", " ["),
                            ("class:blue", '{message} tasks'.format(message=taskSize)),
                            ("class:text", "]")
                        ],
                        value={
                            "name": file.split("\\")[-1],
                            "size": taskSize,
                            "content": tasks
                        }
                    ))
                else:
                    InvalidChoices.append(Choice(
                        title=[
                            ("class:purple", '{message: <14}'.format(message=file.split("\\")[-1])),
                            ("class:text", " ["),
                            ("class:red", '{message}'.format(message=headerStatus)),
                            ("class:text", "]")
                        ],
                        value={
                            "name": file.split("\\")[-1],
                            "size": taskSize,
                            "error": headerStatus
                        },
                        disabled="Invalid"
                    ))

            except IndexError:
                Logger.error(f"[Profiles] Empty profiles! ")
                InvalidChoices.append(Choice(
                    title=[
                        ("class:purple", '{message: <14}'.format(message=file.split("\\")[-1])),
                        ("class:text", " ["),
                        ("class:red", '{message}'.format(message="0 tasks")),
                        ("class:text", "]")
                    ],
                    value={
                        "name": file.split("\\")[-1],
                        "error": "Empty profiles"
                    },
                    disabled="Empty Profiles"
                ))

        if (len(InvalidChoices) > 0):
            Choices.append(Separator("       ------- Invalid -------"))
        return (Choices + InvalidChoices)

    def loadProfiles(self):
        ProfileAreLoaded = None

        while ProfileAreLoaded == None:
            Logger.debug("[Profiles] Loading Profiles Files...")
            profilesFiles = self.getProfilesFiles()
            Logger.debug("[Profiles] Successfully loaded Profiles Files")

            if (len(profilesFiles) > 0):
                try:
                    answers = questionary.select(
                        "Which profiles file you want to use?",
                        choices=profilesFiles,
                    ).ask()

                    ProfileAreLoaded = True
                except AttributeError:
                    Logger.error("[Profiles] None of your profiles are correct")

                    for profileFile in profilesFiles:
                        try:
                            Logger.error(f"Profile: [{profileFile.value['name']}] is invalid! Error: [{profileFile.value['error']}]")
                        except Exception:
                            pass
                        
                    if (not questionary.confirm(f"[Profiles] Are you sure that at least one of your profiles is correct?").ask()):
                        ProfileAreLoaded = False
            else:
                if (not questionary.confirm(f"[Profiles] Can't find any profiles in the directory! Have you added at least one of your profiles?").ask()):
                    ProfileAreLoaded = False

        if (ProfileAreLoaded == False or ProfileAreLoaded == None):
            self.profiles = None
            return (False)

        if (answers is None):
            return (None)

        Logger.info("[Profiles] Loading Profiles...")
        self.profiles = TaskChecker(answers["content"], checkTasks=self.checkTasks).getTasks()
        self.profileName = answers["name"].replace(".csv", "")

        shuffleState = "Same"
        if (Configuration().getUserSettings()['ShuffleTasks'] is True):
            shuffleState = "Shuffle"
            random.shuffle(self.profiles)
            
        Logger.success(f"[Profiles] Successfully loaded {len(self.profiles)}/{len(answers['content'])} tasks! [Order={shuffleState}]")
        return True

    def __init__(self, moduleName, subModuleName, directory=None, checkTasks=True) -> None:
        self.moduleName = moduleName
        self.subModuleName = subModuleName
        self.directory = directory

        self.module = ModuleController().getModule(moduleName)
        self.subModule = ModuleController().getSubModule(self.module, subModuleName)
        self.profiles = []
        self.checkTasks = checkTasks

    def getProfiles(self):
        return self.profiles

    def getProfileName(self):
        return self.profileName
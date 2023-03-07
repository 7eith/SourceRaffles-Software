"""********************************************************************"""
"""                                                                    """
"""   [EnterForm] EnterForm.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 22/09/2021 18:04:46                                     """
"""   Updated: 04/11/2021 12:13:49                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
import os
from services.notifier.Discord.GoogleFormNotifier import NotifyEndFillGoogleForm, NotifyEnteredGoogleForm 

from services.notifier.Discord.EnterRaffleNotifier import NotifyEndRaffleEntries, NotifyEnteredAccount
from core.configuration.Configuration import Configuration
import requests

from .EnterFormTask import EnterFormTask

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger

import json

class EnterForm:
    
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyEnteredGoogleForm(self.module, task, self.configuration)

    def PromptForm(self):
        
        dirs = os.listdir("shops/GoogleForm/")

        Choices = []
        for file in dirs:
            Choices.append(
                questionary.Choice(
                    title=[("class:purple", file)], value={"fileName": file}
                )
            )

        Choices.append(
            questionary.Choice(title=[("class:red", "Exit")], value={"slug": "Exit"})
        )

        answer = questionary.select(
            "Which form do you want to enter?",
            choices=Choices,
        ).ask()

        if "slug" in answer:
            return None
        else:
            return answer['fileName']

    def readConfiguration(self):

        configurationFile = open(f"shops/GoogleForm/{self.formDirectory}/configuration.json", "r", encoding="utf-8", newline="")
        configuration = json.load(configurationFile)
        configurationFile.close()

        return (configuration)

    def getFieldbyName(self, name):

        for page in self.configuration['pages']:
            
            for field in page:
                if (field['name'] == name):
                    return (field)
        
        return (None)

    def __init__(self) -> None:
        self.moduleName = "GoogleForm"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "EnterForm"

        self.formDirectory = self.PromptForm()

        if self.formDirectory is None:
            return

        """ Load Profiles & Proxy """
        ProfilesManager(self.moduleName, self.subModuleName, directory=f"shops/GoogleForm/{self.formDirectory}").loadProfiles()
        self.Profiles = ProfilesManager().getProfiles()

        if self.Profiles is None:
            return

        ProfileName = ProfilesManager().getProfileName()
        profilesNumber = len(self.Profiles)

        """
            Form Configuration
        """

        self.configuration = self.readConfiguration()

        if (self.configuration is None):
            return 

        """ UI Utilities """
        DiscordRPC().updateRPC("Running {}".format(self.moduleName))
        setTitle("SourceRaffles [{}] | {}".format(self.moduleName, self.subModuleName))

        """ Logger """
        now = datetime.now()
        self.date = "{:02d}_{:02d}_{:02d}-{:02d}-{:02d}".format(
            now.day, now.month, now.hour, now.minute, now.second
        )
        self.loggerFileName = (
            f"logs/{self.moduleName}/{self.configuration['title']}-{self.date}.csv"
        )
        self.TaskLogger = TaskLogger(self.loggerFileName)
        loggerStatus = self.TaskLogger.createLogger(self.Profiles)

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

        self.checkTasks()

        tasks = []
        successTask: int = 0
        failedTask: int = 0
        runningLoop = True

        while runningLoop:
            if self.threads > 1:
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    for index, profile in enumerate(self.Profiles):

                        if (
                            profile["status"] == "PENDING"
                            or profile["status"] == "FAILED"
                        ):
                            tasks.append(
                                executor.submit(
                                    EnterFormTask,
                                    index,
                                    profilesNumber,
                                    profile,
                                    self.configuration,
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
                            f"SourceRaffles - [GoogleForm] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )
            else:
                printSeparator()
                for index, profile in enumerate(self.Profiles):

                    if profile["status"] == "PENDING" or profile["status"] == "FAILED":
                        TaskResult = EnterFormTask(
                            index, profilesNumber, profile, self.configuration
                        )

                        if TaskResult.success:
                            successTask += 1
                        else:
                            failedTask += 1

                        self.endedTask(TaskResult)

                        remaining = profilesNumber - (failedTask + successTask + 1)
                        setTitle(
                            f"SourceRaffles - [Google Form] | Success: {str(successTask)} - Failed {str(failedTask)} - Remaining {str(remaining)}"
                        )

                        printSeparator()
                        print("")
                        waitUntil(random.randint(self.minDelay, self.maxDelay))
                        print("")

            NotifyEndFillGoogleForm(
                self.module,
                profilesNumber,
                failedTask,
                successTask,
                self.loggerFileName,
                self.configuration
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

    def checkTasks(self):

        for index, profile in enumerate(self.Profiles):
            for key, value in profile.items():
                if (key != "email" and key != "status"):
                    field = self.getFieldbyName(key)

                    if (value == "!! REQUIRED !!"):
                        profile['status'] = "INVALID"
                        self.logErrorTask(profile, f"Task got a required field without value!")

                    if (field['type'] == "DROPDOWN"):
                        if (value == "#RANDOM#"):
                            profile[key] = random.choice(field['choices'])
                        else:
                            if (value not in field['choices']):
                                profile['status'] = "INVALID"
                                self.logErrorTask(profile, f"Invalid choices! ({key})")

                    if (field['type'] == "CHECKBOX" or field['type'] == "MULTIPLE_CHOICE"):
                        if (value == "#RANDOM#"):
                            profile[key] = random.choices(field['choices'])
                        else:
                            choices = value.split("-")
                            
                            choicesSelected = []
                            for indexChoice in choices:

                                try:
                                    index = int(indexChoice) - 1
                                except ValueError:
                                    profile['status'] = "INVALID"
                                    self.logErrorTask(profile, f"Invalid choices! ({key} - Not an integer)")

                                if (index < 0):
                                    profile['status'] = "INVALID"
                                    self.logErrorTask(profile, f"Invalid choices! ({key} - Invalid Index)") 
                                else:
                                    try:
                                        choicesSelected.append(field['choices'][index])
                                    except IndexError:
                                        profile['status'] = "INVALID"
                                        self.logErrorTask(profile, f"Invalid choices! ({key} - Invalid Index)")
                                        
                            profile[key] = choicesSelected

    def logErrorTask(self, profile, error):

        if ("email" in profile):
            Logger.error(f"[{profile['email']}] Invalid Task: {error}")
        else:
            Logger.error(f"[???] Invalid Task, check logs.csv to know failed task! {error}")

        for key, value in profile.items():
            if (type(value) == list):
                profile[key] = "-".join(value)
                
        self.TaskLogger.logProfile(profile)

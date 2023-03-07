"""********************************************************************"""
"""                                                                    """
"""   [configuration] Configuration.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 11/10/2021 19:39:05                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import json
import sys
import questionary

from services.initializator import Initializator

from json.decoder import JSONDecodeError

from core.singletons.ConfigurationSingleton import ConfigurationSingletonMeta
from utilities import Logger, waitUntil

class Configuration(metaclass=ConfigurationSingletonMeta):

    defaultConfiguration = {
        "LicenseKey": "SOURCE-XXXX-XXXX-XXXX",
        "WebhookURL": "DISCORD_WEBHOOK_URL",
        "ProxyLess": False,
        "CaptchaServices": {
            "Favorite": "2Captcha",
            "2Captcha": ["KEY", "KEY"],
            "CapMonster": ["KEY", "KEY"]
        },
        "UserSettings": {
            "DiscordPresence": True,
            "NotifyEachTask": True,
            "NotifyFailedTask": True,
            "ShuffleTasks": True
        }
    }

    def __init__(self) -> None:
        self.configuration = None

        if (self.configuration is None):
            Logger.info("[Configuration] Loading Configuration...")
            self.loadConfiguration()
            self.checkConfiguration()
            Logger.success("[Configuration] Successfully loaded Configuration!")

    def loadConfiguration(self):

        try: 

            configurationFile = open("configuration.json", "r", encoding="utf-8", newline="")
            self.configuration = json.load(configurationFile)
            configurationFile.close()

        except FileNotFoundError:
            
            try:
                Initializator()
            except Exception:
                pass
            
            Logger.info("Configuration file not found, creating new one!")

            with open("configuration.json", "w") as SettingsFile:
                SettingsFile.write(json.dumps(self.defaultConfiguration, indent=4))

            self.configuration = self.defaultConfiguration

        except JSONDecodeError as error:
            Logger.error("[Configuration] JsonDecodeError - Failed to read Configuration File!")

            configurationFile = open("configuration.json", "r", encoding="utf-8", newline="")
            lines = configurationFile.readlines()
            ErrorLine = lines[error.lineno - 1].replace("    ", "")[:-2]
            configurationFile.close()

            Logger.error(f"[Configuration] Line #{error.lineno} is invalid: '{ErrorLine}' is not JSON!")

            if (questionary.confirm(f"[Configuration] Have you corrected your problem? ").ask()):
                self.loadConfiguration()
            else:
                questionary.print(f"> [Configuration] Invalid Configuration file! Exiting in 5s", style="bold italic fg:darkred")
                waitUntil(5)
                sys.exit(1)
                
    def checkConfiguration(self):
        Logger.debug("[Configuration] Checking Configuration...")

        error = False
        for key in self.defaultConfiguration:

            if key not in self.configuration:
                error = True
                Logger.error(f"[Configuration] '{key}' is missing in Configuration!")

        # check user settings
        for key in self.defaultConfiguration['UserSettings']:

            if key not in self.configuration['UserSettings']:
                error = True
                Logger.error(f"[Configuration] '{key}' is missing in Configuration / UserSettings!")

        if (error):
            if (questionary.confirm(f"[Configuration] Have you corrected your problem? ").ask()):
                self.loadConfiguration()
                self.checkConfiguration()
            else:
                questionary.print(f"> [Configuration] Invalid Configuration file! Exiting in 5s", style="bold italic fg:darkred")
                waitUntil(5)
                sys.exit(1)

        favoriteCaptchaHandler = self.configuration['CaptchaServices']['Favorite']
            
        if (favoriteCaptchaHandler not in ["2Captcha", "CapMonster"]):
            Logger.error(f"[Configuration] Unsupported Captcha Provider! We only support 2Captcha or CapMonster")

            if (questionary.confirm(f"[Configuration] Have you corrected your problem? ").ask()):
                self.loadConfiguration()
                self.checkConfiguration()

        for index, key in enumerate(self.configuration['CaptchaServices'][favoriteCaptchaHandler]):

            if (key == "KEY"):
                self.configuration['CaptchaServices'][favoriteCaptchaHandler].pop(index)

        if (len(self.configuration['CaptchaServices'][favoriteCaptchaHandler]) == 0):
            if (questionary.confirm(f"[Configuration] You need to have setup a Captcha Handler Key for {favoriteCaptchaHandler}, confirm when its done").ask()):
                self.loadConfiguration()
                self.checkConfiguration()
        else:
            self.saveConfiguration()
            
    def saveConfiguration(self):
        Logger.debug("Saving Configuration to configuration File...")

        configurationFile = open("configuration.json", "w", encoding="utf-8", newline="")
        configurationFile.write(json.dumps(self.configuration, indent=4))
        configurationFile.close()

        Logger.debug("Successfully saved configuration file!")

    """ 
        @Getters / @Setters
    """

    def getConfiguration(self):
        return self.configuration

    def getUserSettings(self):
        return self.configuration['UserSettings']

    def updateConfiguration(self, key, value):
        self.configuration[key] = value
        self.saveConfiguration()

    def setLicenseKey(self, licenseKey):
        self.updateConfiguration("LicenseKey", licenseKey)
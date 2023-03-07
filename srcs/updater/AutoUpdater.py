"""********************************************************************"""
import platform

"""                                                                    """
"""   [updater] AutoUpdater.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 09/11/2021 22:14:29                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import os
import sys
import requests
import time
import sys
import hashlib

from utilities import Logger, getVersion, waitUntil

class AutoUpdater():

    def __deleteTempFiles(self):
        Logger.debug("Looking for temporary files to remove...")

        tempFiles = [file for file in os.listdir() if file.endswith(".tmp")]

        if (len(tempFiles) > 0):
            for file in tempFiles:
                try:
                    Logger.debug(f"Removing {file}...")
                    os.remove(file)
                    Logger.debug(f"Removed {file}!")
                except Exception as error:
                    Logger.debug(f"Error when removing old files from updates.. {error}")
        else:
            Logger.debug("No temporary files founded.")

    def doUpdate(self, updaterResponse):

        Logger.info(f"An update was found!")

        Logger.debug(f"Renaming {self.executableName} to SourceRaffles.exe.tmp!")
        os.rename(self.executableName, ".SourceRaffles.exe.tmp")
        Logger.debug(f"Renamed {self.executableName} to SourceRaffles.exe.tmp!")
        
        Logger.info(f"Downloading SourceRaffles {updaterResponse['version']}")
        response = requests.get("https://sourceraffles.s3.eu-west-3.amazonaws.com/CLI/SourceRaffles.exe", allow_redirects=True)
        open(self.executableName, 'wb').write(response.content)
        Logger.success(f"Successfully downloaded new version! Launching Source Raffles {updaterResponse['version']}")
        os.system(self.executableName)
        sys.exit(0)

    def checkInjectedPacket(self, versionChecksum):
        sha256_hash = hashlib.sha256()
        with open(self.executableName, "rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            self.shaHash = sha256_hash.hexdigest()

            if (versionChecksum != sha256_hash.hexdigest()):
                Logger.error("Error#0007 - Incident will be reported! Exiting CLI!")
                waitUntil(5)
                sys.exit(0)

    def __init__(self) -> None:

        if "darwin" in platform.system().lower():
            Logger.debug("Mac detected, not updating the bot")

        else:

            Logger.debug("Windows detected, launching autoupdate procedure")

            self.executableName = sys.argv[0].split("\\")[-1]

            if (self.executableName == "srcs"):
                Logger.info("[Debug] Launch mode: DEBUG - Developper")
                return

            self.__deleteTempFiles()

            Logger.info("Checking for updates...")

            try:
                updaterResponse = requests.get("https://sourceraffles.s3.eu-west-3.amazonaws.com/CLI/version.json").json()
            except Exception as error:
                Logger.error(f"Error when checking for updates! {error}")

            if ("updater.sr" in os.listdir()):
                Logger.warning("[AutoUpdater] AutoUpdate disabled! Launching current version")
                return

            if (updaterResponse['version'] != getVersion()):
                try:
                    self.doUpdate(updaterResponse)
                except Exception as error:
                    Logger.error("An exception has occured when trying to do update...")
                    Logger.error(error)
                    time.sleep(15)
                    sys.exit(0)
            else:
                Logger.info("No updates available! Launching SourceRaffles!")
                # self.checkInjectedPacket(updaterResponse['uuid'])
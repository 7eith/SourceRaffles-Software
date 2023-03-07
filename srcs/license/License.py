"""********************************************************************"""
"""                                                                    """
"""   [license] License.py                                             """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 08/11/2021 10:49:06                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import os
import requests
import sys
import hashlib
import jwt

from utilities import *
from user import *
from core.configuration import *

JWT_KEY = "767dabacf45240009997b39630da61ea9f23f4318a1145729ba71f066b4e86ef"

class License():

    def askLicense(self):

        try:
            key = input(Logger.formatForInput('[License] Enter your license key here: '))
            Configuration().setLicenseKey(key)

        except KeyboardInterrupt:
            Logger.info("Exiting CLI!")
            waitUntil(5)
            exit(0)

    def getMachineId(self, computerUser, computerName, processorName):
        m = hashlib.sha256()
        m.update(computerUser.encode('utf-8'))
        m.update(computerName.encode('utf-8'))
        m.update(processorName.encode('utf-8'))
        m.digest()

        return m.hexdigest()

    def __init__(self) -> None:

        Logger.info("[License] Checking License...")

        if (Configuration().getConfiguration()['LicenseKey'] == "SOURCE-XXXX-XXXX-XXXX" or Configuration().getConfiguration()['LicenseKey'] == ""):
            self.askLicense()

        if "darwin" not in platform.system().lower():
            try:
                computerUser = os.environ['USERNAME']
            except KeyError:
                computerUser = "Unkown"

            computerName = "os.environ['COMPUTERNAME']"
            processorName = "os.environ['PROCESSOR_IDENTIFIER']"
            machineId = self.getMachineId(computerUser, computerName, processorName)
        else:
            computerUser = os.environ['USER']
            computerName = os.environ['USER']
            processorName = os.environ['USER']
            machineId = self.getMachineId(computerUser, computerName, processorName)

        try:
            response = requests.post(
                f"{getAPI()}/license/authenticate",
                data={
                    "key": Configuration().getConfiguration()['LicenseKey'],
                    "machineId": machineId,
                    "computerName": computerName,
                    "computerUser": computerUser,
                    "processorName": processorName,
                    "cliVersion": getVersion()
                }
            )

            data = response.json()

            if (data['status'] is False):
                Logger.error(f"[License] {data['error']}")
                input("")
                sys.exit()
                
            decoded = jwt.decode(data['token'], JWT_KEY, algorithms=["HS256"])

            if (response.status_code == 200):
                Logger.success(f"[License] Successfully Authentificated! Welcome back {decoded['username']}#{decoded['discriminator']}!")
                User(decoded, data['token'])

            elif (response.status_code == 404):
                Logger.error("[License] Invalid License Key!")
                input("")
                sys.exit()

            else:
                Logger.error(f"[License] Error while authentificating... {data['error']}")
                input("")
                sys.exit()

        except Exception as error:
            Logger.error(f"[License] Error while authentificating. If you think is a mistake open a ticket!")
            Logger.debug(str(error))
            input("")
            sys.exit()
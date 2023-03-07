"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 10/09/2021 05:43:30                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from core.configuration.Configuration import Configuration
import requests

from services.captcha import CaptchaHandler
from utilities import *

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile, raffle) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile
        self.raffle: dict = raffle

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.captchaToken: str = None
        self.proxyLess = False

        """ Utilities """
        self.profile["Product"] = raffle["product"]
        self.initSession()

        try:

            status = self.executeTask()

            if (status == 1):
                self.success = True
                self.profile["status"] = "SUCCESS"
                Logger.success(f"{self.logIdentifier} Successfully entered raffle!")
            else:
                self.success = False
                self.profile['status'] = "FAILED"
                
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def getCaptcha(self):
        self.retryCaptcha = 0
        Logger.log(f"{self.logIdentifier} Solving Captcha...")

        captcha = CaptchaHandler().handleRecaptcha(
            '6LeSbUEaAAAAAF4woKyngoqrs7K7Y2rs_-Zk_Krm',
            self.raffle["link"],
            pollingInterval=3
        )

        if captcha["success"]:
            Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            return captcha["code"]
        else:
            self.retryCaptcha += 1
            Logger.warning(
                f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)"
            )
            Logger.error(f"{self.logIdentifier} {captcha['error']}")

            if self.retryCaptcha <= 3:
                return self.getCaptcha()
            else:
                return None

    def executeTask(self):

        try:

            Logger.info("Getting captcha token")
            self.captcha = self.getCaptcha()
            if self.captcha is None:
                Logger.error("Error while getting captcha")
                return -1

            headers = {
                'Referer': 'https://rezetstore.dk/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                'Content-Type': 'application/json',
            }

            data = {
                "captcha": self.captcha,
                "email": self.profile["email"],
                "sdk": self.raffle["metadata"]["sdk"],
                "sku": self.profile["sku"],
                "size": self.profile["size"],
                "phone": self.profile["phone_number"],
                "country": self.profile["country_code"]
            }

            Logger.info("Submitting entry")
            r = requests.post('https://master-7rqtwti-2sungu3anaqlq.eu-4.platformsh.site/api/en/wr/register',
                              headers=headers,
                              json=data)

            if r.status_code == 200:
                return 1
            else:
                Logger.error("Error while submitting entry : {}".format(r.status_code))
                return 0

        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1



import requests


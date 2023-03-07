"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 17/09/2021 11:27:59                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import *
from core.configuration.Configuration import Configuration
from services.captcha import CaptchaHandler
import random

class EnterRaffleTask:

    def initSession(self):
        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
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
        self.productId = raffle["metadata"]["productId"]
            
        self.userAgent = getRandomUserAgent()
        self.initSession()

        try:
            
            status = self.submit()

            if status == 1:

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

        captcha = CaptchaHandler().handleHCaptcha(
            'c79f2f54-731d-4abb-b6db-13748c75cdc2',
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

    def submit(self):

        headers = {
            'authority': 'www.keller-x.de',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
        }

        try:
            response = self.session.get(self.raffle["link"],
                                        headers=headers)
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting main page : {}".format(str(e)))
            return -1
        if response.status_code == 200:
            Logger.info("Accessed main page")
        else:
            Logger.error("Error while getting main page : {}".format(response.status_code))
            return -1

        headers = {
            'authority': 'www.keller-x.de',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': 'application/json, text/plain, */*',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-gpc': '1',
            'origin': 'https://www.keller-x.de',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.keller-x.de/raffle/{}'.format(self.raffle["metadata"]["slug"]),
            'accept-language': 'en-US,en;q=0.9',
        }

        list_size = ['EU 35,5 - US 5', 'EU 36 - US 5,5', 'EU 36,5 - US 6',
                     'EU 37,5 - US 6,5', 'EU 38 - US 7',
                     'EU 38,5 - US 7,5', 'EU 39 - US 8',
                     'EU 40 - US 8,5', 'EU 40,5 - US 9', 'EU 41 - US 9,5',
                     'EU 42 - US 10', 'EU 42,5 - US 10,5',
                     'EU 43 - US 11', 'EU 44 - US 11,5', 'EU 44,5 - US 12']

        if self.size == "random":
            self.size = random.choice(list_size)

        number = list_size.index(self.size)
        if number < 10:
            number = "0{}".format(number)
        self.weirdId = self.raffle["metadata"]["weirdId"]
        self.optionId = "{}{}".format(self.weirdId, number)

        data = {
            'instagram': self.profile["instagram"],
            'email': self.profile["email"],
            'size': self.profile["size"],
            'terms': 'true',
            'subscription': 'true',
            'country': self.profile["country_code"],
            'token': self.getCaptcha(),
            'optionId': self.optionId,
            'slug': self.raffle["metadata"]["slug"]
        }

        try:
            response = self.session.post('https://www.keller-x.de/raffle/', headers=headers, data=data)
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1
        if response.status_code == 200:
            return 1
        else:
            Logger.error("Error while submitting entry : {}".format(response.status_code))
            return -1
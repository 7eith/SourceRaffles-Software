"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 17/09/2021 05:04:10                                     """
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

        if self.proxyLess == False:
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
        self.proxyLess = Configuration().getConfiguration()["ProxyLess"]

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

    def executeTask(self):

        if self.captchaToken == None:
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8',
                self.raffle["metadata"]["entryURL"],
                pollingInterval=3
            )

            if captcha["success"]:
                self.captchaToken = captcha["code"]
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1

                Logger.warning(
                    f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)"
                )
                Logger.error(f"{self.logIdentifier} {captcha['error']}")

                if self.retry <= 3:
                    return self.executeTask()
                else:
                    return (-1)

        Logger.log(f"{self.logIdentifier} Bypassing CloudFlare...")
        Logger.log(f"{self.logIdentifier} CloudFlare bypassed! ")

        headers = {
            'authority': 'app.rule.io',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://www.woodwood.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': getRandomUserAgent(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.woodwood.com/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'dnt': '1',
        }

        data = {
            'tags[]': self.raffle["metadata"]['tags'],
            'token': self.raffle["metadata"]['token'],
            'rule_email': self.profile["email"],
            'fields[Raffle.Phone Number]': self.profile["phone"],
            'fields[Raffle.First Name]': self.profile["first_name"],
            'fields[Raffle.Last Name]': self.profile["last_name"],
            'fields[Raffle.Shipping Address]': f"{self.profile['house_number']} {self.profile['street']}",
            'fields[Raffle.Postal Code]': self.profile["zip"],
            'fields[Raffle.City]': self.profile["city"],
            'fields[Raffle.Country]': self.profile["country_code"],
            'fields[SignupSource.ip]': 'undefined',
            'fields[SignupSource.useragent]': 'undefined',
            'language': 'sv',
            'g-recaptcha-response': self.captchaToken
        }

        # TODO: Color 
        # if self.profile["color"] != "":
        #     data["fields[Raffle.Collect]"] = self.profile["color"]

        try:
            response = self.session.post(
                'https://app.rule.io/subscriber-form/subscriber',
                headers=headers,
                data=data,
                allow_redirects=False
            )

            if (response.status_code == 302 and response.headers['Location'] == "https://www.woodwood.com/en/raffle-confirm-email"):
                return (1)
            else:
                return (0)

        except (requests.ConnectionError, requests.exceptions.ProxyError) as error:
            Logger.debug(f"{self.logIdentifier} Error while submitting entry.. {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ProxyError while submitting entry! Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.executeTask()
            else:
                return (-1)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while submitting entry.. {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ProxyError while submitting entry! Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.executeTask()
            else:
                return (-1)

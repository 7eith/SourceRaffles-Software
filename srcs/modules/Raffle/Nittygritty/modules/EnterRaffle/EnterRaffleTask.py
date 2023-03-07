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

    def executeTask(self):

        Logger.info('Submitting Raffle Entry')
        headers = {
            'authority': 'app.rule.io',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'origin': 'https://nittygrittystore.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://nittygrittystore.com/',
        }

        data = {
            'tags[]': self.raffle["ProductId"],
            'token': self.raffle["Token"],
            'rule_email': self.task["Email"],
            'fields[Raffle.First Name]': self.task["FirstName"],
            'fields[Raffle.Last Name]': self.task["LastName"],
            'fields[Raffle.Shipping Address]': self.task["Address"],
            'fields[Raffle.Postal Code]': self.task["PostalCode"],
            'fields[Raffle.City]': self.task["City"],
            'fields[Raffle.Phone Number]': self.task["PhoneNumber"],
            'fields[Raffle.Country]': self.task["CountryCode"],
            'fields[raffle.size-dh0952]': 'US {}'.format(self.task["Size"]),  ## us sizing
            'fields[SignupSource.ip]': '192.0.0.1',
            'fields[SignupSource.useragent]': 'Mozilla',
            'language': 'sv'
        }

        try:
            r = self.session.post('https://app.rule.io/subscriber-form/subscriber', headers=headers,
                                  data=data, allow_redirects=False)
            if r.status_code == 302:
                Logger.success("Successful entry !")
                return 1
            else:
                Logger.error(f"Error while submitting ! Rotating proxy... ({self.retry}/{self.maxRetry})")
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
                self.retry += 1
                if self.retry < self.maxRetry:
                    return self.executeTask()()
                else:
                    Logger.error("Too much retries, stopping task")
                    return -1
        except (requests.ConnectionError, requests.exceptions.ProxyError):
            Logger.error(f"ProxyError! Rotating proxy... ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.retry += 1
            if self.retry < self.maxRetry:
                return self.executeTask()()
            else:
                Logger.error("Too much retries, stopping task")
                return -1

        except Exception as error:
            Logger.error(f"Exception occurred (({self.retry}/{self.maxRetry})")
            Logger.error(f"Error : {error}")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.retry += 1
            if self.retry < self.maxRetry:
                return self.executeTask()()
            else:
                Logger.error("Too much retries, stopping task")
                return -1

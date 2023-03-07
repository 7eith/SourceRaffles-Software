"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 11/09/2021 17:29:56                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from utilities import *
from requests import ConnectionError
import json
from bs4 import BeautifulSoup
import random
from core.configuration.Configuration import Configuration
from services.captcha import CaptchaHandler


class AccountGeneratorTask():

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy)
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile

        """ Store """
        self.logIdentifier: str     = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state:         str     = "PENDING"
        self.success:       bool    = False
        self.retry:         int     = 0
        self.maxRetry:      int     = 10
        self.csrfToken:     str     = None
        self.captchaToken:  str     = None

        self.initSession()

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            
            self.executeTask()
            ProxyManager().banProxy(self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occurred when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def captcha(self):
        if self.captchaToken is None:
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6LemOsYUAAAAABGFj8B7eEvmFT1D1j8IbXJIdvNn',
                version="v3",
                url="https://juicestore.com/account",
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
                    return self.captcha()
                else:
                    return None

    def executeTask(self):
        
        Logger.log(f"{self.logIdentifier} Accessing main page...")
        
        status: int = self.createAccount()

        if (status == 1):
            self.retry = 0

            Logger.success(f"{self.logIdentifier} Successfully created account !")
            self.state = "SUCCESS"
            self.success = True

        else:
            self.state = "FAILED"
            self.success = False

    def createAccount(self):

        captcha = self.captcha()
        if captcha is None:
            Logger.error("Unvalid captcha token received, exiting")
            return -1

        headers = {
            'authority': 'juicestore.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'origin': 'https://juicestore.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://juicestore.com/account/register',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        data = {
            'form_type': 'create_customer',
            'utf8': '\u2713',
            'customer[first_name]': self.profile["first_name"],
            'customer[last_name]': self.profile["last_name"],
            'customer[email]': self.profile["email"],
            'customer[password]': self.profile["password"],
            'recaptcha-v3-token': captcha,
        }

        try:
            response = self.session.post('https://juicestore.com/account', headers=headers, data=data)
            if response.status_code == 200:
                return 1

        except Exception as e:
            Logger.error("Error while creating account : {}".format(str(e)))
            return -1
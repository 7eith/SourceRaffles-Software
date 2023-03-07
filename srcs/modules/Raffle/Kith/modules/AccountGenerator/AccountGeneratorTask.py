"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 05/09/2021 01:15:08                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import *
from requests.exceptions import ProxyError
from core.configuration.Configuration import Configuration
from bs4 import BeautifulSoup
from services.captcha import CaptchaHandler


class AccountGeneratorTask:
    
    def initSession(self):

        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile

        """ Store """
        self.logIdentifier:  str     = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
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
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def executeTask(self):
        
        status: int = self.createAccount()

        if status == 1:
            Logger.info(f"{self.logIdentifier} Successfully created account ! ")
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def captcha(self):
        if self.captchaToken == None:
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6LfbPnAUAAAAACqfb_YCtJi7RY0WkK-1T4b9cUO8',
                "https://eu.kith.com/account",
                invisible=1
            )

            if (captcha['success']):
                self.captchaToken = captcha['code']
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1

                Logger.warning(f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)")
                Logger.error(f"{self.logIdentifier} {captcha['error']}")

                if self.retry <= 3:
                    return self.captcha()
                else:
                    return -1

    def createAccount(self):
        Logger.info("Getting main page")

        headers = {
            'authority': 'eu.kith.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
        }
        try:
            self.session.get('https://eu.kith.com/account', headers=headers)
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
        except Exception as e:
            Logger.error("Error while creating the account (1) : {}".format(str(e)))

        headers = {
            'authority': 'eu.kith.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://eu.kith.com/account/login',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
        }

        try:
            self.session.get('https://eu.kith.com/account/register', headers=headers)
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while creating the account : {}".format(str(e)))
            return -1

        headers = {
            'authority': 'eu.kith.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'origin': 'https://eu.kith.com',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://eu.kith.com/account/register',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
        }

        data = {
            'form_type': 'create_customer',
            'utf8': '\u2713',
            'customer[first_name]': self.profile["first_name"],
            'customer[last_name]': self.profile["last_name"],
            'customer[email]': self.profile["email"],
            'customer[password]': self.profile["password"]
        }
        try:
            response = self.session.post('https://eu.kith.com/account', headers=headers, data=data)
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while creating the account (2) : {}".format(str(e)))
            return -1

        if "challenge" in response.url:
            challenge_html = response.text
            page_soup = BeautifulSoup(challenge_html, 'html.parser')
            token_new = page_soup.find("input", {"name": "authenticity_token"})["value"]

            headers = {
                'authority': 'eu.kith.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'upgrade-insecure-requests': '1',
                'origin': 'https://eu.kith.com',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-gpc': '1',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://eu.kith.com/challenge',
                'accept-language': 'en-US,en;q=0.9',
            }

            Logger.info("Challenge detected")

            captcha = self.captcha()

            if captcha is None or -1:
                Logger.error("Failed to get valid captcha token")
                return -1

            data = {
                'authenticity_token': token_new,
                'g-recaptcha-response': captcha
            }

            try:
                response = self.session.post('https://eu.kith.com/account', headers=headers, data=data)
            except ProxyError:
                Logger.error("Proxy Error, stopping task")
                return -1
            except Exception as e:
                Logger.error("Error while creating the account (3) : {}".format(str(e)))
                return -1
            if response.status_code == 200:
                return 1
            else:
                Logger.error("Error while creating account : {}".format(response.json()))
                return -1
        else:
            return 1
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

    def executeTask(self):
        
        Logger.log(f"{self.logIdentifier} Accessing main page...")
        
        accessMainPage: int = self.accessMainPage()

        if (accessMainPage == 1):
            self.retry = 0

            Logger.success(f"{self.logIdentifier} Successfully accessed main page !")

            createAccount: int = self.createAccount()

            if createAccount == 1:

                Logger.success(f"{self.logIdentifier} Account created !")
                
                self.state = "SUCCESS"
                self.success = True

            else:
                Logger.error(f"{self.logIdentifier} MaxRetryExceeded: Failed to create account")
                
                self.state = "FAILED"
                self.success = False
        else:
            self.state = "FAILED"
            self.success = False

    def accessMainPage(self):
        """
            - Step [1]
                - Accessing main page to get the CSRF token

            - Params: None

            - Returns
                - 1 : Successfully accessed main page
                - 0 : Failed to access main page
        """

        headers = {
            'authority': 'shop.footshop.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.footshop.com/',
        }

        try:
            r = self.session.get('https://shop.footshop.com/en/profile/login', headers=headers)
        except (requests.ConnectionError, requests.exceptions.ProxyError) as err:
            Logger.error(f"{self.logIdentifier} Error while getting main page! Rotating proxy and session... ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.retry += 1
            if self.retry < self.maxRetry:
                self.accessMainPage()
                return
            else:
                Logger.error(f"{self.logIdentifier} Too many retries, stopping task")
                return 0

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception occurred (({self.retry}/{self.maxRetry})")
            Logger.debug(f"{self.logIdentifier} Error : {error}")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            if self.retry < self.maxRetry:
                self.accessMainPage()
                return
            else:
                Logger.error(f"{self.logIdentifier} Too many retries, stopping task")
                return 0

        if r.status_code != 200:
            Logger.error(f"{self.logIdentifier}Access denied to main page")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            if self.retry < self.maxRetry:
                self.accessMainPage()
                return
            else:
                Logger.error(f"{self.logIdentifier} Too many retries, stopping task")
                return 0

        soup = BeautifulSoup(r.text, "html.parser")
        t = json.loads(soup.find('div', {'id': 'authentication'})["data-json"])
        self.csrf = t["registration"]["defaultValue"]["_csrf_token"]
        return 1

    def createAccount(self):
        """
                    - Step [2]
                        - Creating account

                    - Params: None

                    - Returns
                        - 1 : Successfully created account
                        - 0 : Failed to create account
                """

        headers = {
            'authority': 'shop.footshop.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.footshop.com/',
        }

        data = {
            "registration": {
                "email": self.profile["email"],
                "password": self.profile["password"],
                "profile": {
                    "name": {
                        "firstName": self.profile["first_name"],
                        "lastName": self.profile["last_name"]
                    },
                    "birth": {
                        "day": str(random.randint(1, 28)),
                        "month": str(random.randint(1, 12)),
                        "year": str(random.randint(1980, 2001))
                    },
                    "_csrf_token": self.csrf
                },
                "consent": {
                    "privacy-policy-101": True
                },
                "_csrf_token": self.csrf
            }
        }
        
        Logger.log(f"{self.logIdentifier} Creating account")
        try:
            r = self.session.post('https://shop.footshop.com/en/profile/register', headers=headers, json=data)
        except (requests.ConnectionError, requests.exceptions.ProxyError) as err:
            Logger.error(f"{self.logIdentifier} Error while getting main page! Rotating proxy and session... ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            if self.retry < self.maxRetry:
                self.createAccount()
                return
            else:
                Logger.error(f"{self.logIdentifier} Too many retries, stopping task")
                return 0

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception occurred (({self.retry}/{self.maxRetry})")
            Logger.error(f"{self.logIdentifier} Error : {error}")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            if self.retry < self.maxRetry:
                self.createAccount()
                return
            else:
                Logger.error(f"{self.logIdentifier} Too many retries, stopping task")
                return 0

        if r.status_code in [200, 230]:
            return 1

        else:
            Logger.error(f"{self.logIdentifier} Error while creating account")
            Logger.debug(f"{self.logIdentifier} Response received from footshop while creating account : {r.status_code} / {r.text}")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            if self.retry < self.maxRetry:
                self.createAccount()
                return
            else:
                Logger.error(f"{self.logIdentifier}Too many retries, stopping task")
                return 0

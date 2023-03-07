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

        self.scraper, self.proxy = CreateCFSession()

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
            self.proxy = ProxyManager().rotateProxy(self.scraper, self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def executeTask(self):
        
        status: int = self.createAccount()

        if status == 1:
            Logger.success(f"{self.logIdentifier} Successfully created account ! ")
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def createAccount(self):
        Logger.info("Getting main page")

        Logger.info("Solving Cloudflare challenge...")
        try:
            r = self.scraper.get("https://stress95.com/en/auth/view")
            csrf = self.scraper.cookies.get_dict().get("AntiCsrfToken")
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while solving CloudFlare : {}".format(str(e)))
            return -1

        Logger.info("Cloudflare challenge solved")

        data = {
            '_AntiCsrfToken': csrf,
            'firstName': self.profile["first_name"],
            'email': self.profile["email"],
            'password': self.profile["password"],
            'action': 'register'
        }

        Logger.info("Creating account...")
        try:

            r = self.scraper.post('https://stress95.com/en/auth/submit', data=data)
            if r.status_code == 200:
                json_rep = r.json()
                if json_rep["Response"]["Success"]:
                    return 1
                else:
                    Logger.error("Error while creating account : {}".format(str(json_rep)))
                    return -1
            else:
                Logger.error('Error while creating the account' + str(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while creating account : {}".format(str(e)))
            return -1
    
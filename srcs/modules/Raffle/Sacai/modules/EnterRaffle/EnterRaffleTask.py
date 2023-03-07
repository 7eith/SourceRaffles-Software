"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 22/11/2021 16:30:34                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from core.configuration.Configuration import Configuration
import cloudscraper
import random

from utilities import *

class EnterRaffleTask:

    def initSession(self):

        self.session = cloudscraper.create_scraper()

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

        self.SizeDict = random.choice(self.raffle['sizeRange'])
        
        """ Utilities """
        self.profile["Product"] = raffle["product"]
        self.profile["Size"] = self.SizeDict['name']
        
        self.initSession()

        Logger.log(f"{self.logIdentifier} Starting task for {self.profile['email']}")
        try:

            status = self.executeTask()

            if (status == SUCCESS):
                self.success = True
                self.profile["status"] = "SUCCESS"
            else:
                self.success = False
                if (self.profile['status'] == "PENDING"):
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

        sessionStatus = self.initializeSession()

        if (sessionStatus == SUCCESS):

            loginStatus = self.login()

            if (loginStatus == SUCCESS):
                Logger.info(f"{self.logIdentifier} Successfully logged-in!")

                enterStatus = self.enterRaffle()

                if (enterStatus == SUCCESS):
                    return SUCCESS
                else:
                    return FAILED
            elif (loginStatus == FAILED):
                self.profile['status'] = "INVALID_CREDENTIALS"
                return FAILED
            else:
                Logger.error(f"{self.logIdentifier} MaxRetryExceeded: Failed to login!")
                return FAILED
        else:
            Logger.error(f"{self.logIdentifier} MaxRetryExceeded: Failed to initialize Session!")
            return FAILED

    def initializeSession(self):

        try:
            response = self.session.get("https://store.sacai.jp/login")

            if (response.status_code == 200):
                self.csrfToken = re.search('fuel_csrf_token" value="(.+?)"', response.text).group(1)
                return (SUCCESS)
            else:
                raise ConnectionError("Failed to initialize session!")
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while initializating session... {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to initializating session... Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.initializeSession()
            else:
                return (EXCEPTION)
                
    def login(self):
        
        data = {
            'fuel_csrf_token': self.csrfToken,
            'back_url': self.raffle['url'],
            'login_id': self.profile['email'],
            'password': self.profile['password'],
            'check_preserve_login': '1',
            'preserve_login_flag': '1'
        }

        try:
            response = self.session.post('https://store.sacai.jp/login', data=data)
                
            if ("error-messages" in response.text):
                Logger.error(f"{self.logIdentifier} This account doesn't exist on Sacai! ")
                return (FAILED)

            if (response.status_code == 200):
                self.csrfToken = re.search('fuel_csrf_token" value="(.+?)"', response.text).group(1)
                return (SUCCESS)
            else:
                raise ConnectionError("Failed to login!")
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while login... {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to login. Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.login()
            else:
                return (EXCEPTION)

    def enterRaffle(self):
        data = {
            'goods_id': self.SizeDict['id'],
            'detail_disp_manage_code': self.raffle['metadata']['detailCode']
        }

        try:

            response = self.session.get(
                'https://store.sacai.jp/apis/csrf/token.json', 
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )

            htmlCSRF = response.json()['html']
            self.csrfToken = re.search('fuel_csrf_token" value="(.+?)"', htmlCSRF).group(1)
            
            data['fuel_csrf_token'] = self.csrfToken
            
            response = self.session.post(
                'https://store.sacai.jp/apis/apply/lottery/customer.json', 
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                },
                data=data
            )
            
            if (response.json()['is_success'] == True):
                Logger.success(f"{self.logIdentifier} Successfully entered raffle! ({self.SizeDict['name']})")
                return (SUCCESS)
            else:
                if (response.json()['errors'][0] == "Already applied for lottery."):

                    Logger.error(f"{self.logIdentifier} Already entered! ")
                    self.profile['status'] = "SUCCESS"
                    return (SUCCESS)
                    
                Logger.error(f"{self.logIdentifier} Error when entering! '{response.json()['errors'][0]}'")
                return FAILED
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while entering {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to enter. Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.enterRaffle()
            else:
                return (EXCEPTION)
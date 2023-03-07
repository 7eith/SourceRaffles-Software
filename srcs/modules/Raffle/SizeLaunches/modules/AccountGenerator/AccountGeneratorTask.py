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

from services.captcha import CaptchaHandler
from json.decoder import JSONDecodeError
from utilities import *
from requests import ConnectionError


class AccountGeneratorTask():

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

        """ Mesh Keys """
        self.apiKey = "0ce5f6f477676d95569067180bc4d46d"
        self.key = "GT0P5LZCT9364QEH2WVK3YVKT6P467S3"
        self.id = "e27d1ea0"

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            self.initSession()
            self.executeTask()
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def executeTask(self):

        createAccount = self.createAccount()

        if createAccount == 1:
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def getCaptcha(self):

        if (self.captchaToken == None):
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6LcHpaoUAAAAANZV81xLosUR8pDqGnpTWUZw59hN',
                "https://size-mosaic-webapp.jdmesh.co/",
                invisible=1,
                version="v3"
            )

            if (captcha['success']):
                self.captchaToken = captcha['code']
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1

                Logger.warning(f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)")
                Logger.error(f"{self.logIdentifier} {captcha['error']}")

                if (self.retry <= 3):
                    return self.createAccount()
                else:
                    return (-1)

    def createAccount(self):
        """
            - Step [3]
                - Create Account!

            - Params: None

            - Returns:
                - 1: Successfully registered!
                - 0: User not registered
                - -1: Failed to register MaxRetryExceeded
        """

        headers = {
            'Accept': '*/*',
            'Authorization': Headers,
            'originalhost': 'mosaic-platform.jdmesh.co',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://size-mosaic-webapp.jdmesh.co',
            'Connection': 'keep-alive',
            'User-Agent': 'SizeLaunch-2.4.1.0 iPhone',
            'Referer': 'https://size-mosaic-webapp.jdmesh.co/',
        }

        params = (
            ('api_key', '0ce5f6f477676d95569067180bc4d46d'),
            ('channel', 'iphone-mosaic'),
        )

        data = {
               "guestUser": False,
               "loggedIn": False,
               "firstName": self.profile["first_name"],
               "lastName": self.profile["last_name"],
               "password": self.profile["password"],
               "username": self.profile["email"],
               "verification": captcha,
        }

        Logger.info("Creating account...")
        try:
            response = self.session.post('https://mosaic-platform.jdmesh.co/stores/size/users/signup',
                                         headers=headers,
                                         params=params,
                                         data=data)

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from SizeLaunches [RegisterAccounts]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from SizeLaunches [RegisterAccounts]")

            if (response.status_code == 200):
                Logger.success("Account created !")

                return (1)
            else:
                return (0)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while registering User {str(error)}")

            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while registering User! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.createAccount()
            else:
                return (-1)

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

if "darwin" not in platform.system().lower():
    from helheim.exceptions import (
        HelheimException
    )

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
        
        Logger.log(f"{self.logIdentifier} Solving CloudFlare...")
        
        solveCloudFlareStatus: int = self.solveCloudflare()

        if (solveCloudFlareStatus == 1):
            self.retry = 0

            Logger.info(f"{self.logIdentifier} Successfully solved CloudFlare! ")

            createAccount = self.createAccount()

            if createAccount == 1:
                self.state = "SUCCESS"
                self.success = True
            else:
                self.state = "FAILED"
                self.success = False

        else:
            self.state = "FAILED"
            self.success = False


    def solveCloudflare(self):
        """
            - Step [1]
                - Solve CloudFlare
                - Check if 200 and got a CSRFToken

            - Params: None
            
            - Returns:
                - 1: Successfully Solved CloudFlare
                - 0: Failed to SolveCloudflare (MaxRetryExceeded)
        """
        
        self.session, self.proxy = CreateCFSession()
        
        try:
            response = self.session.get(
                "https://www.sneakersnstuff.com/"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from SNS [SolveCloudflare]")
            
            if (response.status_code == 200):
                self.csrfToken = self.session.cookies.get_dict().get("AntiCsrfToken")

                return (1)
            else:
                self.retry += 1
                Logger.warning(f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

                if (self.retry <= self.maxRetry):
                    return self.solveCloudflare()
                else:
                    return (0)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} Error while solving CloudFlare on SNS: {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on SNS: {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

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
        
        if (self.captchaToken == None):
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6LeKIW0UAAAAAA-ouoKHOnWuQDNymSwDFYeGP323',
                "https://www.sneakersnstuff.com/en/auth/view?op=register",
                invisible=1
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

        payload = {
            "_AntiCsrfToken": self.csrfToken,
            "firstName": self.profile["first_name"],
            "email": self.profile["email"],
            "password": self.profile["password"],
            "g-recaptcha-response": self.captchaToken,
            "action": "register"
        }

        Logger.info("Creating account...")
        try:
            response = self.session.post("https://www.sneakersnstuff.com/en/auth/submit", data=payload)

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from SNS [RegisterAccounts]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from SNS [RegisterAccounts]")

            if (response.status_code == 200):
                Logger.success("Account created !")

                return (1)
            else:
                return (0)

        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while registering User {str(error)}")

            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while registering User ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.createAccount()
            else:
                return (-1)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while registering User {str(error)}")

            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while registering User! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.createAccount()
            else:
                return (-1)
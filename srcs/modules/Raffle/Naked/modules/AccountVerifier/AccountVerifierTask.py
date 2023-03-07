"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 03/10/2021 09:22:55                                     """
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

class AccountVerifierTask():

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
                    
            loginStatus = self.login()

            if (loginStatus == 1):
                Logger.info(f"{self.logIdentifier} Successfully logged-in!")
                
                fetchProfileStatus = self.fetchProfile()

                if (fetchProfileStatus == 1):
                    
                    verifyStatus = self.verifyAccount()

                    if (verifyStatus == 1):
                        Logger.success(f"{self.logIdentifier} Successfully verified {self.profile['email']}! ")

                        self.state = "SUCCESS"
                        self.success = True

                    else:

                        Logger.error(f"{self.logIdentifier} Failed to verify Account!")
                        self.state = "FAILED"
                        self.success = False

                elif (fetchProfileStatus == -2):
                    Logger.warning(f"{self.logIdentifier} This account doesn't need to be verified! Skipping Tasks")

                    self.state = "SUCCESS"
                    self.success = True
                else:

                    self.state = "FAILED"
                    self.success = False
            elif (loginStatus == 0):

                Logger.error(f"{self.logIdentifier} Failed to login! Invalid Credentials!")
                self.state = "INVALID"
                self.success = False
            else:
                Logger.error(f"{self.logIdentifier} MaxRetryExceeded: Failed to login!")
                
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
                "https://www.nakedcph.com/en/customer/viewprofile?action=register"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [SolveCloudflare]")
            
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
            Logger.debug(f"{self.logIdentifier} Error while solving CloudFlare on Naked: {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on Naked: {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

    def login(self):
        """
            - Step [2]
                - Login

            - Params: None
            
            - Returns:
                - 1: Successfully login!
                - 0: User not login
                - -1: Failed to login MaxRetryExceeded
        """
               
        try:
            response = self.session.post(
                "https://www.nakedcph.com/en/auth/submit",
                headers={
                    "x-anticsrftoken": self.csrfToken,
                    "x-requested-with": "XMLHttpRequest"
                },
                data={
                    "_AntiCsrfToken": self.csrfToken,
                    "email": self.profile['email'],
                    "password": self.profile['password'],
                    "action": "login"
                }
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [LoginAccount]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from Naked [LoginAccount]")
            
            if (response.json()['Response']['Success']):
                return (1)
            else:
                return (0)

        except JSONDecodeError:
            self.retry += 1
            
            Logger.warning(f"{self.logIdentifier} Naked sent invalid response while login User ({self.retry}/3)")

            if (self.retry <= 3):
                return self.login()
            else:
                return (-1)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while login User {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while login User ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.login()
            else:
                return (-1)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while login User {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while login User! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.login()
            else:
                return (-1)

    def fetchProfile(self):

        """
            - Step [4]
                - Fetch Profile

            - Params: None
            
            - Returns:
                - 1: Successfully fetched
                - 0: Failed
                - -1: Failed to register MaxRetryExceeded
        """
        
        try:
            response = self.session.get(
                "https://www.nakedcph.com/en/customer/viewprofile"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [FetchProfile]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from Naked [FetchProfile]")
            
            if (response.status_code == 200):

                if "We have created a temporary account for you" not in response.text:
                    return (-2)
                    
                self.rememberToken = re.search('<a href="/en/customer/rememberme/(.+?)"', response.text).group(1)
                Logger.debug(f"{self.logIdentifier} RememberToken [{self.rememberToken}]")

                return (1)
            else:
                return (0)

        except JSONDecodeError:
            self.retry += 1
            
            Logger.warning(f"{self.logIdentifier} Naked sent invalid response while fetching Profile ({self.retry}/3)")

            if (self.retry <= 5):
                return self.fetchProfile()
            else:
                return (-1)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while fetching Profile {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while fetching Profile ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.fetchProfile()
            else:
                return (-1)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while fetching Profile {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while fetching Profile! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.fetchProfile()
            else:
                return (-1)

    def verifyAccount(self):

        """
            - Step [5]
                - Verify Account

            - Params: None
            
            - Returns:
                - 1: Successfully verified
                - 0: Failed
                - -1: Failed to verify MaxRetryExceeded
        """
        
        try:
            response = self.session.get(
                f"https://www.nakedcph.com/en/customer/rememberme/{self.rememberToken}"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [VerifyAccount]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from Naked [VerifyAccount]")
            
            if ("Ok, we will keep your personal data" in response.text):
                return (1)
            else:
                return (0)

        except JSONDecodeError:
            self.retry += 1
            
            Logger.warning(f"{self.logIdentifier} Naked sent invalid response while verifying account ({self.retry}/3)")

            if (self.retry <= 5):
                return self.verifyAccount()
            else:
                return (-1)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while verifying account {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while verifying account ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.verifyAccount()
            else:
                return (-1)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while verifying account{str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while verifying account! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.verifyAccount()
            else:
                return (-1)
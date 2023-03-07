"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 17/09/2021 11:27:59                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import *
if "darwin" not in platform.system().lower():
    from helheim.exceptions import (
        HelheimException
    )

class EnterRaffleTask:

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
        self.productId = raffle["metadata"]["productId"]
            
        self.userAgent = getRandomUserAgent()

        try:
            
            status = self.solveCloudflare()

            if status == 1:

                submitStatus = self.submit()

                if submitStatus == 1:
                    self.success = True
                    self.profile["status"] = "SUCCESS"
                    Logger.success(f"{self.logIdentifier} Successfully entered raffle!")
                else:
                    self.success = False
                    self.profile['status'] = "FAILED"
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
                "https://www.urbanstaroma.com/"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [SolveCloudflare]")

            if (response.status_code == 200):
                return (1)
            else:
                self.retry += 1
                Logger.warning(
                    f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

                if (self.retry <= self.maxRetry):
                    return self.solveCloudflare()
                else:
                    return (0)

        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} Error while solving CloudFlare on Naked: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on Naked: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)
        
    def submit(self):

        finalURL = 'https://www.urbanstaroma.com/en/dfs_core/customRequest/raffle/'

        final_data = {
            'product': self.productId,
            'fullname': self.profile["first_name"] + " " + self.profile["last_name"],
            'customemail': self.profile["email"],
            'product_size': self.profile["size"],
            'message': self.profile["message"],
            'customprivacy': '1'
        }
        try:
            r = self.session.post(finalURL, data=final_data)
            if r.status_code == 200:
                return 1
            else:
                self.retry += 1
                if self.retry < self.maxRetry:
                    Logger.error('Error while submitting entry, retrying...')
                    return self.submit()
                else:
                    Logger.error("Too many retries, stopping")
                    return 0

        except requests.exceptions.ProxyError:
            self.retry += 1
            if self.retry < self.maxRetry:
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
                Logger.error('Proxy error, rotating...')
                return self.submit()
            else:
                Logger.error("Too many retries, stopping")
                return 0

        except Exception as e:
            self.retry += 1
            if self.retry < self.maxRetry:
                Logger.error('Error : {}, retrying...'.format(str(e)))
                return self.submit()
            else:
                Logger.error("Too many retries, stopping")
                return 0

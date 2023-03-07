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
from imap_tools import MailBox, A
import regex as re

class EmailConfirmerTask():

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile
        self.list_urls = []

        """ Store """
        self.logIdentifier: str     = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state:         str     = "PENDING"
        self.success:       bool    = False
        self.retry:         int     = 0
        self.maxRetry:      int     = 10

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            
            self.executeTask()
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

            confirmEntry = self.confirmEntry()

            if confirmEntry == 1:
                Logger.success("Entry confirmed !")
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
                - Check if 200

            - Params: None

            - Returns:
                - 1: Successfully Solved CloudFlare
                - 0: Failed to SolveCloudflare (MaxRetryExceeded)
        """

        self.session, self.proxy = CreateCFSession()

        try:
            response = self.session.get(
                "https://raffle.bstn.com/"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from BSTN [SolveCloudflare]")

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

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on BSTN: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

    def confirmEntry(self):

        try:

            token = self.profile["link"].replace('https://raffle.bstn.com/verify/', '')
            data = {'token': token}
            response = self.session.get("https://raffle.bstn.com/api/verify", json=data)

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from BSTN [SolveCloudflare]")

            if (response.status_code == 201):
                return (1)
            else:
                self.retry += 1
                Logger.warning(
                    f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

                if (self.retry <= self.maxRetry):
                    return self.confirmEntry()
                else:
                    return (0)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on BSTN: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.confirmEntry()
            else:
                return (0)

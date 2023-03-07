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

        self.session = requests.Session()

        self.proxy = "Localhost"
        self.proxyLess = True

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

    def confirmEntry(self):

        try:
            response = self.session.get(self.profile["link"])

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Nittygritty [SolveCloudflare]")

            if (response.status_code == 200):
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
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on Nittygritty: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.confirmEntry()
            else:
                return (0)

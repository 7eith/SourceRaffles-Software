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

class EmailConfirmerTask():

    def __init__(self, index, taskNumber, profile, driver) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile
        self.list_urls = []
        self.driver = driver

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

        self.retry = 0

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
            time.sleep(random.randint(1,5))
            self.driver.get(self.profile["link"])
            time.sleep(3)
            self.driver.find_element_by_id("payment-submit-btn").click()
            time.sleep(4)
            Logger.success("Entry confirmed !")
            return 1
        except:
            Logger.error("Failed to confirm entry, please confirm manually and press Enter")
            input()
            return 1

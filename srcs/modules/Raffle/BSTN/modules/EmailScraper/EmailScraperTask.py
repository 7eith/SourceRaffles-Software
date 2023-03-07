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


class EntryScraperTask():

    def __init__(self, index, taskNumber, profile, loggerFile) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile
        self.linkslogger = loggerFile
        self.list_urls = []

        """ Store """
        self.logIdentifier: str     = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state:         str     = "PENDING"
        self.success:       bool    = False
        self.retry:         int     = 0
        self.maxRetry:      int     = 10

        self.mailSender = "service@bstn.com"
        self.stringTofind = "verify"

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

        result = self.scrapeMailBox()

        if result == 1:
            Logger.success("Links saved in csv !")
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def scrapeMailBox(self):

        try:
            if "gmail" in self.profile["email"]:
                imap_server = "imap.gmail.com"
            elif "outlook" in self.profile["email"]:
                imap_server = "outlook.office365.com"
            else:
                Logger.error('Auto confirm supported only for Outlook and Gmail, open a ticket to add another service.')
                return -1

            with MailBox(imap_server).login(self.profile["email"], self.profile["password"], 'INBOX') as mailbox:
                for msg in mailbox.fetch(A(seen=False, from_=self.mailSender)):
                    body = msg.html
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex, body)
                    urls = [x[0] for x in url]
                    for url in urls:
                        if self.stringTofind in url:
                            self.list_urls.append(url)
            if len(self.list_urls) == 0:
                Logger.error("No new link found in your mailbox.")
            else:
                Logger.info("{} link(s) found, saving to csv".format(len(self.list_urls)))
                return self.saveToCsv()
                
        except Exception as e:
            Logger.error("Error while scraping mail box : {}".format(str(e)))
            return -1

    def saveToCsv(self):
        try:
            try:
                with open(self.linkslogger, newline='') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    if headers == ["email", "link"]:
                        needHeaders = False
                    else:
                        needHeaders = True
            except FileNotFoundError:
                needHeaders = True

            with open(self.linkslogger, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                if needHeaders:
                    writer.writerow(["email", "link"])
                for url in self.list_urls:
                    writer.writerow([self.profile["email"], url])
            return 1

        except Exception as e:
            Logger.error("Error while saving links in the csv : {}".format(str(e)))
            return -1
"""********************************************************************"""
"""                                                                    """
"""   [AccountConfirmer] AccountConfirmerTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 04/10/2021 06:59:04                                     """
"""   Updated: 22/10/2021 20:00:41                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import requests
import random
from imap_tools import MailBox, A
from bs4 import BeautifulSoup
import regex as re
from core.configuration.Configuration import Configuration

from utilities import *

class AccountConfirmerTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

        self.session.headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': getRandomUserAgent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'dnt': '1',
        }

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.captchaToken: str = None
        self.proxyLess = False

        """ Utilities """
        self.initSession()

        status = self.executeTask()

        if (status == 1):
            self.success = True
            self.profile["status"] = "SUCCESS"
            Logger.success(f"{self.logIdentifier} Successfully created account!")
        else:
            self.success = False
            self.profile['status'] = "FAILED"
            
        if (not self.proxyLess):
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

    def scrapeEmails(self):
        try:
            emailConfirm = self.profile["masterEmail"]
            passwordConfirm = self.profile["masterPassword"]

            if "gmail" in emailConfirm:
                imap_server = "imap.gmail.com"
            elif "outlook" in emailConfirm:
                imap_server = "outlook.office365.com"
            else:
                Logger.error(f'{self.logIdentifier} Auto confirm supported only for Outlook and Gmail, open a ticket to add another service.')
                return -1
            self.list_urls = []
            with MailBox(imap_server).login(emailConfirm, passwordConfirm, 'INBOX') as mailbox:
                for msg in mailbox.fetch(A(seen=False, from_="no-reply@store.undercoverism.com")):
                    Logger.info(f"{self.logIdentifier} Found unreadead email. Reading...")
                    body = msg.text
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    url = re.findall(regex, body)
                    urls = [x[0] for x in url]
                    for url in urls:
                        if "access_key" in url and "undercoverism" in url:
                            Logger.info(f"{self.logIdentifier} URL found : {url}")
                            self.list_urls.append(url)
            if len(self.list_urls) == 0:
                Logger.error(f"{self.logIdentifier} No new link found in your mailbox")
                return -1
            else:
                Logger.info("{} {} link(s) found, starting confirmation.".format(self.logIdentifier, len(self.list_urls)))
                return self.confirmLinks()
        except Exception as e:
            Logger.error("{} Error while scraping urls : {}".format(self.logIdentifier, str(e)))
            return -1

    def confirmLinks(self):
        for link in self.list_urls:
            Logger.info("{} Confirming account for link : {}".format(self.logIdentifier, link))
            try:
                r = self.session.get(link)
                if r.status_code == 200:
                    Logger.info(f"{self.logIdentifier} Accessed main page, confirming password...")

                    fuelCsrfToken = self.session.cookies.get_dict().get("fuel_csrf_token")
                    access_key = link.split("?access_key=")[1]

                    headers = {
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                        'Upgrade-Insecure-Requests': '1',
                        'Origin': 'https://store.undercoverism.com',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Sec-GPC': '1',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'Referer': link,
                        'Accept-Language': 'fr-FR,fr;q=0.9',
                    }

                    data = {
                        'fuel_csrf_token': fuelCsrfToken,
                        'access_key': access_key,
                        'password': self.profile["password"],
                        'end': 'Register'
                    }

                    response = self.session.post('https://store.undercoverism.com/signup/step04', headers=headers, data=data)
                    if response.status_code == 200:
                        Logger.success(f"{self.logIdentifier} Account successfully confirmed !")
                        return 1
                    
                    if response.status_code == 503:
                        Logger.error(f"{self.logIdentifier} 503 - Service seems to be unavailable... ")
                        print(response.text)
                        print(response.status_code)

                else:
                    Logger.error("{} Error while confirming account : {}".format(self.logIdentifier, r.status_code))
                    return -1
            except Exception as e:
                Logger.error("{} Error while confirming account : {}".format(self.logIdentifier, str(e)))

    def executeTask(self):

        try:

            self.initSession()

            if self.profile["link"] == "":
                statusScrapeUrl = self.scrapeEmails()

                if statusScrapeUrl == 1:
                    Logger.success(f"{self.logIdentifier} Links scraped successfully !")

                    confirmAccounts = self.confirmLinks()

                    if confirmAccounts == 1:
                        Logger.success(f"{self.logIdentifier} Accounts confirmed !")
                        self.success = True
                        self.profile["status"] = "SUCCESS"

                    else:
                        self.success = False
                        self.profile["status"] = "FAILED"

                else:
                    self.success = False
                    self.profile["status"] = "FAILED"

            else:
                self.list_urls = [self.profile["link"]]
                confirmAccounts = self.confirmLinks()

                if confirmAccounts == 1:
                    Logger.success(f"{self.logIdentifier} Accounts confirmed !")
                    self.success = True
                    self.profile["status"] = "SUCCESS"
                    return (1)
                else:
                    self.success = False
                    self.profile["status"] = "FAILED"
                    return (0)
                    
        except Exception as e:
            Logger.error("{} Error while running task : {}".format(self.logIdentifier, str(e)))
            self.success = False
            self.profile["status"] = "FAILED"
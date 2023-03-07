"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffleInstore] InstoreRaffleTask.py                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/10/2021 20:31:27                                     """
"""   Updated: 03/10/2021 08:51:50                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 10/09/2021 05:43:30                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import cloudscraper
import random

from core.configuration.Configuration import Configuration

from utilities import *

class EnterRaffleTask:

    def initSession(self):

        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome', # we want a chrome user-agent
                'mobile': True,
                'platform': 'ios' # pretend to be a desktop by disabling mobile user-agents
            },
        )

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

        """ Utilities """

        if (self.raffle['loyalty'] is True):
            if ("card" not in self.profile or "dob" not in self.profile):
                self.success = False
                self.profile['status'] = "INVALID"
                Logger.error(f"{self.logIdentifier} Invalid Task! This raffle need Courir Card! (missing 'card' or 'dob' field)")
                return

        self.SizeDict = random.choice(self.raffle['sizeRange'])
                
        self.profile["Product"] = "Nike Dunk Low - Spartan Green"
        self.profile['Shop'] = self.raffle['shop']['name']
        self.profile["Size"] = self.SizeDict['name']
        
        self.initSession()

        try:

            status = self.executeTask()

            if (status == 1):
                self.success = True
                self.profile["status"] = "SUCCESS"
                Logger.success(f"{self.logIdentifier} Successfully entered and fetched card! Check your webhooks!")
            else:
                self.success = False
                self.profile['status'] = "FAILED"
                Logger.error(f"{self.logIdentifier} Failed to enter into Raffle...")

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

        Logger.log(f"{self.logIdentifier} Initializating Session...")
        initState = self.initializeEntry()

        if (initState == SUCCESS):
            Logger.info(f"{self.logIdentifier} Successfully initializated Session!")
            
            Logger.log(f"{self.logIdentifier} Entering Raffle...")

            postEntryStatus = self.postEntry()

            if (postEntryStatus == SUCCESS):
                Logger.info(f"{self.logIdentifier} Successfully entered! Fetching Wallet URL")

                status = self.getWalletURL()
                return status
            else:
                Logger.debug(f"{self.logIdentifier} Failed to Post Entry!")
                return postEntryStatus
        else:
            Logger.debug(f"{self.logIdentifier} Failed to Initialize Session!")
            return FAILED

    def initializeEntry(self):

        try:
            response = self.session.get(
                self.raffle['link']
            )

            if (response.status_code == 200):
                self.csrfToken = re.search('"csrf-token" content="(.+?)"', response.text).group(1)
                self.xsrfToken = self.session.cookies['XSRF-TOKEN']
                
                return (1)
            else:
                return (0)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while initializating Session {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to initializating Session Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.executeTask()
            else:
                return (-1)
                
    def postEntry(self):
                
        try:
            headers = {
                'authority': 'courir.captainwallet.com',
                'accept': 'application/json, text/plain, */*',
                'x-xsrf-token': self.xsrfToken,
                'x-csrf-token': self.csrfToken,
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json;charset=UTF-8',
                'origin': 'https://courir.captainwallet.com',
                'referer': self.raffle['link'],
            }

            if (self.raffle['loyalty'] is True):
                data = {
                    "store": self.raffle['shop']['content']['identifier'],
                    "cardId": self.profile['card'],
                    "birthdate": self.profile['dob'],
                    "sneakerSizes": [self.SizeDict['id']]
                }
            else:
                data = {
                    "email": self.profile['email'],
                    "firstname": self.profile['first_name'],
                    "lastname": self.profile['last_name'],
                    "sneakerSizes": [str(self.SizeDict['id'])],
                    "store": self.raffle['shop']['content']['identifier']
                }
                
            response = self.session.post(self.raffle['link'], headers=headers, json=data)

            if (response.status_code == 200):

                self.userProfile = response.json()
                return SUCCESS

            if (response.status_code == 404):
                Logger.error(f"{self.logIdentifier} This Courir card doesn't exist! ")
                return FAILED
            
            else:
                return FAILED
        
        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while posting entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to post Entry! Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.executeTask()
            else:
                return (-1)

    def getWalletURL(self):
                
        try:
            headers = {
                'authority': 'courir.captainwallet.com',
                'referer': self.raffle['link']
            }

            if (self.raffle['loyalty'] is True):

                params = {
                    'channel': 'store',
                    'tag': self.raffle['shop']['content']['identifier'],
                    'skip-hash': '1',
                    'user[store-raffle]': self.raffle['shop']['content']['identifier'],
                    'user[cardId]': self.userProfile['cardId'],
                    'user[tier]': self.userProfile['tier'],
                    'user[cardExpiresAt]': self.userProfile['cardExpiresAt'],
                    'user[identifier]': self.userProfile['identifier'],
                    'user[firstname]': self.userProfile['firstname'],
                    'user[lastname]': self.userProfile['lastname'],
                    'user[balance]': self.userProfile['balance'],
                    'user[employeeTypeCode]': self.userProfile['employeeTypeCode'],
                    'user[birthdate]': self.userProfile['birthdate'],
                    'user[sneakerSizes]': f'["{str(self.SizeDict["id"])}"]',
                    'user[offers]': self.userProfile['offers']
                }

            else:
                params = (
                    ('channel', "store"),
                    ('tag', self.raffle['shop']['content']['identifier']),
                    ('skip-hash', '1'),
                    ('user/[store-raffle/]', self.raffle['shop']['content']['identifier']),
                    ('user/[identifier/]', self.userProfile['identifier']),
                    ('user/[firstname/]', self.profile['first_name'].upper()),
                    ('user/[lastname/]', self.profile['last_name'].upper()),
                    ('user/[email/]', self.profile['email']),
                    ('user/[employeeTypeCode/]', '0'),
                    ('user/[sneakerSizes/]', f'/["{str(self.SizeDict["id"])}"/]'),
                )

            response = self.session.get(self.raffle['walletBaseURL'], headers=headers, params=params, allow_redirects=False)

            if (response.status_code == 302):
                Logger.debug(f"{self.logIdentifier} Wallet URL={response.headers['Location']}")
                self.walletURL = response.headers['Location']

                return SUCCESS
            else:

                Logger.debug(response.text)
                Logger.debug(response.status_code)

                return FAILED
                
        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while posting entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to post Entry! Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.executeTask()
            else:
                return (-1)
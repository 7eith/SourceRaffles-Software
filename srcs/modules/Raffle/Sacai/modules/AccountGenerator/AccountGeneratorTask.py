"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 04/10/2021 06:59:04                                     """
"""   Updated: 04/10/2021 13:10:19                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import requests
import random
import re

from bs4 import BeautifulSoup

from core.configuration.Configuration import Configuration

from utilities import *

class AccountGeneratorTask:

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

    def executeTask(self):

        initSessionState = self.initializeSession()

        if (initSessionState == SUCCESS):
            Logger.info(f"{self.logIdentifier} Successfully initializated Session!")

            createAccountState = self.createAccount()

            if (createAccountState == SUCCESS):

                Logger.info(f"{self.logIdentifier} Account submitted with success!")
                Logger.log(f"{self.logIdentifier} Confirming account...")

                confirmAccountState = self.confirmCreateAccount()

                if (confirmAccountState == SUCCESS):
                    return (SUCCESS)
                    
                elif (confirmAccountState == FAILED):
                    Logger.error(f"{self.logIdentifier} Error has happen when completing creating account... ")
                    return (FAILED)

            elif (createAccountState == FAILED):
                Logger.error(f"{self.logIdentifier} Error has happen when submitting account... ")
                return (FAILED)

            else:
                Logger.error(f"{self.logIdentifier} MaxRetryExceeded: Retry exceeded when creating account!")
                return (FAILED)
        else:
            return (FAILED)

    def initializeSession(self):

        try:
            response = self.session.get("https://store.sacai.jp/signup")

            if (response.status_code == 200):
                self.csrfToken = re.search('fuel_csrf_token" value="(.+?)"', response.text).group(1)
                return (SUCCESS)
            else:
                raise ConnectionError("Failed to initialize session!")
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while initializating session... {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to initializating session... Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.initializeSession()
            else:
                return (EXCEPTION)
                
    def createAccount(self):

        self.genderId = str(random.randint(1, 2))
        self.birthDay = str(random.randint(1, 28))
        self.birthMonth = str(random.randint(1, 12))
        self.birthYear = str(random.randint(1985, 2002))

        data = {
            'fuel_csrf_token': self.csrfToken,
            'back_url': 'https://store.sacai.jp/member/mod',
            'name1': self.profile['first_name'],
            'name2': self.profile['last_name'],
            'name1_kana': '',
            'name2_kana': '',
            'zip': self.profile['zip'],
            'city': self.profile['city'],
            'town': f"{self.profile['house_number']} {self.profile['street']}",
            'address': self.profile['additional'],
            'state': self.profile['state'],
            'country': self.profile['country'],
            'pref_id': '',
            'tel': self.profile['phone'],
            'mail': self.profile['email'],
            'password': self.profile['password'],
            'sex_id': self.genderId,
            'birth_year': self.birthYear,
            'birth_month': self.birthMonth,
            'birth_day': self.birthDay,
            'mail_info_send': '2',
            'mail_magazine_send_flag': '1',
            'check_preserve_login': '1',
            'preserve_login_flag': '1',
            'confirm': 'I AGREE TO TERMS AND CONFIRM'
        }
        
        try:

            response = self.session.post('https://store.sacai.jp/signup/step03', data=data)
            
            if (response.status_code == 200):

                if ("error-messages" in response.text):
                    soup = BeautifulSoup(response.text, "html.parser")
                    errors = soup.find_all("ul", {"class": "error-messages"})

                    for error in errors:
                        Logger.error(f"{self.logIdentifier} Error when submitting form: '{error.text}'")

                    return (FAILED)

                self.csrfToken = re.search('fuel_csrf_token" value="(.+?)"', response.text).group(1)
                return (SUCCESS)
            else:
                raise ConnectionError("Failed to create account (1/2)!")
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while creating account... {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to create account... Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.createAccount()
            else:
                return (EXCEPTION)

    def confirmCreateAccount(self):

        data = {
            'fuel_csrf_token': self.csrfToken,
            'back_url': 'https://store.sacai.jp/member/mod',
            'customer_attributes[1][lang]': 'en',
            'name1': self.profile['first_name'],
            'name2': self.profile['last_name'],
            'name1_kana': '',
            'name2_kana': '',
            'zip': self.profile['zip'],
            'city': self.profile['city'],
            'town': f"{self.profile['house_number']} {self.profile['street']}",
            'address': self.profile['additional'],
            'state': self.profile['state'],
            'country': self.profile['country'],
            'pref_id': '',
            'tel': self.profile['phone'],
            'mail': self.profile['email'],
            'password': self.profile['password'],
            'sex_id': self.genderId,
            'birth_year': self.birthYear,
            'birth_month': self.birthMonth,
            'birth_day': self.birthDay,
            'mail_info_send': '2',
            'mail_magazine_send_flag': '1',
            'check_preserve_login': '1',
            'preserve_login_flag': '1',
            'end': 'Send to email address'
        }
        
        try:

            response = self.session.post('https://store.sacai.jp/signup/pre_complete', data=data)
            
            if (response.status_code == 200):
                return (SUCCESS)
            else:
                raise ConnectionError("Failed to create account (2/2)!")
                
        except Exception as error:

            Logger.debug(f"{self.logIdentifier} Error while complete account... {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to complete account... Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.createAccount()
            else:
                return (EXCEPTION)
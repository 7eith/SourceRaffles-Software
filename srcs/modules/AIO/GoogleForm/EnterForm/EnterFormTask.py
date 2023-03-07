"""********************************************************************"""
"""                                                                    """
"""   [EnterForm] EnterFormTask.py                                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 23/09/2021 08:51:19                                     """
"""   Updated: 04/11/2021 12:09:57                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import requests
import re
import json

from core.configuration.Configuration import Configuration

from services.captcha import CaptchaHandler
from utilities import *

class EnterFormTask:

    def initSession(self):

        self.session = requests.Session()

        self.proxy = "Localhost"
        self.proxyLess = True

    def __init__(self, index, taskNumber, profile, formSettings) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile
        self.formSettings: dict = formSettings

        """ Store """
        if ("email" in self.profile):
            self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        else:
            self.logIdentifier: str = "[{}/{}]".format(self.index, self.taskNumber)

        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.captchaToken: str = None
        self.proxyLess = True

        """ Utilities """
        self.initSession()

        try:

            status = self.executeTask()

            if (status == SUCCESS):
                self.success = True
                self.profile["status"] = "SUCCESS"
                Logger.success(f"{self.logIdentifier} Successfully entered raffle!")
            else:
                self.success = False
                self.profile['status'] = "FAILED"

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def executeTask(self):

        self.responseIdentifier = "338709213841851914"

        if (self.formSettings['captcha']):
            self.captchaToken = ""

        self.prepareAnswer()

        scrapeStatus = self.scrapeFormParams()

        if (scrapeStatus == SUCCESS):
            Logger.info(f"{self.logIdentifier} Session fetched with Success!")

            self.retry = 0

            self.enterForm()

            for key, value in self.profile.items():
                if (type(value) == list):
                    self.profile[key] = "/-/".join(value)

            return (SUCCESS)
        else:
            Logger.error(f"{self.logIdentifier} Failed to fetch Session!")

            self.profile['status'] = "FAILED"
            self.success = False
            
            return (scrapeStatus)

    def prepareAnswer(self):

        pages = len(self.formSettings['pages'])
        data = {}

        if (pages > 1):

            if (self.formSettings['email']):

                draftDict = [
                    [],
                    None,
                    self.responseIdentifier,
                    None,
                    None,
                    None,
                    self.profile['email'],
                    1
                ]

            else:
                draftDict = [
                    [],
                    None,
                    self.responseIdentifier
                ]

            for index, page in enumerate(self.formSettings['pages']):
                if (index < pages):
                    for field in page:
                        answerData = []

                        fieldValue = self.profile[field['name']]

                        if (type(fieldValue) == list):
                            answerData = fieldValue
                        else:
                            answerData.append(fieldValue)
                        
                        self.profile[field['name']] = fieldValue

                        draftDict[0].append([
                            None,
                            field['id'],
                            answerData,
                            0
                        ])

        else:
            draftDict = [
                None,
                None,
                self.responseIdentifier
            ]

        for field in self.formSettings['pages'][-1]:
            value = self.profile[field['name']]

            data["entry.{}".format(field['id'])] = value

            self.profile[field['name']] = value

            if (field['type'] == "MULTIPLE_CHOICE" or field['type'] == "CHECKBOX"):
                data["entry.{}_sentinel".format(field['id'])] = ""

        if (self.formSettings['email']):
            data['emailAddress'] = self.profile['email']
        
        data['fvv'] = 1
        data['draftResponse'] = draftDict

        if (pages > 1):
            pageHistory = ""
            pageIndex = 0

            for page in self.formSettings['pages']:
                pageHistory += f"{pageIndex},"
                pageIndex += 1

            data['pageHistory'] = pageHistory
        else:
            data['pageHistory'] = 0

        if (self.formSettings['captcha']):
            data['g-recaptcha-response'] = self.captchaToken
            
        data['fbzx'] = self.responseIdentifier
        return (data)

    def scrapeFormParams(self):

        Logger.info(f"{self.logIdentifier} Fetching Session...")

        headers = {
			'authority': 'docs.google.com',
			'cache-control': 'max-age=0',
			'upgrade-insecure-requests': '1',
			'user-agent': getRandomUserAgent(),
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-user': '?1',
			'sec-fetch-dest': 'document',
			'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
			'dnt': '1',
		}

        try:
            response = self.session.get(
                self.formSettings['url'],
                headers=headers
            )
            
            self.responseIdentifier = re.search('name="fbzx" value="(.+?)">', response.text).group(1)

            return (SUCCESS)
            
        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while scrapping form {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to scrape form! Retrying.. ({self.retry}/{self.maxRetry})")

            if (self.retry <= self.maxRetry):
                return self.scrapeFormParams()
            else:
                return (FAILED)
                
    def enterForm(self):

        headers = {
            'authority': 'docs.google.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'origin': 'https://docs.google.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': getRandomUserAgent(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'dnt': '1',
        }

        data = self.prepareAnswer()

        response = requests.post(self.formSettings['postingURL'], headers=headers, data=data)

        if ("freebirdFormviewerViewResponseConfirmationMessage" in response.text):
            return (1)
        else:
            return (0)
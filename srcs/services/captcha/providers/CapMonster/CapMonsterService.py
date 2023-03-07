"""********************************************************************"""
"""                                                                    """
"""   [TwoCaptcha] TwoCaptchaService.py                                """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 06/09/2021 00:01:06                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from json.decoder import JSONDecodeError
import requests
import time

from utilities import Logger

class CapMonsterService():

    def __init__(self, apiKey, pollingInterval = 3) -> None:

        self.softId = 2815
        self.apiKey = apiKey
        self.pollingInterval = pollingInterval
        self.defaultTimeout = 600

        self.apiURL = "https://api.capmonster.cloud"

        self.defaultParams = {}
        self.defaultParams['clientKey'] = self.apiKey

    def askCaptchaIdentifier(self, **kwargs):
        params = {
            "clientKey": self.apiKey,
            "task": {**kwargs}
        }

        try:
            apiURL = self.apiURL + "/createTask"

            Logger.debug(f"[CapMonster] Parameters = {params}")
            response = requests.post(apiURL, json=params)

            data = response.json()

            if (data['errorId'] == 0):
                Logger.debug(f"[CapMonster] Successfully fetched Captcha Identifier | id={data['taskId']}")

                return {
                    "success": True,
                    "CaptchaIdentifier": data['taskId']
                }

            else:
                Logger.debug(f"[CapMonster] Failed to get a valid Captcha Identifier.. res={data}")

                return {
                    "success": False,
                    "error": data['errorDescription']
                }

        except JSONDecodeError as error:
            Logger.debug(f"[CapMonster-Error] {error}")

            return {
                "success": False,
                "error": "Invalid response from CapMonster.."
            }

        except (requests.ConnectionError, requests.RequestException) as error:
            Logger.debug(f"[CapMonster-Error] {error}")

            return {
                "success": False,
                "error": "Failed to send requests to CapMonster"
            }

    def waitCaptchaResult(self, identifier):
        maxWaitingTime = time.time() + self.defaultTimeout

        while time.time() < maxWaitingTime:
            
            try:
                result = self.askCaptchaResponse(identifier=identifier)

                if result['success']:
                    
                    return result

                else:

                    if (result['waiting']):
                        Logger.debug(f"[CapMonster] {identifier} is not ready... Waiting {self.pollingInterval} to retry")
                        time.sleep(self.pollingInterval)

                    else:
                        Logger.debug(f"[CapMonster] An error has occured after fetching result.. | res={result}")

            except Exception as error:
                Logger.error(error)
        pass

    def askCaptchaResponse(self, identifier):
        params = {
            "clientKey": self.apiKey,
            "taskId": identifier
        }

        try:
            apiURL = self.apiURL + "/getTaskResult"

            Logger.debug(f"[CapMonster] Asking CapMonster about {identifier}...")
            response = requests.post(apiURL, json=params)

            data = response.json()
            Logger.debug(data)

            if (data['status'] == "ready"):
                Logger.debug(f"[CapMonster] Successfully fetched Captcha Result | id={identifier}")

                return {
                    "success": True,
                    "code": data['solution']
                }

            else:
                if (data['status'] != "ready"):

                    return {
                        "success": False,
                        "waiting": True
                    }

                else:
                    Logger.debug(f"[CapMonster] An error has occured when fetching result about Captcha! {data}")

                    return {
                        "success": False,
                        "error": data['errorDescription']
                    }

        except JSONDecodeError as error:
            Logger.debug(f"[CapMonster-Error] {error}")

            return {
                "success": False,
                "error": "Invalid response from CapMonster.."
            }

        except (requests.ConnectionError, requests.RequestException) as error:
            Logger.debug(f"[CapMonster-Error] {error}")

            return {
                "success": False,
                "error": "Failed to send requests to CapMonster"
            }

    def solve(self, **kwargs):

        Logger.debug("[CapMonster] Asking CapMonster for a Captcha Solving...")

        response = self.askCaptchaIdentifier(**kwargs)

        if (response['success']):
            CaptchaIdentifier = response['CaptchaIdentifier']

            return self.waitCaptchaResult(identifier=CaptchaIdentifier)

        else:
            return {
                "success": False,
                "error": response['error']
            }

    def getBalance(self):
        """
            getBalance()
                return 2Captcha Balance
        """

        apiEndpoint = "{}/getBalance".format(self.apiURL)

        try:

            response = requests.post(apiEndpoint, json=self.defaultParams).json()
            
        except Exception as error:
            Logger.error("An error has occured when trying to fetch 2Captcha Balance...")
            Logger.error(error)

            return {
                "success": False,
                "error": error
            }

        if (response['errorId'] != 0):
            return {
                "success": False,
                "error": response['errorCode'],
                "message": response['errorDescription']
            }
        else:
            return {
                "success": True,
                "balance": response['balance'],
            }

    def solveReCaptcha(self, siteKey, url, version="v2", invisible=0, proxy=None):
        Logger.debug("[Captcha] Initializating ReCaptcha using CapMonster as provider.")
        Logger.debug(f"[Captcha] siteKey={siteKey}, url={url}, version={version}, invisible={invisible}, proxy={proxy}")

        if (version == "v3"):
            data = self.solve(type="RecaptchaV3TaskProxyless", websiteURL=url, websiteKey=siteKey, minScore=0.3)
        else:
            data = self.solve(type="NoCaptchaTaskProxyless", websiteURL=url, websiteKey=siteKey)

        if (data['success']):
            return {
                "success": True,
                "code": data['code']['gRecaptchaResponse']
            }
        else:
            return data
            
    def solveHCaptcha(self, siteKey, url, invisible=0, proxy=None):
        Logger.debug("[Captcha] Initializating HCaptcha using CapMonster as provider.")

        if (invisible == 1):
            invisible = True
        else:
            invisible = False
            
        Logger.debug(f"[Captcha] siteKey={siteKey}, url={url}, invisible={invisible}, proxy={proxy}")
        data = self.solve(type="HCaptchaTaskProxyless", websiteURL=url, websiteKey=siteKey, invisible=invisible)

        if (data['success']):
            return {
                "success": True,
                "code": data['code']['gRecaptchaResponse']
            }
        else:
            return data
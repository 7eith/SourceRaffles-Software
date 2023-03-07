"""********************************************************************"""
"""                                                                    """
"""   [TwoCaptcha] TwoCaptchaService.py                                """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 26/09/2021 21:57:56                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from json.decoder import JSONDecodeError
import requests
import time

from utilities import Logger

class TwoCaptchaService():

    def __init__(self, apiKey, pollingInterval = 10) -> None:

        self.softId = 2815
        self.apiKey = apiKey
        self.pollingInterval = pollingInterval
        self.defaultTimeout = 600

        self.apiURL = "https://2captcha.com/"

        self.defaultParams = {}
        self.defaultParams['key'] = self.apiKey
        self.defaultParams['json'] = 1
        self.defaultParams['soft_id'] = self.softId

    def askCaptchaIdentifier(self, **kwargs):
        params = {**kwargs, **self.defaultParams}

        try:
            apiURL = self.apiURL + "in.php"

            Logger.debug(f"[2Captcha] Parameters = {params}")
            response = requests.post(apiURL, params=params)

            data = response.json()

            if (data['status'] == 1):
                Logger.debug(f"[2Captcha] Successfully fetched Captcha Identifier | id={data['request']}")

                return {
                    "success": True,
                    "CaptchaIdentifier": data['request']
                }

            else:
                Logger.debug(f"[2Captcha] Failed to get a valid Captcha Identifier.. res={data}")

                return {
                    "success": False,
                    "error": data['error_text']
                }

        except JSONDecodeError as error:
            Logger.debug(f"[2Captcha-Error] {error}")

            return {
                "success": False,
                "error": "Invalid response from 2Captcha.."
            }

        except (requests.ConnectionError, requests.RequestException) as error:
            Logger.debug(f"[2Captcha-Error] {error}")

            return {
                "success": False,
                "error": "Failed to send requests to 2Captcha"
            }

    def waitCaptchaResult(self, identifier):
        maxWaitingTime = time.time() + self.defaultTimeout

        while time.time() < maxWaitingTime:
            
            try:
                result = self.askCaptchaResponse(identifier=identifier)

                if result['success']:
                    
                    return result

                else:

                    if ("waiting" in result):
                        Logger.debug(f"[2Captcha] {identifier} is not ready... Waiting {self.pollingInterval} to retry")
                        time.sleep(self.pollingInterval)

                    else:
                        Logger.debug(f"[2Captcha] An error has occured after fetching result.. | res={result}")
                        return result

            except Exception as error:
                Logger.error(error)
                return result
        pass

    def askCaptchaResponse(self, identifier):
        params = {
            "action": "get",
            "key": self.apiKey,
            "id": identifier,
            "json": 1
        }

        try:
            apiURL = self.apiURL + "res.php"

            Logger.debug(f"[2Captcha] Asking 2Captcha about {identifier}...")
            response = requests.post(apiURL, params=params)

            data = response.json()
            Logger.debug(data)

            if (data['status'] == 1):
                Logger.debug(f"[2Captcha] Successfully fetched Captcha Result | id={data['request']}")

                return {
                    "success": True,
                    "code": data['request']
                }

            else:
                if (data['request'] == "CAPCHA_NOT_READY"):

                    return {
                        "success": False,
                        "waiting": True
                    }

                else:
                    Logger.debug(f"[2Captcha] An error has occured when fetching result about Captcha! {data}")

                    if (data['request'] == "ERROR_CAPTCHA_UNSOLVABLE"):
                        return {
                            "success": False,
                            "error": "Captcha Unsolvable. Retrying..."
                        }

                    return {
                        "success": False,
                        "error": data['error_text']
                    }

        except JSONDecodeError as error:
            Logger.debug(f"[2Captcha-Error] {error}")

            return {
                "success": False,
                "error": "Invalid response from 2Captcha.."
            }

        except (requests.ConnectionError, requests.RequestException) as error:
            Logger.debug(f"[2Captcha-Error] {error}")

            return {
                "success": False,
                "error": "Failed to send requests to 2Captcha"
            }

    def solve(self, **kwargs):

        Logger.debug("[2Captcha] Asking 2Captcha for a Captcha Solving...")

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

        apiEndpoint = "{}/res.php".format(self.apiURL)

        try:

            response = requests.get(apiEndpoint, params={
                "key": self.apiKey,
                "action": "getbalance",
                "json": 1
            }).json()

        except Exception as error:
            Logger.error("An error has occured when trying to fetch 2Captcha Balance...")
            Logger.error(error)

            return {
                "success": False,
                "error": error
            }

        if (response['status'] != 1):
            return {
                "success": False,
                "error": response['request'],
                "message": response['error_text']
            }
        else:
            return {
                "success": True,
                "balance": response['request'],
            }

    def solveReCaptcha(self, siteKey, url, version="v2", invisible=0, proxy=None):
        Logger.debug("[Captcha] Initializating ReCaptcha using 2Captcha as provider.")
        Logger.debug(f"[Captcha] siteKey={siteKey}, url={url}, version={version}, invisible={invisible}, proxy={proxy}")

        return self.solve(version=version, method="userrecaptcha", googlekey=siteKey, pageurl=url, invisible=invisible)

    def solveHCaptcha(self, siteKey, url, invisible=0, proxy=None):
        Logger.debug("[Captcha] Initializating HCaptcha using 2Captcha as provider.")
        Logger.debug(f"[Captcha] siteKey={siteKey}, url={url}, invisible={invisible}, proxy={proxy}")

        return self.solve(method="hcaptcha", sitekey=siteKey, pageurl=url, invisible=invisible, proxy=proxy)
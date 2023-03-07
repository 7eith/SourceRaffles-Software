"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 11/10/2021 00:46:37                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
import time

from requests import ConnectionError
from json.decoder import JSONDecodeError

from services.captcha import CaptchaHandler
from services.mail import MailController
from utilities import *

if "darwin" not in platform.system().lower():
    from helheim.exceptions import (
        HelheimException
    )
    
class EnterRaffleTask:

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

        """ Utilities """
        self.profile["Product"] = raffle["product"]

        """ Session """
        self.session, self.proxy = CreateCFSession()
        self.raffleId = self.raffle["metadata"]["entryUrl"].replace('https://raffle.bstn.com/', '')

        try:
            
            self.executeTask()
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            
            if (self.profile['status'] == "PENDING"):
                self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def executeTask(self):
        
        Logger.log(f"{self.logIdentifier} Solving CloudFlare...")
        
        solveCloudFlareStatus: int = self.solveCloudflare()

        if (solveCloudFlareStatus == SUCCESS):
            self.retry = 0

            Logger.info(f"{self.logIdentifier} Successfully solved CloudFlare!")
            Logger.log(f"{self.logIdentifier} Submitting entry...")
            
            enterStatus = self.enterRaffle()

            if (enterStatus == SUCCESS):
                Logger.success(f"{self.logIdentifier} Successfully entered raffle!")

                if (self.raffle['AutoConfirmer']['status'] is True):
                    Logger.info(f"{self.logIdentifier} Launching AutoConfirmer! (Waiting ({self.raffle['AutoConfirmer']['delay']} s)")
                    time.sleep(self.raffle['AutoConfirmer']['delay'])
                    
                    self.retry = 0
                    self.maxRetry = 30

                    autoconfirmFetch = self.AutoConfirm_FetchLink()

                    if (autoconfirmFetch == SUCCESS):
                        self.retry = 0
                        self.maxRetry = 7
                        
                        Logger.info(f"{self.logIdentifier} Successfully fetched link to confirm your entry!")
                        confirmState = self.AutoConfirm_Confirm()

                        if (confirmState == SUCCESS):
                            Logger.success(f"{self.logIdentifier} Successfully AutoConfirmed Entry!")

                            self.profile['status'] = "CONFIRMED"
                            self.success = True

                        elif (confirmState == FAILED):
                            Logger.error(f"{self.logIdentifier} Failed to confirm entry maybe you have already confirmed entry.")

                            self.profile['status'] = "FAILED_AUTOCONFIRM"
                            self.success = True
                        
                        else:
                            Logger.error(f"{self.logIdentifier} MaxRetryExceeded while confirming entry!")

                            self.profile['status'] = "FAILED_AUTOCONFIRM"
                            self.success = True
                        
                    elif (autoconfirmFetch == FAILED):
                        self.profile['status'] = "FAILED_AUTOCONFIRM"
                        self.success = True
                    else:
                        self.profile['status'] = "FAILED_AUTOCONFIRM"
                        self.success = True
                else:
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

        try:
            response = self.session.get(
                self.raffle["metadata"]["entryUrl"]
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from BSTN [SolveCloudflare]")

            if response.status_code == 200:
                return SUCCESS
            else:
                self.retry += 1

                Logger.warning(
                    f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")

                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

                if self.retry <= self.maxRetry:
                    return self.solveCloudflare()
                else:
                    return (FAILED)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on BSTN: {str(error)}")

            self.retry += 1

            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")

            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (FAILED)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while solving CloudFlare on BSTN: {str(error)}")

            self.retry += 1

            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")

            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (FAILED)

    def enterRaffle(self):

        if (self.captchaToken == None):
            Logger.log(f"{self.logIdentifier} Solving Captcha...")
            
            captcha = CaptchaHandler().handleRecaptcha(
                '6LemOsYUAAAAABGFj8B7eEvmFT1D1j8IbXJIdvNn',
                self.raffle["metadata"]["entryUrl"],
                pollingInterval=3
            )

            if (captcha['success']):
                self.captchaToken = captcha['code']
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1
                
                Logger.warning(f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)")
                Logger.error(f"{self.logIdentifier} {captcha['error']}")
            
                if (self.retry <= 3):
                    return self.enterRaffle()
                else:
                    return (EXCEPTION)

        try:
            payload = {
                'additional': {
                    'instagram': self.profile["instagram"]
                },
                'title': 'female' if self.profile["gender"].lower() == "female" else 'male',
                'bDay': random.randint(1, 30),
                'bMonth': random.randint(1, 12),
                'email': self.profile["email"],
                'firstName': self.profile["first_name"],
                'lastName': self.profile["last_name"],
                'street': self.profile["street"],
                'streetno': self.profile["house_number"],
                'address2': self.profile["additional"],
                'zip': self.profile["zip"],
                'city': self.profile["city"],
                'country': self.profile["country"],
                'acceptedPrivacy': True,
                'newsletter': False,
                'recaptchaToken': self.captchaToken,
                'raffle': {'raffleId': self.raffleId, 'parentIndex': 0, 'option': self.profile["size"]},
                'issuerId': 'raffle.bstn.com'
            }

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error happen when making Payload! ")
            Logger.debug(f"{self.logIdentifier} Error: {str(error)} ")
            Logger.error(f"{self.logIdentifier} Error while entering! {str(error)}")
            
            return (FAILED)

        try:
            response = self.session.post('https://raffle.bstn.com/api/register', json=payload)
    
            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from BSTN [EnterRaffle]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from BSTN [EnterRaffle]")
            
            if (response.json()['message'] == "success"):
                return (SUCCESS)

            elif (response.json()['name'] == "GeneralError"):
                Logger.error(f"{self.logIdentifier} Error: {response.json()['message']}")

                self.retry += 1
                if (self.retry <= 3):
                    return self.enterRaffle()
                else:
                    return (EXCEPTION)
            else:
                return (FAILED)

        except JSONDecodeError:
            self.retry += 1
            
            Logger.warning(f"{self.logIdentifier} BSTN sent invalid response while submitting entry ({self.retry}/3)")

            if (self.retry <= 3):
                return self.enterRaffle()
            else:
                return (EXCEPTION)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while submitting entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while submitting entry ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.enterRaffle()
            else:
                return (EXCEPTION)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while submitting entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while submitting entry! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.enterRaffle()
            else:
                return (EXCEPTION)

    def AutoConfirm_FetchLink(self):

        if (self.retry >= self.maxRetry):
            Logger.error(f"{self.logIdentifier} Failed to AutoConfirm (MaxRetryExceeded)")
            return (EXCEPTION)

        state = MailController().fetchMail("service@bstn.com", self.profile['email'], "Verify your email", False, "verify")

        if (state['status'] is True):

            if (state['link'] is None):

                if ("mail" in state):
                    Logger.error(f"{self.logIdentifier} Found email but doesn't contains a valid links to verify your entry!")
                    return (FAILED)
                
                self.retry += 1
                delay = self.raffle['AutoConfirmer']['delay']
                Logger.warning(f"{self.logIdentifier} AutoConfirm hasn't found email yet! Retrying in {delay}s. ({self.retry}/{self.maxRetry})")
                time.sleep(delay)
                return (self.AutoConfirm_FetchLink())

            else:
                self.confirmLink = state['link']
                return (SUCCESS)
        else:
            Logger.error(f"{self.logIdentifier} Error happen while trying to AutoConfirm! \"{state['message']}\"")
            return (FAILED)

    def AutoConfirm_Confirm(self):

        try:
            response = self.session.post(
                'https://raffle.bstn.com/api/verify', 
                headers={
                    "referer": self.confirmLink
                },
                json={
                    "token": self.confirmLink.replace("https://raffle.bstn.com/verify/", "")
                }
            )
    
            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from BSTN [ConfirmLink]")
            Logger.debug(f"{self.logIdentifier} Received {response.text} from BSTN [ConfirmLink]")

            if (response.status_code == 201):
                return (SUCCESS)
            else:
                return (FAILED)
                
        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} CloudFlare exception while confirming entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Something went wrong with CloudFlare while confirming entry ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.AutoConfirm_Confirm()
            else:
                return (EXCEPTION)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while confirming entry {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} ConnectionError while confirming entry! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.AutoConfirm_Confirm()
            else:
                return (EXCEPTION)
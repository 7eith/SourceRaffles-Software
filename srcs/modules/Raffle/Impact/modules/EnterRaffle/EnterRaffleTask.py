"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 17/09/2021 11:27:59                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
import string

from core.configuration.Configuration import Configuration
import requests
from requests_toolbelt import MultipartEncoder

from services.captcha import CaptchaHandler
from utilities import *

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
        self.proxyLess = False

        """ Utilities """
        self.profile["Product"] = raffle["product"]
        self.profile["Size"] = random.choice(self.raffle['metadata']['sizes'])

        if (self.profile['payment'] != "Paypal"):
            self.profile['payment'] = "En Boutique"

        if (self.profile['shipping'] == "Pickup-Strasbourg"):
            self.profile['shipping'] = "Retrait en magasin (Strasbourg)"
        elif (self.profile['shipping'] == "Pickup-Mulhouse"):
            self.profile['shipping'] = "Retrait en magasin (Mulhouse)"
        else:
            self.profile['shipping'] = "Envoi Postal"
            
        self.userAgent = getRandomUserAgent()

        try:
            
            status = self.executeTask()

            if (status == 1):
                self.success = True
                self.profile["status"] = "SUCCESS"
                Logger.success(f"{self.logIdentifier} Successfully entered raffle!")
            else:
                self.success = False
                self.profile['status'] = "FAILED"
                
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

        headers = {
            'authority': 'www.impact-premium.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'user-agent': self.userAgent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'dnt': '1',
        }

        response = self.session.get('https://www.impact-premium.com/cf/raffle-1', headers=headers)

        if (response.status_code == 200):
            Logger.info(f"{self.logIdentifier} Session initialized with success!")
        else:
            Logger.error(f"{self.logIdentifier} Failed to initialize Session!")
    
    def executeTask(self):

        self.initSession()

        status = self.enterRaffle()

        if (status == 1):
            Logger.success(f"{self.logIdentifier} Successfully entered account (size={self.profile['Size']})")
            self.success = True
            self.profile["status"] = "SUCCESS"
        elif status == 0:
            Logger.error(f"{self.logIdentifier} Failed to enter into raffle")
            self.success = False
            self.profile["status"] = "FAILED"
        else:
            Logger.error(f"{self.logIdentifier} Failed to enter into raffle (MaxRetryExceeded)")
            self.success = False
            self.profile["status"] = "MaxRetryExceeded"
        
    def enterRaffle(self):

        if self.captchaToken == None:
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                "6LdgCYoaAAAAAOiwh9Vi_rpwp3I31r4WrE7IfMKa",
                self.raffle["metadata"]["entryURL"],
                pollingInterval=3
            )

            if captcha["success"]:
                self.captchaToken = captcha["code"]
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1

                Logger.warning(
                    f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)"
                )
                Logger.error(f"{self.logIdentifier} {captcha['error']}")

                if self.retry <= 3:
                    return self.executeTask()
                else:
                    return (-1)

        fields = {
            "c_pointure": self.profile['Size'],
            "c_name": self.profile['last_name'],
            "c_prenom": self.profile['first_name'],
            "c_adresse": f"{self.profile['house_number']} {self.profile['street']}",
            "c_code_postal": self.profile['zip'],
            "c_ville": self.profile['city'],
            "c_myemail": self.profile['email'],
            "c_numero_telephone": self.profile['phone'],
            "c_pays": self.profile['country'],
            "c_paiement": self.profile['payment'],
            "c_livraison": self.profile['shipping'],
            "g-recaptcha-response": self.captchaToken,
            "submitform": "Valider mon inscription",
            "fid": '1'
        }

        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        EncodedFields = MultipartEncoder(fields=fields, boundary=boundary)

        headers = {
            'authority': 'www.impact-premium.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://www.impact-premium.com',
            'content-type': EncodedFields.content_type,
            'user-agent': self.userAgent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.impact-premium.com/cf/raffle-1',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'dnt': '1',
        }

        try:
            response = self.session.post(
                'https://www.impact-premium.com/cf', 
                headers=headers, 
                data=EncodedFields,
                allow_redirects=False
            )

            if (response.status_code == 302 and response.headers['Location'] == "https://www.impact-premium.com/content/7-raffle-confirmation"):
                return (1)
            else:
                return (0)

        except Exception as error:
            Logger.debug(f"{self.logIdentifier} Error while submitting entry.. {str(error)}")
            
            self.retry += 1
            Logger.warning(f"{self.logIdentifier} Failed to submit entry! Retrying.. ({self.retry}/{self.maxRetry})")
            
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.enterRaffle()
            else:
                return (-1)
                
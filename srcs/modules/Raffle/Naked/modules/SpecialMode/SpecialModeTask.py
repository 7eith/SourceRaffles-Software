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

"""
Steps : 1 - Scrape products until finding an available size, get the product id from url
        2 - Login
        3 - Initiate checkout
        4 - Generate random information
        5 - Finish checkout
"""

from core.configuration.Configuration import Configuration
import requests
import random
from bs4 import BeautifulSoup
from services.captcha import CaptchaHandler
from utilities import *
if "darwin" not in platform.system().lower():
    from helheim.exceptions import (
        HelheimException
    )

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

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
        self.profile["Product"] = raffle["product"]
        self.initSession()

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

    def solveCloudflare(self):
        """
            - Step [1]
                - Solve CloudFlare
                - Check if 200 and got a CSRFToken

            - Params: None

            - Returns:
                - 1: Successfully Solved CloudFlare
                - 0: Failed to SolveCloudflare (MaxRetryExceeded)
        """

        self.session, self.proxy = CreateCFSession()

        try:
            response = self.session.get(
                "https://www.nakedcph.com/en/customer/viewprofile?action=register"
            )

            Logger.debug(f"{self.logIdentifier} Received {response.status_code} from Naked [SolveCloudflare]")

            if (response.status_code == 200):
                self.csrfToken = self.session.cookies.get_dict().get("AntiCsrfToken")

                return (1)
            else:
                self.retry += 1
                Logger.warning(
                    f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

                if (self.retry <= self.maxRetry):
                    return self.solveCloudflare()
                else:
                    return (0)

        except HelheimException as error:
            Logger.debug(f"{self.logIdentifier} Error while solving CloudFlare on Naked: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

        except ConnectionError as error:
            Logger.debug(f"{self.logIdentifier} ConnectionError while solving CloudFlare on Naked: {str(error)}")

            self.retry += 1
            Logger.warning(
                f"{self.logIdentifier} Failed to solve CloudFlare.. Rotating Session! ({self.retry}/{self.maxRetry})")
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            if (self.retry <= self.maxRetry):
                return self.solveCloudflare()
            else:
                return (0)

    def scrapeProducts(self):
        self.urlList = []
        try:
            getProductsRequest = self.session.get("https://www.nakedcph.com/en/2/sneakers")
            if getProductsRequest.status_code == 200:
                Logger.success("Accessed main page ! Scraping products...")
                soup = BeautifulSoup(getProductsRequest.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    url = a['href']
                    list_brand = ["new-balance", "reebok", "nike", "jordan", "adidas"]
                    for brand in list_brand:
                        if brand in url and "product" in url:
                            self.urlList.append("https://www.nakedcph.com" + url)

        except Exception as e:
            Logger.error("Error while getting products page to scrape products : {}".format(str(e)))
            self.retry += 1
            if self.retry < self.maxRetry:
                self.scrapeProducts()
                return
            
    def scrapeProductInformation(self):
        self.productUrl = random.choice(self.urlList)
        Logger.info("Using url : {}".format(self.productUrl))
        self.urlList.remove(self.productUrl)
        Logger.info("Removing product url from list of scraped urls")
        
        try:
            productInformationRequest = self.session.get(self.productUrl)
            if productInformationRequest.status_code == 200:
                Logger.success("Accessed product page !")
        except Exception as e:
            Logger.error("Error while getting product page to scrape product informations : {}".format(str(e)))
            self.retry += 1
            if self.retry < self.maxRetry:
                self.scrapeProductInformation()
                return
            

    def executeTask(self):

        if self.captchaToken == None:
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleHCaptcha(
                "1ec22aa7-94d5-4d65-b7b6-3bbe8c87b233",
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

        Logger.log(f"{self.logIdentifier} Bypassing CloudFlare...")
        Logger.log(f"{self.logIdentifier} CloudFlare bypassed! ")

        headers = {
            "authority": "helpers.rule.se",
            "cache-control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "upgrade-insecure-requests": "1",
            "origin": "https://www.nakedcph.com",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": getRandomUserAgent(),
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.nakedcph.com/",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
            "dnt": "1",
        }

        data = {
            'tags[]': self.raffle["metadata"]["tags"],
            'token': self.raffle["metadata"]["token"],
            'rule_email': self.profile['email'],
            'fields[Raffle.Instagram Handle]': self.profile['instagram'],
            'fields[Raffle.Phone Number]': self.profile['phone'],
            'fields[Raffle.First Name]': self.profile['first_name'],
            'fields[Raffle.Last Name]': self.profile['last_name'],
            'fields[Raffle.Shipping Address]': f"{self.profile['house_number']} {self.profile['street']}",
            'fields[Raffle.Postal Code]': self.profile['zip'],
            'fields[Raffle.City]': self.profile['city'],
            'fields[Raffle.Country]': self.profile['country_code'],
            'fields[SignupSource.ip]': "192.0.0.1",
            'fields[SignupSource.useragent]': 'Mozilla',
            'language': 'sv',
            'g-recaptcha-response': self.captchaToken,
            'h-captcha-response': self.captchaToken
        }

        try:
            response = self.session.post(
                'https://helpers.rule.se/raffle/naked.php', 
                headers=headers, 
                data=data,
                allow_redirects=False
            )

            if (response.status_code == 302 and response.headers['Location'] == "https://www.nakedcph.com/en/775/you-are-now-registered-for-our-fcfs-raffle"):
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
                return self.executeTask()
            else:
                return (-1)

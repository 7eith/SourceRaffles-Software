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

from core.configuration.Configuration import Configuration
import requests

from services.captcha import CaptchaHandler
from utilities import *

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

            status = self.solveCloudflare()

            if status == 1:
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
        try:
            r = self.session.get(self.raffle["url"])

            if r.status_code == 200:
                return self.submitEntry()
            else:
                Logger.error(f"{self.logIdentifier} Cloudflare has blocked the request!")
                return -1

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when solving cloudflare : {error}"
            )
            return -1

    def submitEntry(self):

        headers = {
            'authority': 'a.klaviyo.com',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua-mobile': '?0',
            'access-control-allow-headers': '*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'accept': '*/*',
            'origin': 'https://oqium.com',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://oqium.com/',
        }

        data = {
            'g': 'Sns8cz',
            '$fields': '$source,$first_name,$last_name,$email,$phone_number,Size,Instagram Account,$address1,$zip,$city,$country,Accepts Marketing,$consent_method,$consent_form_id,$consent_form_version,services',
            '$list_fields': 'Accepts Marketing',
            '$timezone_offset': '1',
            '$source': self.raffle["metadata"]["source"], ## format 555088-611
            '$first_name': self.profile["first_name"],
            '$last_name': self.profile["last_name"],
            '$email': self.profile["email"],
            '$phone_number': self.profile["phone_number"],
            'Size': self.profile["size"], ## format US 7 / EU 40
            'Instagram Account': self.profile["instagram"],
            '$address1': self.profile["address"],
            '$zip': self.profile["zip"],
            '$city': self.profile["city"],
            '$country': self.profile["country"],
            'Accepts Marketing': 'YesByRaffle',
            '$consent_method': 'Klaviyo Form',
            '$consent_form_id': self.raffle["metadata"]["form_id"], ## format QYG2na
            '$consent_form_version': self.raffle["metadata"]["version_consent"], ## format 4395213
            'services': '{"shopify":{"source":"form"}}',
            '$exchange_id': self.raffle["metadata"]["exchange_id"], ## format xdM6mEMQU8Wrkbfr61R5Bt5X16htqt633cOTgJsxxN5C76tKVOda0aQIrEd1tJ5u.R3sbqs
        }

        try:
            response = self.session.post('https://a.klaviyo.com/ajax/subscriptions/subscribe', headers=headers, data=data)
            if (response.status_code == 200):
                return 1
            else:
                Logger.error(f"{self.logIdentifier} Failed to enter raffle : {response.status_code} / {response.text}")
                return 0
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1

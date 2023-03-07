"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 20:08:48                                     """
"""   Updated: 29/09/2021 20:21:22                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from core.configuration.Configuration import Configuration
from utilities import *
from bs4 import BeautifulSoup
import random
from requests.exceptions import ProxyError


class EnterRaffleTask:

    def initSession(self):
        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile, raffle) -> None:

        """ Props """
        self.index: int = index + 1
        self.profileNumber: int = taskNumber
        self.profile: dict = profile
        self.raffle: dict = raffle

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.profileNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.proxyLess = False

        """ Utilities """
        self.profile["Product"] = raffle["product"]

        self.initSession()

        try:
            status = self.submit()
            if status == 1:
                Logger.success(f"{self.logIdentifier} Entry submitted !")
                self.success = True
                self.profile['status'] = "SUCCESS"

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

    def generateRandomTimeline(self):
        timestamp = round(time.time() * 1000)

        expando = "jQuery1.9.00."
        expando += str(random.randint(0, 9999999999999999))
        expando += "_"
        expando += str(timestamp)

        return {
            "expando": f"{expando.replace('.', '')}{str(timestamp)}",
            "submitTime": f"{str(timestamp + random.randint(1, 2))}",
        }

    def submit(self):

        Logger.info("Submitting entry...")

        timeLine = self.generateRandomTimeline()

        params = (
            ("u", self.raffle["u"]),
            ("id", self.raffle["id"]),
            ("c", timeLine["expando"]),
            ("EMAIL", self.profile["email"]),
            ("FNAME", self.profile["first_name"]),
            ("LNAME", self.profile["last_name"]),
            ("PHONE", self.profile["phone"]),
            ('MMERGE6', self.profile['country']),
            (f'{self.raffle["params"]["Birthday"]}[day]', self.profile["day"]),
            (f'{self.raffle["params"]["Birthday"]}[month]', self.profile["month"]),
            ('MMERGE9', self.profile['gender']),
            (f'{self.raffle["params"]["Instagram"]}', self.profile["instagram"]),
            (f'{self.raffle["params"]["Store"]["fieldName"]}', self.profile["shop"]),
            (f'{self.raffle["params"]["Sizes"]["fieldName"]}', self.profile["size"]),
            (f"b_{self.raffle['u']}_{self.raffle['id']}", ""),
            ("subscribe", "Subscribe"),
            ("_", timeLine["submitTime"]),
        )

        try:
            response = self.session.get(
                "https://solebox.us16.list-manage.com/subscribe/post-json",
                params=params,
            )
            Logger.debug(response.text)

        except Exception as error:
            Logger.error(f"Uncatched error... {error}")
            return -1

        if "already subscribed" in response.text:
            Logger.error("Already subscribed to this raffle!")
            return -1

        if "success" in response.text:
            return 1

"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 05/09/2021 01:15:08                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import *
from mohawk import Sender


class AccountGeneratorTask():

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10

        """ Mesh Keys """
        self.apiKey = "0ce5f6f477676d95569067180bc4d46d"
        self.key = "EfvEQ0WPLNPmKgTBCEDayn89SDOdD9Y5"
        self.id = "1f1dfc2d"

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")

        try:
            self.initSession()
            self.executeTask()

            if Configuration().getConfiguration()["ProxyLess"]:
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def executeTask(self):

        status = self.login()

        if status == 1:
            Logger.success(f"{self.logIdentifier} Account created for {self.profile['email']} !")
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def generateHeaders(self, url, requestMethod="POST"):

        content = ''
        content_type = 'application/json'

        sender = Sender(
            credentials={
                'id': self.id,
                'key': self.key,
                'algorithm': 'sha256'
            },
            url=url,
            method=requestMethod,
            content=content,
            content_type=content_type)

        return sender.request_header

    def getCaptcha(self, action):

        baseUrl = "https://footpatrolgb-mosaic-webapp.jdmesh.co"
        sitekey = "6LcHpaoUAAAAANZV81xLosUR8pDqGnpTWUZw59hN"
        apiKey = random.choice(Configuration().getConfiguration()["CaptchaServices"][Configuration().getConfiguration()["CaptchaServices"]["Favorite"]])

        r = requests.get(
            f"http://2captcha.com/in.php?key={apiKey}&method=userrecaptcha&version=v3&action={action}&min_score=0.3&googlekey={sitekey}&pageurl={baseUrl}&json=1")
        Logger.debug(r.json())

        rep = r.json()
        id = rep["request"]
        Logger.info(f"{self.logIdentifier} Getting captcha token")
        while True:
            r = requests.get(f"http://2captcha.com/res.php?key={apiKey}&action=get&id={id}&json=1")
            if r.json()["request"] == "CAPCHA_NOT_READY":
                time.sleep(5)
                Logger.debug(f"{self.logIdentifier} captcha not ready")
            else:
                Logger.info(r.json())
                return r.json()["request"]

    def login(self):

        signupUrl = "https://mosaic-platform.jdmesh.co/stores/footpatrolgb/users/signup?" \
                    "api_key=6048110e2d7e087082d9a8d1c07b9e2c&channel=iphone-mosaic"

        headers = {
            'Host': 'mosaic-platform.jdmesh.co',
            'Accept': '*/*',
            'Authorization': self.generateHeaders(url=signupUrl, requestMethod="POST"),
            'originalhost': 'mosaic-platform.jdmesh.co',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://footpatrolgb-mosaic-webapp.jdmesh.co',
            'Connection': 'keep-alive',
            'User-Agent': 'FP Launch-2.4.1.0 iPhone',
            'Referer': 'https://footpatrolgb-mosaic-webapp.jdmesh.co/?channel=iphone-mosaic&appversion=2&buildversion=2.4.1.0'
        }

        data = {
           "guestUser": False,
           "loggedIn": False,
           "firstName": self.profile["first_name"],
           "lastName": self.profile["last_name"],
           "password": self.profile["password"],
           "addresses": [
              {
                 "firstName": self.profile["first_name"],
                 "lastName": self.profile["last_name"],
                 "address1": self.profile["address1"],
                 "address2": self.profile["address2"],
                 "town": self.profile["city"],
                 "county": self.profile["region"],
                 "postcode": self.profile["zipcode"],
                 "locale": self.profile["country_code"].lower(),
                 "phone": self.profile["phone"],
                 "isPrimaryAddress": True,
                 "isPrimaryBillingAddress": True
              }
           ],
           "email": self.profile["email"],
           "verification": self.getCaptcha(action="Login/SignUp")
        }

        Logger.info(f"{self.logIdentifier} Creating account")

        try:
            r = self.session.post(
                url=signupUrl,
                json=data,
                headers=headers
            )
        except Exception as e:
            Logger.error("Error while creating account : {}".format(str(e)))
            return -1

        if r.status_code != 200:
            Logger.error("Error while creating account : {} / {}".format(r.status_code, r.text))
            return -1

        return 1

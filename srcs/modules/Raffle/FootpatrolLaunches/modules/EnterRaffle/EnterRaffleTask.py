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
from py_adyen_encrypt import encryptor


class EnterRaffleTask():

    def __init__(self, index, taskNumber, profile, raffle) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile
        self.raffle: dict = raffle

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

            # if Configuration().getConfiguration()["ProxyLess"]:
            #     self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def initSession(self):

        self.session = requests.Session()

        # if Configuration().getConfiguration()["ProxyLess"] == False:
        #     self.proxy = ProxyManager().getProxy()
        #     self.session.proxies.update(self.proxy['proxy'])
        # else:
        #     self.proxy = "Localhost"
        #     self.proxyLess = True

    def executeTask(self):

        status = self.login()

        if status == 1:
            Logger.success(f"{self.logIdentifier} Entry successfull {self.profile['email']}!")
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
        apiKey = "8793a27f00aba51877a539f587475ea2"

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
                Logger.debug(f"{self.logIdentifier}captcha not ready")
            else:
                return r.json()["request"]

    def login(self):

        loginUrl = "https://mosaic-platform.jdmesh.co/stores/footpatrolgb/users/login?" \
                   "api_key=6048110e2d7e087082d9a8d1c07b9e2c&channel=iphone-mosaic"

        data = {
           "guestUser": False,
           "loggedIn": False,
           "firstName": self.profile["first_name"],
           "lastName": self.profile["last_name"],
           "password": self.profile["password"],
           "password2":"",
           "username": self.profile["email"],
           "billing":{
              "firstName":"",
              "lastName":"",
              "address1":"",
              "address2":"",
              "town":"",
              "county":"",
              "postcode":"",
              "locale":"",
              "phone":""
           },
           "delivery":{
              "firstName":"",
              "lastName":"",
              "address1":"",
              "address2":"",
              "town":"",
              "county":"",
              "postcode":"",
              "locale": self.profile["country_code"].lower(),
              "phone":"",
              "useAsBilling": True
           },
           "verification": self.getCaptcha(action="Login/SignUp")
        }

        headers = {
            'Host': 'mosaic-platform.jdmesh.co',
            'Accept': '*/*',
            'Authorization': self.generateHeaders(url=loginUrl, requestMethod="POST"),
            'originalhost': 'mosaic-platform.jdmesh.co',
            # 'Accept-Language': 'de-de',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://footpatrolgb-mosaic-webapp.jdmesh.co',
            'Content-Length': '957',
            'Connection': 'keep-alive',
            'User-Agent': 'FP Launch-2.4.1.0 iPhone',
            'Referer': 'https://footpatrolgb-mosaic-webapp.jdmesh.co/?channel=iphone-mosaic&appversion=2&buildversion=2.4.1.0'
        }

        Logger.info(f"{self.logIdentifier}Logging in")
        try:
            r = self.session.post(
                url=loginUrl,
                json=data,
                headers=headers
            )
        except Exception as e:
            Logger.error("Error while logging in : {}".format(str(e)))
            return -1

        if r.status_code != 200:
            Logger.error("Error while logging in : {} / {}".format(r.status_code, r.text))
            return -1

        Logger.info(f"{self.logIdentifier}Logged in")
        self.loginResponse = r.json()
        return self.fetchDelivertyMethods()

    def fetchDelivertyMethods(self):

        headers = {
            'Host': 'mosaic-platform.jdmesh.co',
            'Origin': 'https://footpatrolgb-mosaic-webapp.jdmesh.co',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'FP Launch-2.4.1.0 iPhone',
            'originalhost': 'mosaic-platform.jdmesh.co',
            'Accept-Language': 'de-de',
            'Referer': 'https://footpatrolgb-mosaic-webapp.jdmesh.co/?channel=iphone-mosaic&appversion=2&buildversion=2.4.1.0'
        }

        r = requests.get(
            'https://mosaic-platform.jdmesh.co/stores/'
            'footpatrolgb/deliverymethods?api_key=6048110e2d7e087082d9a8d1c07b9e2c&'
            'channel=iphone-mosaic&locale={}'.format(self.profile["country_code"].lower()),
            headers=headers)

        if r.status_code == 200:
            Logger.info(f"{self.logIdentifier}good request response")
            try:
                methods = r.json()["deliverytypes"][0]["options"]
                freeMethod = [x for x in methods if x["name"] == "France Standard Delivery"][0]
            except IndexError:
                Logger.error("Free delivery method not found")
                return -1

            self.deliveryMethod = freeMethod
            self.deliveryMethod["type"] = "delivery"
            Logger.info(self.deliveryMethod)
            return self.preAuth()

        else:
            Logger.error(f"{self.logIdentifier}Error while getting delivery methods : {r.status_code} / {r.text}")
            return -1

    def preAuth(self):

        preAuthUrl = "https://mosaic-platform.jdmesh.co/stores/footpatrolgb/preAuthorise/order?" \
                     "api_key=6048110e2d7e087082d9a8d1c07b9e2c&channel=iphone-mosaic"

        headers = {
            'Host': 'mosaic-platform.jdmesh.co',
            'Accept': '*/*',
            'Authorization': self.generateHeaders(url=preAuthUrl, requestMethod="POST"),
            'originalhost': 'mosaic-platform.jdmesh.co',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://footpatrolgb-mosaic-webapp.jdmesh.co',
            'Content-Length': '1375',
            'Connection': 'keep-alive',
            'User-Agent': 'FP Launch-2.4.1.0 iPhone',
            'Referer': 'https://footpatrolgb-mosaic-webapp.jdmesh.co/?channel=iphone-mosaic&appversion=2&buildversion=2.4.1.0'
        }

        data = {
            "customer": {
                "isPrefilled": False,
                "firstName": self.profile["first_name"],
                "lastName": self.profile["last_name"],
                "email": self.profile["email"],
                "phone": self.profile["phone"]
                },
            "delivery": {
                "isPrefilled": False,
                "firstName": self.profile["first_name"],
                "lastName": self.profile["last_name"],
                "postcode": self.profile["zipcode"],
                "address1": self.profile["address1"],
                "address2": self.profile["address2"],
                "town": self.profile["city"],
                "county": self.profile["region"],
                "locale": self.profile["country_code"].lower()
                },
            "billing": {
                "isPrefilled": False,
                "firstName": self.profile["first_name"],
                "lastName": self.profile["last_name"],
                "postcode": self.profile["zipcode"],
                "address1": self.profile["address1"],
                "address2": self.profile["address2"],
                "town": self.profile["city"],
                "county": self.profile["region"],
                "locale": self.profile["country_code"].lower()
                },
            "deliveryMethod": self.deliveryMethod,
            "optionID": self.raffle["metadata"]["productId"] + ":" + self.profile["size"],  # US sizing
            "productID": self.raffle["metadata"]["productId"],
            "userID": self.loginResponse["customer"]["userID"],
            "verification": self.getCaptcha(action="PreAuth_Create")
        }

        Logger.info("Pre-Authenticating")
        try:
            r = self.session.post(
                url=preAuthUrl,
                headers=headers,
                json=data)
        except Exception as e:
            Logger.error("Error while making preauthentification in : {}".format(str(e)))
            return -1

        if r.status_code != 200:
            Logger.error("Error while making preauth : {} / {}".format(r.status_code, r.text))
            return -1

        Logger.info("First preauth completed")

        self.preAuthResponse = r.json()
        return self.payment()

    def payment(self):

        self.orderID = self.preAuthResponse["orderID"]

        paymentUrl = "https://mosaic-platform.jdmesh.co/stores/footpatrolgb/preAuthorise/payment/" \
                     "{}?api_key=6048110e2d7e087082d9a8d1c07b9e2c&channel=iphone-mosaic&type=CARD".format(self.orderID)

        headers = {
            'Host': 'mosaic-platform.jdmesh.co',
            'Accept': '*/*',
            'Authorization': self.generateHeaders(url=paymentUrl, requestMethod="PUT"),
            'originalhost': 'mosaic-platform.jdmesh.co',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://footpatrolgb-mosaic-webapp.jdmesh.co',
            # 'Content-Length': '4132',
            'Connection': 'keep-alive',
            'User-Agent': 'FP Launch-2.4.1.0 iPhone',
            'Referer': 'https://footpatrolgb-mosaic-webapp.jdmesh.co/?channel=iphone-mosaic&appversion=2&buildversion=2.4.1.0'
        }

        self.adyenKey = "10001|8677B0C92CA9D3FF33C345BD024EBC6235D2A79DEFFCE50F28F517447AECD7D95CD0663842CDB51D63E78AD86EDF4B4D569824B41B161E479909A4B141ED9C1CD7C492B81ECABD4D6984413D456BF4016C09E17283D436AEED0C85B0C9B745D9D19823123100A7D8E0EF8B32ED7191EC740F839D5C91C4A415F7750D1D69CC46DFA3E058007490133993E76C43B2D70B005A7BFA73DD66C652DAAC861B686C891B89B24C54F4F699D0770A2D53BFF29B60DBA42777C3A1C0ACCDA49CDF18382637DDE4123413FBEB897F3BD96B5467A3DB9606764979BCB6480BF497D0C75FFB719A4E54D0612982E0393B1A6BDF25546EE3D6443B9AEF5A1210A10AC2C26259"

        import pytz

        generation_time = datetime.now(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        enc = encryptor(self.adyenKey)
        data = {
            "cvc": self.profile["card_cvc"],
            "number": self.profile["card_number"],
            "expiryYear": self.profile["card_year"],  # XXXX format
            "expiryMonth": self.profile["card_month"],  # XX format
            "generationtime": generation_time
        }
        encoded = enc.encrypt_from_dict(dict_=data)

        # data = {
        #     "encryptedData": "adyenjs_0_1_18$J3f6+88igQXfBZXH0aMaqwa/go02DrtHvKHhGSYxCSJeTxBd4tcy2ONVnhF+jympRhjDKmxdkNThGSTTfn4FJ/lqW2OYcK0tPocGI6bsWX+mXuCqVsVLomaNoZaRVmlN5/7nL991ReRemG7OX6ejQKOVMJrgx3yp/NLai3OILSu32muJjzBzkk+EoXR95Q7FJ+ahGSBJhM8ZjOYO3okFyqXfI4nOwLQtuXf07Ea01Fu+4nk0T5dxloMM9/LNr1Cogz3SdjG4KpRjbM8sGdN+KWsZWH30dYHvtHqh8maX4CSLX7op+cLFVTbFIPVwbNyyeUmyPtVX3TwBCyB/uVvyjQ==$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"
        #     }

        data = {
            "encryptedData": encoded
        }

        Logger.info(f"{self.logIdentifier} Sending payment informations")
        try:
            r = self.session.put(
                url=paymentUrl,
                headers=headers,
                json=data)
            Logger.info(r.text)

        except Exception as e:
            Logger.error(f"{self.logIdentifier} Error while sending payment informations : {str(e)}")
            return -1

        if r.status_code != 200:
            Logger.error(f"{self.logIdentifier} Error sending payment informations : {r.status_code} / {r.text}")
            return -1

        Logger.info(f"{self.logIdentifier} Payment informations sent")

        self.paymentResponse = r.json()
        md = self.paymentResponse['md']
        pareq = self.paymentResponse['paReq']




if __name__ == '__main__':

    profile = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "loulouburner@gmail.com",
        "password": "Password69",
        "phone": "0781234567",
        "zipcode": "90210",
        "address1": "123 Main Street",
        "address2": "",
        "city": "Beverly Hills",
        "region": "California",
        "country_code": "FR",
        "size": "8",
        "card_number": "4785540018433001",
        "card_month": "08",
        "card_year": "2023",
        "card_cvc": "316",
    }

    raffle = {
        "metadata": {
            "productId": "a80d9056-1804-472c-b14f-d21aba9daf45"
        }
    }

    # EnterRaffleTask(index=1, taskNumber=2, profile=profile, raffle=raffle)
    # input()

    ADYEN_KEY = "10001|8677B0C92CA9D3FF33C345BD024EBC6235D2A79DEFFCE50F28F517447AECD7D95CD0663842CDB51D63E78AD86EDF4B4D569824B41B161E479909A4B141ED9C1CD7C492B81ECABD4D6984413D456BF4016C09E17283D436AEED0C85B0C9B745D9D19823123100A7D8E0EF8B32ED7191EC740F839D5C91C4A415F7750D1D69CC46DFA3E058007490133993E76C43B2D70B005A7BFA73DD66C652DAAC861B686C891B89B24C54F4F699D0770A2D53BFF29B60DBA42777C3A1C0ACCDA49CDF18382637DDE4123413FBEB897F3BD96B5467A3DB9606764979BCB6480BF497D0C75FFB719A4E54D0612982E0393B1A6BDF25546EE3D6443B9AEF5A1210A10AC2C26259"
    enc = encryptor(ADYEN_KEY)
    card = enc.encrypt_card(card='4143140003850207', cvv='561', month='03', year='2022')
    for elt in card:
        print(card[elt])

"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 11/09/2021 17:07:34                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from core.configuration.Configuration import Configuration
import random
import base64

from services.captcha import CaptchaHandler
from utilities import *

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy)
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
                ProxyManager().banProxy(self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )
            Logger.error(str(error))
            self.profile["status"] = "FAILED"
            self.success = False

    def getCaptcha(self):
        self.retryCaptcha = 0
        Logger.log(f"{self.logIdentifier} Solving Captcha...")

        captcha = CaptchaHandler().handleHCaptcha(
            '55c7c6e2-6898-49ff-9f97-10e6970a3cdb',
            self.raffle["metadata"]["entryUrl"],
            pollingInterval=3
        )

        if captcha["success"]:
            Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            return captcha["code"]
        else:
            self.retryCaptcha += 1
            Logger.warning(
                f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)"
            )
            Logger.error(f"{self.logIdentifier} {captcha['error']}")

            if self.retryCaptcha <= 3:
                return self.getCaptcha()
            else:
                return None

    def executeTask(self):

        url = 'https://releases.JuiceStore.com/api/raffles/{}'.format(self.raffle["metadata"]["raffleId"])

        headers = {
            'authority': 'releases.JuiceStore.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.77 Safari/537.36",
            'sec-gpc': '1',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
        }

        Logger.info(f"{self.logIdentifier} Getting sizes")
        try:
            get = self.session.get(url, headers=headers)
        except Exception as e:
            self.retry += 1
            Logger.error("Error while getting sizes : {}".format(str(e)))
            if self.retry < self.maxRetry:
                return self.executeTask()
            else:
                return -1
        if get.status_code != 200:
            Logger.error("Access denied while getting sizes : {}".format(get.status_code))
            if self.retry < self.maxRetry:
                return self.executeTask()
            else:
                return -1

        try:

            size_you_want = "notfound"
            gender = "notfound"

            size_you_want_unisex = get.json()["sizeSets"]["Unisex"]["sizes"]
            size_you_want_men = get.json()["sizeSets"]["Men"]["sizes"]
            size_you_want_women = get.json()["sizeSets"]["Women"]["sizes"]

            if len(size_you_want_unisex) != 0:
                size_you_want = size_you_want_unisex[0]["id"]
                gender = "Unisex"
            elif len(size_you_want_men) != 0:
                size_you_want = size_you_want_men[0]["id"]
                gender = "Men"
            elif len(size_you_want_women) != 0:
                size_you_want = size_you_want_women[0]["id"]
                gender = "Women"

            if size_you_want == "notfound":
                Logger.error(f"{self.logIdentifier} Error while getting sizes informations")
                return -1

        except Exception as e:
            Logger.error(f"{self.logIdentifier}" + "Error while getting sizeID : {}".format(str(e)))
            return -1

        Logger.success("Variant found : {} / {}".format(size_you_want, gender))

        self.raffle_code = self.raffle["metadata"]["raffleId"]
        referrer = 'https://releases.JuiceStore.com/register/{}/{}/'.format(self.raffle_code, gender) + size_you_want

        sess_headers = {
            'authority': 'releases.JuiceStore.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'sec-gpc': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': referrer,
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        Logger.info("Selecting size...")
        try:
            Size_Id_Get = self.session.get('https://releases.JuiceStore.com/api/raffles/{}'.format(self.raffle_code),
                                           headers=sess_headers)
        except Exception as e:
            Logger.error("Error while selecting size : {}".format(str(e)))
            return -1
        if Size_Id_Get.status_code != 200:
            Logger.error("Error while selecting size, code : {} / response : {}".format(Size_Id_Get.status_code, Size_Id_Get.text))
            return -1

        id_ = Size_Id_Get.json()
        sizeID_list = id_.get('sizeSets')[gender]['sizes']
        if self.profile["size"].lower() == "random":
            elt = random.choice(sizeID_list)
            sizeID = elt["id"]
        else:
            for elt in sizeID_list:
                if elt["eur"] == self.profile["size"]:
                    sizeID = elt["id"]
            try:
                sizeID == 'random'
            except:
                Logger.error("Size not found, getting random one")
                elt = random.choice(sizeID_list)
                sizeID = elt["id"]

        headers = {
            'authority': 'releases.JuiceStore.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'sec-gpc': '1',
            'origin': 'https://releases.JuiceStore.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': referrer,
            'accept-language': 'en-US;q=0.8,en;q=0.7',
        }

        data = {
            "email": self.profile["email"],
            "phone": self.profile["phone"],
            "id": None}

        Logger.info("Checking for duplicity entry")
        try:
            r = self.session.post(
                'https://releases.JuiceStore.com/api/registrations/check-duplicity/{}'.format(self.raffle_code),
                headers=headers, json=data)
        except Exception as e:
            Logger.error("Error while checking for duplicity : {}".format(str(e)))
            return -1
        if r.status_code != 200:
            Logger.error("Details already submitted")
            return -1

        self.captcha = self.getCaptcha()
        if self.captcha is None:
            Logger.error("Unvalid captcha token received, stopping task")
            return -1

        new_create_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHT'
                          'ML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://releases.JuiceStore.com',
            'Connection': 'keep-alive',
            'Referer': 'https://releases.JuiceStore.com/register/{}/{}/{}'.format(self.raffle_code, gender, sizeID)
        }

        create_data = {
            "id": None,
            "sizerunId": sizeID,
            "account": "New Customer",
            "email": self.profile["email"],
            "phone": self.profile["phone"],
            "gender": "Mr",
            "firstName": self.profile["first_name"],
            "lastName": self.profile["last_name"],
            "instagramUsername": self.profile["instagram"],
            "birthday": "{}-{}-{}".format(str(random.randint(1980, 2000)), str(random.randint(1, 10)),
                                          str(random.randint(1, 10))),
            "deliveryAddress": {
                "country": self.profile["country_code"],
                "state": self.profile["state"],
                "county": '',
                "city": self.profile["city"],
                "street": self.profile["street"],
                "houseNumber": self.profile["house_number"],
                "additional": self.profile["additional"],
                "postalCode": self.profile["zip"]
            },
            "consents": [
                "privacy-policy-101"
            ],
            "verification": {
                "token": self.captcha
            }
        }

        Logger.info("Creating entry")
        try:
            r = self.session.post('https://releases.JuiceStore.com/api/registrations/create/{}'.format(self.raffle_code),
                                  headers=new_create_headers,
                                  json=create_data)
        except Exception as e:
            Logger.error("Error while creating entry : {}".format(str(e)))
            return -1
        if r.status_code != 200:
            Logger.error("Access denied while creating entry : {}".format(r.status_code))
            return -1

        get_registrationID = r.json()
        registration_id = get_registrationID.get('registration')['id']

        from py_adyen_encrypt import encryptor

        ADYEN_KEY = "10001|A05EE5BCE99CA6C29B937BF6A5F0392A586C53EEEF3E4F848ACB086D35F54E38B99BAF63C2" \
                    "97689D09E533E6B3F2606608492B618D9219F47C7B7D97A56EFC9E5F118AB5257BD57DFB09A7A22DC" \
                    "A4C9BD17BDD22871A903FAA840F7897A2036E02CB3956C6CAE6B712C3E0A83BCD42A9B4E4008D17793" \
                    "5901C853E6A4F8705DF3F6D3A3C350C5A488B5C931C96C021959BF9317E642D96724744238A4F8EB8F5" \
                    "304BC05789C5942490FB7DD851C740A1310058304ADE2265B014196F871FD3DDADF0E4C4C698EE217A16" \
                    "BC6CC9308D23E21A9C98764F0F37874F29FD6EEA7FAA3DADB18DD8D7C48E6E91E126BA378129AFC2FD5C6" \
                    "06AF03110183D24080BD603"

        enc = encryptor(adyen_public_key=ADYEN_KEY, adyen_version='_0_1_25')
        card = enc.encrypt_card(card=self.profile["cc_number"], cvv=self.profile["cc_cvv"],
                                month=self.profile["cc_month"], year=self.profile["cc_year"])

        clientDataToEncode = {
            "version": "1.0.0",
            "deviceFingerprint": "GHHctdIkbA0040eqswEtLkIt16002YD2r1evOdfkj0000009Qp8Z9KINHDGiMVSwn2S:40",
            "persistentCookie": []}

        clientDataToEncode = {
            "version": "1.0.0",
            "persistentCookie": []
        }

        message = str(clientDataToEncode)
        message_bytes = message.encode('ascii')
        clientData = base64.b64encode(message_bytes).decode('utf-8')

        data = {
            "riskData": {
                "clientData": "eyJ2ZXJzaW9uIjoiMS4wLjAiLCJwZXJzaXN0ZW50Q29va2llIjpbXX0="
            },
            "paymentMethod": {
                "type": "scheme",
                "holderName": self.profile["first_name"] + " " + self.profile["last_name"],
                "encryptedExpiryMonth": card["month"],
                "encryptedExpiryYear": card["year"],
                "encryptedCardNumber": card["card"],
                "encryptedSecurityCode": card["cvv"],
                "brand": self.profile["cc_type"]
            },
            "browserInfo": {
                "acceptHeader": "*/*",
                "colorDepth": 30,
                "language": "fr-FR",
                "javaEnabled": False,
                "screenHeight": 900,
                "screenWidth": 1440,
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/92"
                             ".0.4515.107 Safari/537.36",
                "timeZoneOffset": -120
            },
            "clientStateDataIndicator": True
        }

        Logger.info("Submitting payment details")
        try:
            response = self.session.post('https://releases.JuiceStore.com/api/payment/make/{}'.format(registration_id),
                                         headers=headers,
                                         json=data)
        except Exception as e:
            Logger.error("Error while submitting payment details : {}".format(str(e)))
            return -1

        if response.status_code != 200:
            Logger.error("Error while submitting payment details,\n Status code : {},\nResponse : {}".format(response.status_code, response.text))
            return -1

        r_json = response.json()
        Logger.debug(r_json)

        try:  ## DETECTS 3DS CHALLENGE
            ThreeDsInfo = r_json['paymentDetail']["action"]["data"]
            print(ThreeDsInfo)
            MD = ThreeDsInfo["MD"]
            Pareq = ThreeDsInfo["Creq"]
            TermUrl = ThreeDsInfo["TermUrl"]

            params = {
                "MD": MD,
                "Pareq": Pareq
            }

            Logger.info("3DS Challenge detected, opening browser...")
            import selenium.webdriver as webdriver
            path = os.getcwd()
            driver = webdriver.Chrome(executable_path=path + "/chromedriver")
            self.post(driver=driver, path=TermUrl, params=data)
            Logger.info("3DS is waiting for you on the browser !")
            return 1

        except KeyError:  ## 3DS URL NOT FOUND
            Logger.info("No 3DS Challenge detected")
            return 1

        except Exception as e:
            Logger.error("Error occurred while opening the browser to solve the 3DS : " + str(e))
            return -1

    def post(self, driver, path, params):
        """
        :param driver: your driver object
        :param path: url path to post request
        :param params: request payload
        """

        driver.execute_script("""
        function post(path, params, method='post') {
            const form = document.createElement('form');
            form.method = method;
            form.action = path;
            for (const key in params) {
                if (params.hasOwnProperty(key)) {
                const hiddenField = document.createElement('input');
                hiddenField.type = 'hidden';
                hiddenField.name = key;
                hiddenField.value = params[key];
                form.appendChild(hiddenField);
            }
          }
          document.body.appendChild(form);
          form.submit();
        }
        post(arguments[1], arguments[0]);
        """, params, path)
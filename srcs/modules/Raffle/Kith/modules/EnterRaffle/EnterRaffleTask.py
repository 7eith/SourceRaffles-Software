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
from utilities import *
import json
import random
from requests.exceptions import ProxyError
import uuid
from http.cookies import SimpleCookie


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
        self.taskNumber: int = taskNumber
        self.profile: dict = profile
        self.raffle: dict = raffle

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.proxyLess = False

        """ Utilities """
        self.profile["Product"] = raffle["product"]
        self.initSession()

        try:

            status = self.executeTask()

            if status == 1:
                self.success = True
                self.profile["status"] = "SUCCESS"
                Logger.success(f"{self.logIdentifier} Successfully entered raffle!")
            else:
                self.success = False
                self.profile['status'] = "FAILED"
                
            if not self.proxyLess:
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def executeTask(self):

        self.session.headers.update({'User-Agent': 'KithApp/2002252216 CFNetwork/1209 Darwin/20.2.0'})
        user_agent = self.session.headers["User-Agent"]

        deviceID = str(uuid.uuid4()).upper()

        sessURL = 'https://ms-api.sivasdescalzo.com/api/locales'

        sessHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.3',
            'app-version': '2.1.0',
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': user_agent,
            'bundle-version': '28',
            'Connection': 'keep-alive'
        }

        Logger.info("Getting main page")
        try:
            r = self.session.get(sessURL, headers=sessHeaders)
            if r.status_code != 200:
                Logger.error("Error while accessing main page : {}".format(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task.")
            return -1
        except Exception as e:
            Logger.error("Error while getting main page : {}".format(str(e)))
            return -1

        loginURL = 'https://ms-api.sivasdescalzo.com/api/login'

        loginHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.3',
            'app-version': '2.1.1',
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': user_agent,
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }

        loginData = {
            "username": self.profile["email"],
            "password": self.profile["password"],
            "customer_agree": "true"
        }

        Logger.info("Login into account")
        try:
            r = self.session.post(loginURL, headers=loginHeaders, json=loginData)
            if r.status_code != 200:
                Logger.error("Error while login into account : code {} / response : {}.".format(r.status_code, r.text))
                try:
                    Logger.error("Error : {}".format(r.json()["message"]))
                except:
                    Logger.error("Error : {}".format(r.json()))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task.")
            return -1
        except Exception as e:
            Logger.error("Error while login into account : {}".format(str(e)))
            return -1

        data = r.json()

        token = data.get("customer_data")["token"]
        deviceID = data.get("customer_data")["device_id"]
        appDeviceIos = data.get("app_device_os")
        appVersion = data.get("app_version")

        addressInfo = data.get("customer_data")["address_data"]
        addressInfo = addressInfo[0]

        fname = addressInfo["firstname"]
        lname = addressInfo["lastname"]
        street = addressInfo["street"]
        city = addressInfo["city"]
        region = addressInfo["region"]
        region_id = addressInfo["region_id"]
        zipcode = addressInfo["postcode"]
        country_id = addressInfo["country_id"]
        phone = addressInfo["telephone"]

        updatedHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': appDeviceIos,
            'Authorization': 'Bearer ' + token,
            'app-version': appVersion,
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': user_agent,
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }

        Logger.info("Getting accounts details")
        try:
            r = self.session.get('https://ms-api.sivasdescalzo.com/api/customers', headers=updatedHeaders)
            if r.status_code != 200:
                Logger.error("Error while getting accounts details : {}".format(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task.")
            return -1
        except Exception as e:
            Logger.error("Error while getting accounts details : {}".format(str(e)))
            return -1

        try:
            Logger.info("Creating cart")
            r = self.session.post('https://ms-api.sivasdescalzo.com/api/carts/create', headers=updatedHeaders)
            if r.status_code != 200:
                Logger.error("Error while getting carting, code : {}".format(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while carting : {}".format(str(e)))
            return -1

        estimate_shippingData = {
            "address": {
                "city": city,
                "country_id": country_id,
                "firstname": fname,
                "lastname": lname,
                "postcode": zipcode,
                "region": region,
                "region_id": region_id,
                "street": [f"{street}"],
                "telephone": phone,
                "custom_attributes": {}
            }
        }

        try:
            Logger.info("Getting shipping rates")
            r = self.session.post('https://ms-api.sivasdescalzo.com/api/raffles/{}/'
                                  'estimate-shipping'.format(self.raffleId),
                                  headers=updatedHeaders,
                                  json=estimate_shippingData)
            if r.status_code != 200:
                Logger.error("Error while getting shipping rates, code : {}".format(r.status_code))
                return -1
            else:
                matrixrate = r.json()[0]["method_code"]
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting shipping rates : {}".format(str(e)))
            return -1

        headers = {
            'Accept': 'application/json',
            'device-os': appDeviceIos,
            'app-version': appVersion,
            'Accept-Language': 'fr-fr',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'store-code': 'en',
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
            'bundle-version': '28',
        }

        Logger.info("Selecting size...")
        try:
            r = self.session.get('https://ms-api.sivasdescalzo.com/api/itemDetail/{}'.format(self.raffleId),
                                 headers=headers)
            if r.status_code != 200:
                Logger.error("Error while getting sizes, code : {}".format(r.status_code))
                return -1
            else:
                t = r.json()["product_data"]["options"]
                sizes_list = t[0]["sizes"]

                if self.profile["size"].lower() == "random":
                    size_info = random.choice(sizes_list)
                    productId = size_info["product_id"]
                    optionId = size_info["option_value_id"]

                else:
                    productId = "notfound"
                    optionId = "notfound"
                    for size in sizes_list:
                        if size["size"][0]["value"] == self.profile["size"]:
                            productId = size["product_id"]
                            optionId = size["option_value_id"]
                            Logger.info("Size found : {}".format(productId))
                            Logger.info("Option found : {}".format(optionId))
                    if productId == "notfound":
                        Logger.info("Size not found, taking random one")
                        size_info = random.choice(sizes_list)
                        productId = size_info["product_id"]
                        optionId = size_info["option_value_id"]
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting sizes : {}".format(str(e)))
            return -1

        Logger.info("Getting payment token")
        try:
            r = self.session.get('https://ms-api.sivasdescalzo.com/api/carts/payments/token', headers=updatedHeaders)
            rawdata = r.headers["Set-Cookie"]
            cookie = SimpleCookie()
            cookie.load(rawdata)
            self.session.cookies.update(cookie)
            if r.status_code != 200:
                Logger.error("Error while getting payment informations, code : {}".format(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting payment informations : {}".format(str(e)))
            return -1

        data = r.json()
        Token = data["token"]
        import base64
        token_decoded = base64.b64decode(Token).decode('utf-8')
        auth_token = json.loads(token_decoded)['authorizationFingerprint']

        headersPaymentAuth = {
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'User-Agent': 'Braintree/iOS/4.31.0',
        }

        paramsPaymentAuth = (
            ('configVersion', '3'),
            ('authorization_fingerprint', auth_token),
        )

        Logger.info("Getting payment authorization")
        try:
            configRequest = self.session.get(
                'https://api.braintreegateway.com/merchants/7rgb8j8vb5f4hdwg/client_api/v1/configuration',
                headers=headersPaymentAuth,
                params=paramsPaymentAuth)
            if r.status_code != 200:
                Logger.error("Error while submitting payment, code : {} / response : {}".
                              format(configRequest.status_code, configRequest.text))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while submitting payment : {}".format(str(e)))
            return -1

        braintreeSetupURL = 'https://api.braintreegateway.com/merchants/7rgb8j8vb5f4hdwg/client_api/v1/paypal_hermes/' \
                            'setup_billing_agreement'

        headersPaypalLink = {
            "Host": "api.braintreegateway.com:443",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "User-Agent": "Braintree/iOS/4.31.0",
            "Accept-Language": "en-DE",
            "Accept-Encoding": "gzip, deflate, br"
        }

        dataPaypalLink = {
            "authorization_fingerprint": auth_token,
            "experience_profile": {
                "brand_name": "Kith - sivasdescalzo",
                "no_shipping": 1,
                "address_override": False
            },
            "_meta": {
                "iosIdentifierForVendor": str(uuid.uuid4()).upper(),
                "source": "paypal-browser",
                "iosDeviceName": "{} Iphone".format(fname),
                "merchantAppName": "KithApp",
                "integration": "dropin2",
                "deviceAppGeneratedPersistentUuid": str(uuid.uuid4()).upper(),
                "merchantAppVersion": "2002252222",
                "iosIsCocoapods": True,
                "sessionId": token.upper(),
                "iosSystemName": "iOS",
                "merchantAppId": "com.sivasdescalzo.Kith-app",
                "platform": "iOS",
                "isSimulator": False,
                "iosDeploymentTarget": "130000",
                "sdkVersion": "4.31.0",
                "deviceManufacturer": "Apple",
                "deviceModel": "iPhone12,3",
                "deviceScreenOrientation": "Portrait",
                "venmoInstalled": False,
                "dropinVersion": "7.5.0",
                "iosBaseSDK": "140500",
                "platformVersion": "14.3"
            },
            "cancel_url": "com.sivasdescalzo.Kith-app.payments://onetouch/v1/cancel",
            "offer_paypal_credit": False,
            "return -1_url": "com.sivasdescalzo.Kith-app.payments://onetouch/v1/success"
        }
        try:
            r = self.session.post(braintreeSetupURL, headers=headersPaypalLink, json=dataPaypalLink)
            if r.status_code != 201:
                Logger.error(
                    "Error while getting paypal link, code : {} / response : {}".format(r.status_code, r.text))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1

        temp = r.json()
        url = temp["agreementSetup"]["approvalUrl"]
        BA_token = temp["agreementSetup"]["tokenId"]
        Logger.info("Paypal payment url found : {}".format(url))
        Logger.info("Opening browser")

        from seleniumwire import webdriver
        from selenium.webdriver.chrome.options import Options
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"}
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        driver = webdriver.Chrome(options=chrome_options, executable_path=os.getcwd() + "/chromedriver")

        driver.get("https://www.paypal.com/login")
        Logger.info("login and press enter")
        input()
        driver.get(url)
        for request in driver.requests:
            try:
                response = request.response
                from seleniumwire.utils import decode
                body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                PaymentToken = "not found"
            except:
                pass

        headersFinal = {
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.6',
            'Authorization': 'Bearer {}'.format(token),
            'app-version': '2.1.1',
            'device-id': deviceID,
            'Accept-Language': 'fr-fr',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': 'KithApp/2002252222 CFNetwork/1240.0.4 Darwin/20.5.0',
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }
        dataFinal = {
            "participation": {
                "product_id": productId,
                "size_group": "eu",
                "store_group_id": 1,
                "product_option_id": optionId,
                "shipping_method": matrixrate,
                "payment_data": PaymentToken,  ## coming from paypal ?
                "shipping_firstname": fname,
                "shipping_lastname": lname,
                "shipping_street": street,
                "shipping_postcode": zipcode,
                "shipping_country_id": country_id,
                "shipping_region_id": region_id,
                "shipping_region": region,
                "shipping_city": city,
                "shipping_telephone": phone,
                "billing_firstname": fname,
                "billing_lastname": lname,
                "billing_street": street,
                "billing_postcode": zipcode,
                "billing_country_id": country_id,
                "billing_region_id": region_id,
                "billing_region": region,
                "billing_city": city,
                "billing_telephone": phone
            }
        }
        try:
            response = self.session.post('https://ms-api.sivasdescalzo.com/api/raffles/{}'.format(self.raffleId),
                                         headers=headersFinal,
                                         json=dataFinal)
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1
        except ProxyError:
            Logger.error("Proxy Error")
            return -1

        if response.status_code == 200:
            return 1
        else:
            Logger.error("Error while submitting entry : \nStatus code : {} \nResponse".format(response.status_code,
                                                                                                response.text))
            return -1

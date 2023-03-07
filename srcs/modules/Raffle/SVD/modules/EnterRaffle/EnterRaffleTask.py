import sys
import os
import json

import requests
import time
import random
import base64

try:
    from utilities import *
    import uuid
    from requests.exceptions import ProxyError
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
except ImportError as e:
    print(f"Error importing library: {e}")
    time.sleep(5)
    sys.exit(1)


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
        self.proxyLess = False

        """ Utilities """

        self.initSession()

        try:

            status = self.start()

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

    def initSession(self):

        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

        self.session.headers.update({
            "device-id": '%016x' % random.randrange(16 ** 16),
            "store-code": "en",
            "app-version": "2.1.0",
            "bundle-version": "22",
            "device-os": "A-Android 10.0",
            "user-agent": "okhttp/3.12.1"
        })

    def mainpage(self):
        sessURL = 'https://ms-api.sivasdescalzo.com/api/locales'

        while True:
            try:
                response = self.session.get(url=sessURL)
                Logger.info("Accessed main page")
                return True
            except Exception as e:
                Logger.error(f'Error loading site: {e}')
                time.sleep(5)
                continue

    def login(self):
        loginURL = 'https://ms-api.sivasdescalzo.com/api/login'

        loginData = {
            "username": self.profile["email"],
            "password": self.profile["password"],
            "customer_agree": "true"
        }
        while True:
            try:
                Logger.info("Logging in...")
                response = self.session.post(
                    loginURL, json=loginData)
                self.loggedInResponse = response.json()
            except Exception as e:
                Logger.error(f"Error logging in: {e}")
                time.sleep(5)
                continue

            if response.status_code not in (400, 403, 404):
                self.account_info = response.json()
                self.session.headers.update(
                    {"Authorization": f"Bearer {response.json()['customer_data']['token']}"})
                Logger.info(f"Succesfully logged in {self.profile['email']}")
                return True
            else:
                Logger.error(f"Error logging in: {response.status_code}")
                time.sleep(10)
                continue

    def create_cart(self):

        token = self.loggedInResponse.get("customer_data")["token"]
        deviceID = self.loggedInResponse.get("customer_data")["device_id"]
        appDeviceIos = self.loggedInResponse.get("app_device_os")
        appVersion = self.loggedInResponse.get("app_version")

        self.updated_headers = {
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
            'User-Agent': self.session.headers["User-Agent"],
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }

        while True:
            try:
                response = self.session.post(
                    url='https://ms-api.sivasdescalzo.com/api/carts/create', headers=self.updated_headers)
            except ProxyError:
                Logger.error(f'Proxy error occurred when getting cart, retrying')
                time.sleep(5)
                continue
            except Exception as e:
                Logger.error(f'Error creating cart: {e}')
                time.sleep(5)
                continue

            if response.status_code in (200, 201, 302, 303, 304):
                Logger.info(f'Successfully created cart')
                return response
            else:
                Logger.error(f'Error creating cart: {response.status_code}')
                time.sleep(5)
                continue

    def get_shipping_rates(self):
        data = self.account_info
        try:
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
        except Exception as e:
            Logger.error(f"Error getting details : {e}")
            time.sleep(10)
            return True

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

        while True:
            try:
                response = self.session.post('https://ms-api.sivasdescalzo.com/api/raffles/{}/'
                                             'estimate-shipping'.format(
                                                 self.raffle["metadata"]["raffleId"]),
                                             json=estimate_shippingData)
            except ProxyError:
                Logger.error(f"Proxy error when getting rates, retrying")
                time.sleep(5)
                continue
            except Exception as e:
                Logger.error(f"Error getting rates: {e}")
                time.sleep(5)
                continue

            if response.status_code in (200, 201, 302, 303, 304):
                matrixrate = None
                try:
                    matrixrate = response.json()[0]["method_code"]
                except Exception as e:
                    Logger.error(f"Error getting rate: {e}")
                    time.sleep(5)
                    continue

                if matrixrate is not None:
                    Logger.info(f"Successfully retrieved rate")
                    self.matrixrate = matrixrate
                    return False
            else:
                Logger.error(f"Error getting rate: {response.status_code}")
                time.sleep(5)
                continue

    def select_size(self):
        Logger.info("Selecting size...")
        try:
            response = self.session.get(
                url='https://ms-api.sivasdescalzo.com/api/itemDetail/{}'.format(self.raffle["metadata"]["raffleId"]))
        except ProxyError:
            Logger.error(f'Proxyerror while getting sizes, retrying')
            return -1
        except Exception as e:
            Logger.error(f'Exception while getting sizes: {e}')
            return -1
        if response.status_code != 200:
            Logger.error(f'Error getting sizes: {response.status_code}')
            return -1
        else:
            t = response.json()["product_data"]["options"]
            sizes_list = t[0]["sizes"]

            if self.profile["size"].lower() == "random":
                size_info = random.choice(sizes_list)
                self.productId = size_info["product_id"]
                self.optionId = size_info["option_value_id"]
                Logger.info("Size found : {}".format(self.productId))
                Logger.info("Option found : {}".format(self.optionId))
                return 1

            else:
                productId = None
                optionId = None
                for size in sizes_list:
                    if size["size"][0]["value"] == self.profile["size"]:
                        productId = size["product_id"]
                        optionId = size["option_value_id"]
                        self.productId = productId
                        self.optionId = optionId
                        Logger.info("Size found : {}".format(productId))
                        Logger.info("Option found : {}".format(optionId))
                        return 1
                if productId is None:
                    Logger.error("Size not found, taking random one")
                    size_info = random.choice(sizes_list)
                    productId = size_info["product_id"]
                    optionId = size_info["option_value_id"]
                    self.productId = productId
                    self.optionId = optionId
                    Logger.info("Size found : {}".format(productId))
                    Logger.info("Option found : {}".format(optionId))
                    return 1

    def paypal_token(self):
        url = "https://ms-api.sivasdescalzo.com/api/carts/payments/token"

        while True:
            try:
                get_token_res = self.session.get(
                    "https://ms-api.sivasdescalzo.com/api/carts/payments/token")
                if get_token_res.status_code == 200:
                    self.decoded_token = json.loads(base64.b64decode(
                        get_token_res.json()['token']).decode("utf-8"))
                    Logger.info(f'Successfully got payment token')
                    return True
                else:
                    Logger.error(f'Error getting token: {get_token_res.status_code}')
                    time.sleep(5)
                    continue
            except Exception as e:
                Logger.error(f'Error getting token: {e}')
                time.sleep(5)
                continue

    def invoice_data(self):
        braintree_get_invoice_data = {
            "return_url": "com.sivasdescalzo.svdapp.braintree://onetouch/v1/success",
            "cancel_url": "com.sivasdescalzo.svdapp.braintree://onetouch/v1/cancel",
            "offer_paypal_credit": False,
            "authorization_fingerprint": self.decoded_token['authorizationFingerprint'],
            "experience_profile":
                {
                    "no_shipping": True,
                    "brand_name": "SVD - sivasdescalzo",
                    "address_override": False
            },
            "authorizationFingerprint": self.decoded_token['authorizationFingerprint']
        }

        while True:
            try:
                response = self.session.post(f"https://api.braintreegateway.com/merchants/{self.decoded_token['merchantId']}/client_api/v1/paypal_hermes/setup_billing_agreement",
                                             json=braintree_get_invoice_data,
                                             headers={
                                                 "user-agent": "braintree/android/3.11.1"}
                                             )
            except ProxyError:
                Logger.error(f'Proxy error when submitting payment token')
                time.sleep(5)
                continue
            except Exception as e:
                Logger.error(f'Error when submitting payment token: {e}')
                time.sleep(5)
                continue
            if response.status_code != 201:
                Logger.error(f'Error getting payment token: {response.status_code}')
                time.sleep(5)
                continue

            else:
                if self.open_browser(response.json()):
                    return True
                else:
                    return False

    def open_browser(self, data):
        url = data['agreementSetup']['approvalUrl']
        options = uc.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        if platform.system() == "Windows":
            driverPath = os.getcwd() + "\\resources\\chromedriver.exe"
        elif platform.system() == "Linux":
            driverPath = os.getcwd() + "/resources/chromedriver"
        elif platform.system() == "Darwin":
            driverPath = os.getcwd() + "/resources/chromedriver"
        else:
            Logger.error("Unsupported OS")
            return False

        try:
            driver = uc.Chrome(options=options, executable_path=driverPath)
        except Exception as e:
            Logger.error("Could not start ChromeDriver : " + str(e))
            return False
        driver.get(url)

        try:
            driver.execute_script(
                f"window.document.getElementsByName('login_email')[0].value = '{self.profile['email']}';")
        except Exception:
            pass

        Logger.info(
            f'Authorization for paypal is now started. Please confirm within a few minutes.')

        paypal_invoice_token = None
        paypal_invoice_ba_token = None

        for i in range(3000):
            if len(driver.find_elements(by=By.ID, value="consentButton")) == 1:
                try:
                    driver.execute_script("""
                        (function(send) {
                            XMLHttpRequest.prototype.send = function(data) {
                                json_data = JSON.parse(data);
                                if (json_data['events'] != undefined) {
                                    json_data['events'].forEach(function(event, index) {
                                        if (event['event'] == 'redirect') {
                                            if (event['payload']['url'].includes("com.sivasdescalzo.svdapp.braintree://onetouch/v1/success")) {
                                                console.log('found success: '+ event['payload']['url']);
                                                var app_redirect_url = new URL(event['payload']['url']);
                                                var new_url = new URL("about:blank" + app_redirect_url.search);
                                                window.location = new_url.href;
                                            }
                                        }
                                    });
                                }
                                send.call(this, data);
                            };
                        })(XMLHttpRequest.prototype.send);
                    """)
                except Exception as exc:
                    Logger.error('Error loading browser : {}'.format(str(exc)))
                break
            else:
                time.sleep(0.5)
        for i in range(300):
            if driver.current_url.startswith("about:blank?token"):
                driver.execute_script("""
                    document.write("<h1>Successfully authorized Paypal");
                    var url = new window.URL(window.location.href);
                    window.token = url.searchParams.get("token");
                    window.ba_token = url.searchParams.get("ba_token");"""
                                      )

                paypal_invoice_token = driver.execute_script(
                    "return window.token")
                paypal_invoice_ba_token = driver.execute_script(
                    "return window.ba_token")
                time.sleep(3)
                driver.close()
                break
            else:
                time.sleep(1)

        if paypal_invoice_token is None:
            driver.close()
            Logger.error(f'Failed getting paypal token, please try again')
            return False

        else:
            self.paypal_invoice_token = paypal_invoice_token
            self.paypal_invoice_ba_token = paypal_invoice_ba_token
            return True

    def braintree_post(self):
        braintree_session_id = '%027x' % random.randrange(27 ** 27)
        data = {
            "_meta":
            {
                "platform": "android",
                "sessionId": braintree_session_id,
                "source": "paypal-browser",
                "integration": "custom"
            },
            "paypalAccount":
            {
                "correlationId": self.paypal_invoice_ba_token,
                "intent": "authorize",
                "client":
                {},
                "response":
                {
                    "webURL": f"com.sivasdescalzo.svdapp.braintree://onetouch/v1/success?token={self.paypal_invoice_token}&ba_token={self.paypal_invoice_ba_token}"
                },
                "response_type": "web"
            },
            "authorizationFingerprint": self.decoded_token['authorizationFingerprint']
        }

        while True:
            try:
                response = self.session.post(f"https://api.braintreegateway.com/merchants/{self.decoded_token['merchantId']}/client_api/v1/payment_methods/paypal_accounts",
                                             json=data,
                                             headers={
                                                 "user-agent": "braintree/android/3.11.1"}
                                             )
            except ProxyError:
                Logger.error(f'Proxyerror verifying payment token, retrying')
                time.sleep(5)
                continue
            except Exception as e:
                Logger.error(f'Error verifying payment token: {e}')
                time.sleep(5)
                continue

            if response.status_code not in [200, 201, 202]:
                Logger.error(f'Error verifying payment token: {response.status_code}')
                Logger.debug(response.text)
                time.sleep(5)
                continue
            else:
                Logger.info(f'Successfully verified payment token')
                self.verify_payment_token = response.json()[
                    "paypalAccounts"][0]["nonce"]
                return True

    def submit_entry(self):
        url = 'https://ms-api.sivasdescalzo.com/api/raffles/{}'.format(
            self.raffle["metadata"]["raffleId"])

        addressInfo = self.account_info.get("customer_data")["address_data"]
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

        data = {
            "participation": {
                "product_id": self.productId,
                "size_group": "eu",
                "store_group_id": 1,
                "product_option_id": self.optionId,
                "shipping_method": self.matrixrate,
                "payment_data": self.verify_payment_token,
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

        while True:
            try:
                response = self.session.post(url=url, json=data)
            except ProxyError:
                Logger.error(f'Proxyerror submitting entry, retry')
                return -1
            except Exception as e:
                Logger.error(f'Error submitting entry: {e}')
                return -1

            if response.status_code == 200:
                return 1
            else:
                Logger.error(f'Error submitting entry: {response.status_code}')
                Logger.debug(response.text)
                return -1

    def start(self):
        self.initSession()
        self.mainpage()
        self.login()
        self.create_cart()

        if self.get_shipping_rates():
            Logger.error(f'Profile/account error, closing task...')
            return False
        sizeResult = self.select_size()
        if sizeResult != 1:
            return -1
        self.paypal_token()

        if self.invoice_data():
            self.braintree_post()
            final = self.submit_entry()
            if final == 1:
                return 1
            else:
                return -1
        else:
            Logger.error(f'Payment error, closing task...')
            return False
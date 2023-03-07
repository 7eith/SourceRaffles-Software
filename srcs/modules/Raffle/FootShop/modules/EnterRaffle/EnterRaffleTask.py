try:
    import json
    from services.captcha import CaptchaHandler
    from utilities import *
    import uuid
    from .adyen_tools import bin_lookup
    from .adyen_tools import encrypt
    from .adyen_tools import gen_risk_data
    from .adyen_3ds_handler import handle_3ds
except ImportError as e:
    print(f"Error importing library: {e}")
    print(f"Exiting...")
    time.sleep(5)
    sys.exit(1)


class EnterRaffleTask:

    def findSizes(self):

        Logger.info(self.sizes)

        try:
            self.gender = "notfound"

            size_you_want_unisex = self.sizes["Unisex"]["sizes"]
            size_you_want_men = self.sizes["Men"]["sizes"]
            Logger.info(size_you_want_men)
            size_you_want_women = self.sizes["Women"]["sizes"]

            if len(size_you_want_unisex) != 0:
                self.gender = "Unisex"
                Logger.info("Gender found : {}".format(self.gender))
            elif len(size_you_want_men) != 0:
                self.gender = "Men"
                Logger.info("Gender found : {}".format(self.gender))
            elif len(size_you_want_women) != 0:
                self.gender = "Women"
                Logger.info("Gender found : {}".format(self.gender))

            else:
                Logger.error("Error, no stock loaded yet")
                return -1

            if self.gender == "notfound":
                Logger.error(f"{self.logIdentifier} Error while getting sizes informations : no gender found")
                return -1

        except Exception as e:
            Logger.error(f"{self.logIdentifier}" + "Error while getting sizeID : {}".format(str(e)))
            return -1

        self.sizeID = 'notfound'
        if self.profile["size"].lower() == "random":
            elt = random.choice(self.sizes[self.gender]['sizes'])
            self.sizeID = elt["id"]
        else:
            for elt in self.sizes[self.gender]['sizes']:
                if elt["eur"] == self.profile["size"]:
                    self.sizeID = elt["id"]
            if self.sizeID == 'notfound':
                Logger.error("Size not found, getting a random one")
                elt = random.choice(self.sizes[self.gender]['sizes'])
                self.sizeID = elt["id"]

        Logger.success("Variant found : {} / {}".format(self.sizeID, self.gender))
        return 1

    def initSession(self):

        self.session = requests.Session()

        ## TODO : add more user agents to the list
        self.session.headers[
            'user-agent'] = getRandomUserAgent()
        self.session.headers[
            'referer'] = f'https://releases.footshop.com/register/{self.raffle_id}/{self.gender}/{self.sizeID}'
        self.session.headers['origin'] = 'https://releases.footshop.com'

        self.session.cookies.set("sessionId", str(uuid.uuid4()))

        try:
            self.session.get(
                "https://releases.footshop.com/api/raffles/G0XAaXgBHBhvh4GFIw1W")
        except Exception as e:
            Logger.debug("Couldn't create session on footshop website (during session init) : {}".format(str(e)))

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy)
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

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

    def __init__(self, index, taskNumber, profile, raffle):

        self.raffle = raffle
        self.raffle_url = self.raffle["metadata"]["entryUrl"]
        self.raffle_id = self.raffle["metadata"]["raffleId"]
        self.sizes = self.raffle["metadata"]["sizes"]
        self.profile = profile

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
        self.captchaToken = None
        self.proxyLess = False

        try:

            findSizes = self.findSizes()

            if findSizes != 1:
                Logger.error("Error while getting sizes information")

            self.initSession()

            duplicate = self.check_duplicate_entry()

            if duplicate == 1:
                Logger.success("No duplicity entry found")

                response = self.submit_info()

                if self.submit_payment(response):
                    Logger.success(f'{self.profile["email"]} has successfully been submitted')
                    self.success = True
                    self.profile['status'] = "SUCCESS"
                else:
                    Logger.error(f'Failed submitting entry for: {self.profile["email"]}')
                    self.success = False
                    self.profile['status'] = "FAILED"
            else:
                self.success = False
                self.profile['status'] = "FAILED"

            if (not self.proxyLess):
                ProxyManager().banProxy(self.proxy)

        except Exception as e:
            Logger.error("Error while running task : {}".format(str(e)))
            self.success = False
            self.profile['status'] = "FAILED"

            if (not self.proxyLess):
                ProxyManager().banProxy(self.proxy)

    def check_duplicate_entry(self):
        while True:
            Logger.info("Checking for duplicate entry")
            try:
                check_duplicity = self.session.post(f"https://releases.footshop.com/api/registrations/check-duplicity/{self.raffle_id}", json={
                    "email": self.profile["email"], "phone": self.profile['phone'], "id": None})
            except Exception as e:
                Logger.error(f'Error checking duplicate entry: {e}')
                return -1
            if check_duplicity.status_code not in (400, 403, 404, 500, 502):

                if check_duplicity.json()['email']:
                    Logger.error(
                        f"Email {self.profile['email']} was already entered before.")
                    return -1
                elif check_duplicity.json()['phone']:
                    Logger.error(
                        f"Phone number {self.profile['phone']} was already entered before.")
                    return -1
                else:
                    Logger.info(f'No duplicated entry found, processing...')
                    return 1
            else:
                Logger.error(
                    f'Error checking duplicity with status: {check_duplicity.status_code}')
                return -1

    def submit_info(self):
        while True:

            captchaToken = self.getCaptcha()

            if captchaToken is None:
                Logger.error("Unvalid captcha token received")
                return -1

            data = {"id": None,
                    "sizerunId": self.sizeID,
                    "account": "New Customer",
                    "email": self.profile["email"],
                    "phone": self.profile["phone"],
                    "gender": "Mr",
                    "firstName": self.profile["first_name"],
                    "lastName": self.profile["last_name"],
                    "instagramUsername": self.profile["instagram"],
                    "birthday": f"{random.randint(1989, 2000)}-0{random.randint(0, 9)}-{random.randint(1, 28)}",
                    "deliveryAddress":
                        {
                            "country": self.profile["country_code"],
                            "state": "",
                            "county": "",
                            "city": self.profile["city"],
                            "street": self.profile["street"],
                            "houseNumber": self.profile["house_number"],
                            "additional": self.profile["house_number"],
                            "postalCode": self.profile["zip"]
                    },
                    "consents": ["privacy-policy-101"],
                    "verification": {"token": captchaToken}}

            try:
                start_reg_res = self.session.post(
                    f"https://releases.footshop.com/api/registrations/create/{self.raffle_id}", json=data)
            except Exception as e:
                Logger.error(f"Error submitting info: {e}")
                time.sleep(10)
                continue

            if start_reg_res.status_code != 200:
                if start_reg_res.status_code == 422:
                    Logger.error(
                        f"Couldn't process registration: {start_reg_res.json().get('errors')}")
                    time.sleep(10)
                    continue
                else:
                    Logger.error(
                        f"Couldn't create registration: {start_reg_res.json().get('errors')}")
                    time.sleep(10)
                    continue

            else:
                Logger.success(f"Submitted shipping successfully!")
                return start_reg_res.json()

    def submit_payment(self, json_response):
        adyen_encryptor = encrypt.Encryptor("10001|A05EE5BCE99CA6C29B937BF6A5F0392A586C53EEEF3E4F848ACB086D35F54E38B99BAF63C297689D09E533E6B3F2606608492B618D9219F47C7B7D97A56EFC9E5F118AB5257BD57DFB09A7A22DCA4C9BD17BDD22871A903FAA840F7897A2036E02CB3956C6CAE6B712C3E0A83BCD42A9B4E4008D177935901C853E6A4F8705DF3F6D3A3C350C5A488B5C931C96C021959BF9317E642D96724744238A4F8EB8F5304BC05789C5942490FB7DD851C740A1310058304ADE2265B014196F871FD3DDADF0E4C4C698EE217A16BC6CC9308D23E21A9C98764F0F37874F29FD6EEA7FAA3DADB18DD8D7C48E6E91E126BA378129AFC2FD5C606AF03110183D24080BD603")
        while True:
            try:
                cc_data = {
                    "riskData": gen_risk_data.gen_risk_data(),
                    "paymentMethod":
                    {
                        "type": "scheme",
                        "holderName": f"{self.profile['first_name']} {self.profile['last_name']}",
                        "encryptedCardNumber": adyen_encryptor.encrypt_card_data(number=self.profile["cc_number"]),
                        "encryptedExpiryMonth": adyen_encryptor.encrypt_card_data(expiry_month=self.profile["cc_month"]),
                        "encryptedExpiryYear": adyen_encryptor.encrypt_card_data(expiry_year=self.profile["cc_year"]),
                        "encryptedSecurityCode": adyen_encryptor.encrypt_card_data(cvc=self.profile["cc_cvv"]),
                        "brand": bin_lookup.get_card_brand(self.session, adyen_encryptor.encrypt_card_data(bin_value=self.profile["cc_number"][:6]), json_response['details']['paymentMethods']['paymentMethods'][0]['brands'], json_response['details']['clientKey'])
                    },
                    "browserInfo":
                    {
                        "acceptHeader": "*/*",
                        "colorDepth": 24,
                        "language": "en-US",
                        "javaEnabled": False,
                        "screenHeight": 1,
                        "screenWidth": 1,
                        "userAgent": self.session.headers['user-agent'],
                        "timeZoneOffset": -120
                    },
                    "clientStateDataIndicator": True
                }
            except Exception as e:
                Logger.error(f'Error encrypting card details: {e}')
                time.sleep(10)
                continue

            try:
                self.registration_id = json_response.get("id", False)
                if not self.registration_id:
                    self.registration_id = json_response.get(
                        "registration").get("id")

                response = self.session.post(
                    f"https://releases.footshop.com/api/payment/make/{self.registration_id}", json=cc_data)
            except Exception as e:
                Logger.error(f"Error completing the registration: {e}")
                time.sleep(10)
                continue

            if response.status_code not in (400, 403, 404, 500, 502):
                try:
                    card_response = response.json()
                except Exception:
                    Logger.error(
                        f'Error submitting card, status code: {response.status_code}')
                    time.sleep(10)
                    continue

                errors = card_response.get("errors", None)

                if errors is None:
                    card_response.get("errors", None)

                if errors is not None:
                    Logger.error(f'Error submitting card: {errors}')
                    time.sleep(10)
                    return False

                if card_response['registration']['noWin']:
                    Logger.error(f'Entry was filtred out...')
                    return False

                else:
                    if self.threeDS(response.json()):
                        return True
                    else:
                        return False
            else:
                Logger.error("Error while submitting card : {}".format(str(e)))
                return False

    def threeDS(self, json):
        try:
            payment_action = json['paymentDetail']['action']

            def redirect_hook(driver):
                threeds_confirmed = False
                for i in range(300):
                    if driver.current_url.startswith("https://releases.footshop.com/registration/finish"):
                        threeds_confirmed = True

                        time.sleep(1)
                        break
                    else:
                        time.sleep(1)

                return threeds_confirmed

            threeds_result = handle_3ds(payment_action, self.session, "live_Y44FYNDGDNFBNKSYXDDP4H2LBQKOU4N3",
                                        f"https://releases.footshop.com/api/payment/make/{self.registration_id}", redirect_hook)

            if threeds_result is not None:
                if not threeds_result.json()['registration']['authorized']:
                    Logger.error(f"Entry unauthorized with 3DS")
                    return False

        except Exception as exc:
            Logger.error(f"Couldn't confirm 3DS: {exc} (most likely soft ban)")
            Logger.debug(payment_action)
            return False

        return True


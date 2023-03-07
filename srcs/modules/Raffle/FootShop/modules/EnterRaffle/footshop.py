import time
import sys
import json
import re
import random
import requests

try:
    import uuid
    from twocaptcha import TwoCaptcha
    import adyen_tools.bin_lookup
    import adyen_tools.encrypt
    import adyen_tools.gen_risk_data
    from adyen_3ds_handler import handle_3ds
except ImportError as e:
    print(f"Error importing library: {e}")
    print(f"Exiting...")
    time.sleep(5)
    sys.exit(1)


class Footshop:
    def __init__(self, raffle_url, profile):

        # The raffle_url could also be declared as a global variable/constant
        # but you do not want too many global variables
        # if you don´t want the SIZES, ID etc as global
        # you can pass it as a parameter when call and declaring them inside this function instead

        self.raffle_url = raffle_url
        self.profile = profile

        try:
            # Making sure the inputted size get´s read correctly to avoid getting the application crashed incase there is some user-error
            # If you want to have random sizing it´s pretty easily implemented since the SIZES is a dict
            # You can do it as following:
            # ================================================================================================
            """ if self.profile.size.lower().strip() == 'random':
                self.sizes = SIZES[random.choice(list(SIZES))]

            else:
                self.sizes = SIZES[int(self.profile['size'])] """

            # ================================================================================================

            self.sizes = SIZES[int(self.profile['size'])]
        except KeyError as e:
            # This will give the user an heads-up incase they have inputted wrong sizing format

            print(f'Error finding size: {e}')
            time.sleep(5)
            return None

        # Calling the start function that will start the "task"
        self.start()

    def build_proxy(self):

        # I used this for testing since i didnt wanna build a entire proxy/client script for the sake of i guess you guys do already have files for that
        # So i´ll let this one sit here if you want it, make sure you pass in proxies as an argument when calling the class
        # Else you can simply just remove it, i have commentated it out from the createClient() function anyway :)

        self.proxy = None
        if self.proxies == [] or not self.proxies:
            return None
        self.px = random.choice(self.proxies)
        self.splitted = self.px.split(':')
        if len(self.splitted) == 2:
            self.proxy = 'http://{}'.format(self.px)
            return None

        elif len(self.splitted) == 4:
            self.proxy = 'http://{}:{}@{}:{}'.format(
                self.splitted[2], self.splitted[3], self.splitted[0], self.splitted[1])
            return None
        else:
            return None

    def createClient(self):

        session = requests.Session()

        # You do want it set to this specific user-agent to avoid filtering!
        # For some reason they seem to filter it out otherwise
        session.headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        session.headers['referer'] = f'https://releases.footshop.com/register/{RAFFLE_ID}/{self.sizes["size_set"]}/{self.sizes["id"]}'
        session.headers['origin'] = 'https://releases.footshop.com'

        # ========================================================================
        # This is how you can use this use the proxy function i made!

        # self.build_proxy()
        """ proxies = {
            'http': self.proxy,
            'https': self.proxy,
        }
        session.proxies.update(proxies) """

        # ==========================================================================

        session.cookies.set("sessionId", str(uuid.uuid4()))

        # This is just to make sure an session is created and started on the site
        try:
            session.get(
                "https://releases.footshop.com/api/raffles/G0XAaXgBHBhvh4GFIw1W")
        except Exception as e:
            pass

        self.session = session
        return session

    def check_duplicate_entry(self):
        while True:
            # Posting to their API to check so there is no duplicate entry
            try:
                check_duplicity = self.session.post(f"https://releases.footshop.com/api/registrations/check-duplicity/{RAFFLE_ID}", json={
                    "email": self.profile["email"], "phone": self.profile['phone'], "id": None})
            except Exception as e:
                print(f'Error checking duplicate entry: {e}')
                time.sleep(3)
                continue
            if check_duplicity.status_code not in (400, 403, 404, 500, 502):

                if check_duplicity.json()['email']:
                    print(
                        f"Email {self.profile['email']} was already entered before.")
                    return True
                elif check_duplicity.json()['phone']:
                    print(
                        f"Phone number {self.profile['phone']} was already entered before.")
                    return True
                else:
                    print(f'No duplicated entry found, processing...')
                    return False
            else:
                print(
                    f'Error checking duplicity with status: {check_duplicity.status_code}')
                time.sleep(3)
                continue

    def submit_info(self):
        while True:

            data = {"id": None,
                    "sizerunId": self.sizes['id'],
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
                    "verification": {"token": solve_captcha(self.raffle_url)}}

            try:
                start_reg_res = self.session.post(
                    f"https://releases.footshop.com/api/registrations/create/{RAFFLE_ID}", json=data)
            except Exception as e:
                print(f"Error submitting info: {e}")
                time.sleep(10)
                continue

            if start_reg_res.status_code != 200:
                if start_reg_res.status_code == 422:
                    print(
                        f"Couldn't process registration: {start_reg_res.json().get('errors')}")
                    time.sleep(10)
                    continue
                else:
                    print(
                        f"Couldn't create registration: {start_reg_res.json().get('errors')}")
                    time.sleep(10)
                    continue

            else:
                print(f"Submitted shipping successfully!")
                return start_reg_res.json()

    def submit_payment(self, json_response):
        adyen_encryptor = modules.Raffle.FootShop.modules.EnterRaffle.adyen_tools.encrypt.Encryptor("10001|A05EE5BCE99CA6C29B937BF6A5F0392A586C53EEEF3E4F848ACB086D35F54E38B99BAF63C297689D09E533E6B3F2606608492B618D9219F47C7B7D97A56EFC9E5F118AB5257BD57DFB09A7A22DCA4C9BD17BDD22871A903FAA840F7897A2036E02CB3956C6CAE6B712C3E0A83BCD42A9B4E4008D177935901C853E6A4F8705DF3F6D3A3C350C5A488B5C931C96C021959BF9317E642D96724744238A4F8EB8F5304BC05789C5942490FB7DD851C740A1310058304ADE2265B014196F871FD3DDADF0E4C4C698EE217A16BC6CC9308D23E21A9C98764F0F37874F29FD6EEA7FAA3DADB18DD8D7C48E6E91E126BA378129AFC2FD5C606AF03110183D24080BD603")
        while True:
            try:
                cc_data = {
                    "riskData": modules.Raffle.FootShop.modules.EnterRaffle.adyen_tools.gen_risk_data.gen_risk_data(),
                    "paymentMethod":
                    {
                        "type": "scheme",
                        "holderName": f"{self.profile['first_name']} {self.profile['last_name']}",
                        "encryptedCardNumber": adyen_encryptor.encrypt_card_data(number=self.profile["cc_number"]),
                        "encryptedExpiryMonth": adyen_encryptor.encrypt_card_data(expiry_month=self.profile["cc_month"]),
                        "encryptedExpiryYear": adyen_encryptor.encrypt_card_data(expiry_year=self.profile["cc_year"]),
                        "encryptedSecurityCode": adyen_encryptor.encrypt_card_data(cvc=self.profile["cc_cvv"]),
                        "brand": modules.Raffle.FootShop.modules.EnterRaffle.adyen_tools.bin_lookup.get_card_brand(self.session, adyen_encryptor.encrypt_card_data(bin_value=self.profile["cc_number"][:6]), json_response['details']['paymentMethods']['paymentMethods'][0]['brands'], json_response['details']['clientKey'])
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
                print(f'Error encrypting card details: {e}')
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
                print(f"Error completing the registration: {e}")
                time.sleep(10)
                continue

            if response.status_code not in (400, 403, 404, 500, 502):
                try:
                    card_response = response.json()
                except Exception:
                    print(
                        f'Error submitting card, status code: {response.status_code}')
                    time.sleep(10)
                    continue

                errors = card_response.get("errors", None)

                if errors is None:
                    card_response.get("errors", None)

                if errors is not None:
                    print(f'Error submitting card: {errors}')
                    time.sleep(10)
                    return False

                if card_response['registration']['noWin']:
                    print(f'Entry was filtred out...')
                    return False

                else:
                    if self.threeDS(response.json()):
                        return True
                    else:
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
                    print(f"Entry unauthorized with 3DS")
                    return False

        except Exception as exc:
            print(f"Couldn't confirm 3DS: {exc}")
            return False

        return True

    def start(self):

        # All the functions will be called from here, keeping it clean, simple and easily maintable

        # Declaring the requests session that will be used for all the requests
        self.createClient()

        # Incase there is a duplicated entry, the task will stop running
        if self.check_duplicate_entry():
            return

        # Saving the response from the shipping response since it will be needed when submitting payment
        response = self.submit_info()

        # Incase something went wrong during the card-step it will check this from here and print it out
        # i dont know if you guys save amount of failed entries or something to a database, so incase you do, you can easily add/keep track of the stats from here
        if self.submit_payment(response):
            print(f'{self.profile["email"]} has successfully been submitted')
        else:
            print(f'Failed submitting entry for: {self.profile["email"]}')

        # It´s done now :)


def global_sizes(url):

    try:
        r = requests.get(url, headers={
                         'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"})
    except Exception as e:
        print(f'Error loading rafflepage: {e}')
        time.sleep(5)

    initial_state = json.loads(re.search(
        "<script>window\\.__INITIAL_STATE__ = ({.+})</script>", r.text).group(1))
    raffle_id = initial_state['raffleDetail']['raffle']['id']

    sizes = {}
    for size_set in initial_state['raffleDetail']['raffle']['sizeSets']:
        for size in initial_state['raffleDetail']['raffle']['sizeSets'][size_set]['sizes']:
            size["size_set"] = size_set
            try:
                size['us'] = int(size['us'])
            except ValueError:
                size['us'] = float(size['us'])

            sizes[size['us']] = size

    return sizes, raffle_id


def solve_captcha(url):
    # Simple captcha solver that is using the global captcha solver we just declared in the "start" function
    # I guess you already have a solver class or a way to solve captchas
    while True:
        try:
            token = SOLVER.hcaptcha(
                sitekey='55c7c6e2-6898-49ff-9f97-10e6970a3cdb', url=url)['code']
            return token
        except Exception as exc:
            raise Exception(f"Couldn't solve recaptcha: {exc}")


# Declaring the global variables in advance so all the functions will have access to them without issues
SIZES = None
RAFFLE_ID = None
SOLVER = None

# Passing in the **kwargs so you guy can easily handle this the way you are calling the "main"/start function for each script :)


def start_footshop(**kwargs):

    global SIZES
    global RAFFLE_ID
    global SOLVER

    # Asks for the raffleurl to scrape the ID and the sizes
    # Then you wont have to scrape it for every task
    raffle_url = input(f'Please enter the url for the raffle: ')
    SIZES, RAFFLE_ID = global_sizes(raffle_url)

    # Declaring a global Solver for the captcha that will be needed when
    # submitting the profile details

    # I belive you have a way to fetch the TwoCaptcha key from settings file or how you guys do it
    # then just pass the key inside the TwoCaptcha initialization
    SOLVER = TwoCaptcha('YOUR-CAPTCHA-KEY')

    # If you are going to use this method for some reason, you can and should make a loop
    # this is purely for the sake of showcasting an example
    task1 = kwargs.get('task')

    # If you are using multithreading or similar you can simply just make a loop for each task you have in the csv file
    # then call it like this:

    # ========================================================================

    """ tasks = []
    
    # 'alltasks' is just a placeholder for a dictionary or list of all the rows from the .csv file
    
    for task in alltasks:
        tasks.append(threading.Thread(target=Footshop, args=[raffle_url, task]))
        tasks[-1].start()


    for t in tasks:
        t.join() """

    # ========================================================================

    # I havent passed any waiting between all the functions incase you wanna have some sort of delay between the submissions
    # Same if you choose to use multithreading, a good strat is to do a random delay between all threads to avoid a "wave" of submissions at the same time.
    # not sure how well they check for stuff like that but i belive thats down to you guys =D
    Footshop(raffle_url, task1)


# I am leaving this here since i belive your taskhandler will read your .csv like this
# This worked well for me with calling it like this, but since i belive you will have taskhandler you wont be needing this


if __name__ == '__main__':
    data = {
        'email': 'YOUREMAIL',
        'size': '8',
        'first_name': 'NAME',
        'last_name': 'NAME',
        'phone': 'PHONE',
        'house_number': 'HOUSE_NUMBER',
        'street': 'STREET',
        'zip': 'ZIP',
        'city': 'CITY',
        'country_code': 'SE',
        'cc_number': '1234123412341234',
        'cc_month': '04',
        'cc_year': '2024',
        'cc_cvv': '114',
        'instagram': 'YOUR@'
    }
    start_footshop(task=data)

"""geocoding.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 14/09/2021	 00:51	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


import random, csv, os, time
import numpy as np
from colorama import Fore
import sys
from utilities import *

from json import loads as parse_json
from requests import Session
from time import sleep
import re
from utilities import *


from datetime import datetime
from time import sleep
import requests


class Solver:
    def __init__(self, api_key):
        self.api_key = api_key

    def __log(self, text, state="default"):
        if state == "default":
            print(f'[{datetime.now().strftime("%X")}] - {text}')
        elif state == "error":
            print(f'[{datetime.now().strftime("%X")}] - \033[91m{text}\033[0m')
        elif state == "success":
            print(f'[{datetime.now().strftime("%X")}] - \033[92m{text}\033[0m')

    def solve_funCaptcha(self, public_key, page_url, service_url="https://client-api.arkoselabs.com"):
        while True:
            try:
                Logger.info("Solving FunCaptcha...")
                resId = requests.post(f"http://2captcha.com/in.php?key={self.api_key}&method=funcaptcha&publickey={public_key}&surl={service_url}&pageurl={page_url}&json=1").json()['request']
                sleep(20)
                while True:
                    res = requests.get(f"https://2captcha.com/res.php?key={self.api_key}&action=get&id={resId}&json=1").json()
                    if res["request"] != "CAPCHA_NOT_READY":
                        if res["request"] == "ERROR_CAPTCHA_UNSOLVABLE":
                            raise Exception
                        else:
                            return res["request"]
                    else:
                        sleep(5)
            except Exception:
                Logger.info("Failed solving FunCaptcha!", "error")
                sleep(3)


class Rotate(Exception):
    pass


from datetime import datetime, date, timedelta
import random

from faker import Faker


class Helper:
    def get_current_time(self):
        return datetime.now().isoformat()

    def load_cookies(self, session):
        cookies = []
        for name, value in session.cookies.get_dict().items():
            cookies.append(name + "=" + value)
        return "; ".join(cookies)

    def gen_birth_date(self, format):
        random_number_of_days = random.randrange((date(2003, 5, 1) - date(1990, 1, 1)).days)
        random_date = date(1990, 1, 1) + timedelta(days=random_number_of_days)
        return random_date.strftime(format)

    def gen_password(self):
        chars = "abcdefghijklmnopqrstwuvwxyz1234567890_.!?"
        password = ""
        for _ in range(random.randint(10, 16)):
            if random.choice([True, False, False]):
                password += (random.choice(chars)).upper()
            else:
                password += random.choice(chars)
        return password

    def gen_first_name(self):
        return Faker().first_name()

    def gen_last_name(self):
        return Faker().last_name()

    def log(self, text, state="default"):
        if state == "default":
            print(f'[{datetime.now().strftime("%X")}] - {text}')
        elif state == "error":
            print(f'[{datetime.now().strftime("%X")}] - \033[91m{text}\033[0m')
        elif state == "success":
            print(f'[{datetime.now().strftime("%X")}] - \033[92m{text}\033[0m')


class OutlookGeneratorLaunch(Helper, Solver):
    def __init__(self):
        favorite: str = Configuration().getConfiguration()['CaptchaServices']['Favorite']
        super().__init__(api_key=random.choice(Configuration().getConfiguration()['CaptchaServices'][favorite]))

    def start(self):
        while True:
            try:
                Logger.debug("start 1")
                self.funcaptcha_enabled = False
                self.session = requests.Session()
                if not Configuration().getConfiguration()["ProxyLess"]:
                    proxy = ProxyManager("Outlook Generator").getProxy()
                    Logger.debug(proxy)
                    self.session.proxies.update(proxy['proxy'])
                Logger.debug("before loaad register")
                self.load_register_page()
                self.attempt_creation()

                with open('accounts.txt', 'a') as f:
                    f.write(f'{self.email}:{self.password}\n')

                self.log(f"Account creation complete ({self.email}:{self.password})", "success")

            except Exception as e:
                Logger.debug("Error while starting : {}".format(str(e)))
                input()

    def load_register_page(self):
        while True:
            try:

                Logger.info("Loading register page...")
                params = {
                    "wa": "wsignin1.0",
                    "lic": "1"
                }
                headers = {
                    "Host": "signup.live.com",
                    "Connection": "keep-alive",
                    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
                }

                res = self.session.get("https://signup.live.com/signup", headers=headers, params=params)

                form_data = parse_json(res.text.split("var t0=")[1].split(";")[0])
                # print(form_data)
                self.country = form_data["WLXAccount"]["signup"]["viewContext"]["data"]["prefill"]["country"]
                self.site_id = form_data["WLXAccount"]["signup"]["viewContext"]["data"]["siteId"]
                self.funcaptcha_hpgid = form_data["cpgids"]["Signup_HipEnforcementPage_Client"]
                self.is_rdm = form_data["WLXAccount"]["signup"]["viewContext"]["data"]["isRdm"]
                self.default_hpgid = form_data["cpgids"]["Signup_BirthdatePage_Client"]
                self.ski = res.text.split('var SKI="')[1].split('";')[0]
                self.tcxt = form_data["clientTelemetry"]["tcxt"]
                self.fid = form_data["WLXAccount"]["hip"]["fid"]
                self.canary = form_data["apiCanary"]
                self.uiflvr = form_data["uiflvr"]
                self.scid = form_data["scid"]
                self.uaid = form_data["uaid"]
                self.mkt = form_data["mkt"]
                self.key = re.findall('var Key="(.*?)";', res.text)[0]
                self.randomNum = re.findall('var randomNum="(.*?)";', res.text)[0]

            except Exception:
                Logger.error("Failed loading register page!")
                sleep(3)
            else:
                break

    def attempt_creation(self):
        while True:
            try:
                if not self.funcaptcha_enabled:
                    self.log("Attempting creation...")
                    self.first_name = self.gen_first_name()
                    self.last_name = self.gen_last_name()
                    self.password = self.gen_password()
                    self.birthdate = self.gen_birth_date("%d:%m:%Y")
                    self.email = self.first_name + self.last_name + "@outlook.com"

                payload = {
                    'key': self.key,
                    'random_number': self.randomNum,
                    'password': self.password
                }

                Logger.info(payload)

                url2 = "http://localhost:8000/api/v3/outlook"
                encrypt = self.session.get(url2, json=payload)

                Logger.info(encrypt.text)

                encrypt = parse_json(encrypt.text)
                self.ciphervalue = encrypt["cipher_value"]

                params = {
                    "wa": "wsignin1.0",
                    "lic": "1"
                }
                headers = {
                    "Host": "signup.live.com",
                    "Connection": "keep-alive",
                    "Content-Length": "1188",
                    "x-ms-apiVersion": "2",
                    "uaid": self.uaid,
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                    "canary": self.canary,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "hpgid": str(self.default_hpgid),
                    "Accept": "application/json",
                    "tcxt": self.tcxt,
                    "X-Requested-With": "XMLHttpRequest",
                    "uiflvr": str(self.uiflvr),
                    "scid": str(self.scid),
                    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                    "x-ms-apiTransport": "xhr",
                    "sec-ch-ua-platform": '"Windows"',
                    "Origin": "https://signup.live.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://signup.live.com/signup?wa=wsignin1.0&lic=1",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": self.load_cookies(self.session)
                }
                json = {
                    "RequestTimeStamp": self.get_current_time(),
                    "MemberName": self.email,
                    "CheckAvailStateMap": [f"{self.email}:undefined"],
                    "EvictionWarningShown": [],
                    "UpgradeFlowToken": {},
                    "FirstName": self.first_name,
                    "LastName": self.last_name,
                    "MemberNameChangeCount": 1,
                    "MemberNameAvailableCount": 1,
                    "MemberNameUnavailableCount": 0,
                    "CipherValue": self.ciphervalue,
                    "SKI": self.ski,
                    "BirthDate": self.birthdate.format("%d:%m:%Y"),
                    "Country": self.country,
                    "IsOptOutEmailDefault": True,
                    "IsOptOutEmailShown": True,
                    "IsOptOutEmail": True,
                    "LW": True,
                    "SiteId": self.site_id,
                    "IsRDM": self.is_rdm,
                    "WReply": None,
                    "ReturnUrl": None,
                    "SignupReturnUrl": None,
                    "uiflvr": self.uiflvr,
                    "uaid": self.uaid,
                    "SuggestedAccountType": "EASI",
                    "SuggestionType": "Prefer",
                    "HFId": self.fid
                }

                Logger.info("headers and json ready")

                if not self.funcaptcha_enabled:
                    Logger.info("no funcatpcha enabled")
                    json.update({
                        "encAttemptToken": "",
                        "dfpRequestId": "",
                        "scid": self.scid,
                        "hpgid": self.default_hpgid
                    })
                    Logger.info("new json ready")

                else:
                    headers["hpgid"] = str(self.funcaptcha_hpgid)
                    Logger.info("have to solve funcaptcha")
                    json.update({
                        "HType": "enforcement",
                        "HSol": self.solve_funCaptcha("B7D8911C-5CC8-A9A3-35B0-554ACEE604DA",
                                                      "https://signup.live.com/signup"),
                        "HPId": "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA",
                        "encAttemptToken": self.enc_attempt_token,
                        "dfpRequestId": self.dfp_request_id,
                        "scid": self.scid,
                        "hpgid": self.funcaptcha_hpgid
                    })

                res = self.session.post("https://signup.live.com/API/CreateAccount", headers=headers, params=params,
                                        json=json).json()

                Logger.info(res)

                # ##########################################################################
                # # this needs to be fixed in order to use the accounts in Skyridge
                # # trying to load the inbox
                # headers1 = {
                #     # ":authority": "outlook.live.com",
                #     # ":method": "GET",
                #     # ":path": "/mail/0/",
                #     # ":scheme": "https",
                #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                #     "accept-encoding": "gzip, deflate, br",
                #     "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
                #     "cookie": self.load_cookies(),
                #     "Referer": "https://outlook.live.com/",
                #     "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                #     "sec-ch-ua-mobile": "?0",
                #     "sec-ch-ua-platform": "Windows",
                #     "sec-fetch-dest": "document",
                #     "sec-fetch-mode": "navigate",
                #     "sec-fetch-site": "same-origin",
                #     "upgrade-insecure-requests": "1",
                #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
                # }

                # # thought a redirect would solve the problem from his request to the next but it doesnt work
                # inbox1 = self.session.get("https://outlook.live.com/mail/0/inbox", headers=headers1, allow_redirects=True)
                # print(inbox1.text)
                # print("---------------------------------------------------------------------------------------")
                # print(inbox1.status_code)
                # ##########################################################################

                if "error" in res and res["error"]["code"] == "1041":
                    self.tcxt = res["error"]["telemetryContext"]
                    error_data = parse_json(res["error"]["data"])
                    self.enc_attempt_token = error_data["encAttemptToken"]
                    self.dfp_request_id = error_data["dfpRequestId"]
                    self.funcaptcha_enabled = True
                elif "slt" in res:
                    break
                else:
                    raise Rotate

            except Rotate:
                raise Exception

            except Exception as e:
                print(e)
                self.log("Failed attempting creation!", "error")
                sleep(3)


if __name__ == '__main__':
    OutlookGeneratorLaunch().start()

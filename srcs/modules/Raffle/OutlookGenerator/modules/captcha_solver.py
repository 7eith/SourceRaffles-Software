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
                self.__log("Solving FunCaptcha...")
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
                self.__log("Failed solving FunCaptcha!", "error")
                sleep(3)
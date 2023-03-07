# ------------------------------------------------------------------------------- #
import re, base64, time, requests
import importlib
from bs4 import BeautifulSoup
from collections import OrderedDict


# ------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------- #


# ------------------------------------------------------------------------------- #

from urllib.parse import urlparse
import lzstring

class SolvingError(Exception):
    '''
    Custom Error to be able to catch this error seperatly.
    '''
    pass

def check_for_captcha(soup_string):
    captcha = soup_string.find("input",attrs={
        "name":"cf_captcha_kind"
    })
    if not captcha:
        return False
    if captcha["value"] == "h":
        return True
    else:
        raise Exception("Captcha type not supported: "+captcha["value"])

def compressToEncodedURIComponent(uncompressed,keyStrUriSafe):
    '''A monkeypatched version of lzstring'''
    if uncompressed is None:
        return ""
    return lzstring._compress(uncompressed, 6, lambda a: keyStrUriSafe[a])

def extract_domain(url: str) -> str:
    """:returns domain from given url."""
    parsed_url = urlparse(url)
    return parsed_url.netloc


class CF_2():
    def __init__(self, adapter, original, key, captcha=False, debug=False):
        # Config vars
        self.script = "https://{}/cdn-cgi/challenge-platform/h/g/orchestrate/jsch/v1"
        self.captcha_script = "https://{}/cdn-cgi/challenge-platform/h/g/orchestrate/captcha/v1"
        self.api_domain = "cf-v2.hwkapi.com"

        self.timeOut = 30
        self.errorDelay = 0

        # set up session for the api communication to prevent renegotiation on each request
        self.s = requests.Session()
        # Vars
        self.adapter = adapter
        self.original_request = original
        self.domain = extract_domain(original.url)
        self.debug = debug
        self.key = key
        self.auth_params = {
            "auth": self.key
        }
        self.md = None

        self.captcha = captcha

        self.start_time = time.time()

        self.init_headers = OrderedDict([
            ('Connection', 'keep-alive'),
            ('sec-ch-ua', '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"'),
            ('sec-ch-ua-mobile', '?0'),
            ('User-Agent', self.adapter.user_agent.custom),
            ('Accept', '*/*'),
            ('Sec-Fetch-Site', 'same-origin'),
            ('Sec-Fetch-Mode', 'no-cors'),
            ('Sec-Fetch-Dest', 'script'),
            ('Referer', 'https://www.referer.com/'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Accept-Language', 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7')])

        self.challenge_headers = OrderedDict([('Connection', 'keep-alive'),
                                              ('sec-ch-ua', '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"'),
                                              ('sec-ch-ua-mobile', '?0'),
                                              ('User-Agent',self.adapter.user_agent.custom),
                                              ('CF-Challenge', 'b6245c8f8a8cb25'),
                                              ('Content-type', 'application/x-www-form-urlencoded'),
                                              ('Accept', '*/*'),
                                              ('Origin', 'https://www.origin.com'),
                                              ('Sec-Fetch-Site', 'same-origin'),
                                              ('Sec-Fetch-Mode', 'cors'),
                                              ('Sec-Fetch-Dest', 'empty'),
                                              ('Referer', 'https://www.referer.com/'),
                                              ('Accept-Encoding', 'gzip, deflate, br'),
                                              ('Accept-Language', 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7')])

        self.submit_headers = OrderedDict(
            [('Connection', 'keep-alive'),
             ('Cache-Control', 'max-age=0'),
             ('sec-ch-ua', '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"'),
             ('sec-ch-ua-mobile', '?0'),
             ('Upgrade-Insecure-Requests', '1'),
             ('Origin', 'https://www.origin.com'),
             ('Content-Type', 'application/x-www-form-urlencoded'),
             ('User-Agent', self.adapter.user_agent.custom),
             ('Accept',
              'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
             ('Sec-Fetch-Site', 'same-origin'), ('Sec-Fetch-Mode', 'navigate'),
             ('Sec-Fetch-Dest', 'document'),
             ('Referer', 'https://ref.com'),
             ('Accept-Encoding', 'gzip, deflate, br'),
             ('Accept-Language', 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7')])

    def solve(self):
        """Loading init script"""
        self.solveRetries = 0
        self.solveMaxRetries = 5
        while True:
            if self.debug:
                print(f"Solving challenge. ({self.solveRetries}/{self.solveMaxRetries})")

            if self.solveRetries == self.solveMaxRetries:
                raise Exception(f"Solving challenge failed after {self.solveMaxRetries} retries.")
            else:
                self.solveRetries += 1

                # Fetching CF script
                if not self.captcha:
                    script = self.script.format(self.domain)
                else:
                    script = self.captcha_script.format(self.domain)

                try:
                    self.adapter.headers = self.init_headers
                    self.adapter.headers["Referer"] = self.original_request.url
                    self.init_script = self.adapter.get(script, timeout=self.timeOut, verify=False,)
                except Exception as e:
                    if self.debug:
                        print(f"Failed to request init script: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    if self.debug:
                        print("Loaded init script.")

                    self.solveRetries = 0
                    return self.challenge_initation_payload()

    def challenge_initation_payload(self):
        """Fetches payload for challenge iniation from our api"""

        self.initPayloadRetries = 0
        self.initPayloadMaxRetries = 5
        while True:
            if self.debug:
                print(f"Fetching payload. ({self.initPayloadRetries}/{self.initPayloadMaxRetries})")

            if self.initPayloadRetries == self.initPayloadMaxRetries:
                raise Exception(f"Fetching payload failed after {self.initPayloadMaxRetries} retries.")
            else:
                self.initPayloadRetries += 1

                # Parsing of the data needed for the api to serve the init payload
                try:
                    matches = re.findall(r"0\.[^('|/)]+", self.init_script.text)
                    urlpart = matches[0]
                    matches = re.findall(r"[\W]?([A-Za-z0-9+\-$]{65})[\W]", self.init_script.text)
                    for i in matches:
                        i = i.replace(",", "")
                        if "+" in i and "-" in i and "$" in i:
                            self.keyStrUriSafe = i
                            break
                except Exception as e:
                    if self.debug:
                        print(f"Failed to parse data needed for init payload: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue

                # Requesting payload from the api
                try:
                    payload = {
                        "body": base64.b64encode(self.original_request.text.encode("UTF-8")).decode("UTF-8"),
                        "url": urlpart,
                        "domain": self.domain,
                        "captcha": self.captcha,
                        "key": self.keyStrUriSafe
                    }
                    challenge_payload = self.s.post("https://{}/cf-a/ov1/p1".format(self.api_domain),
                                                      params=self.auth_params, json=payload, verify=False,
                                                      timeout=self.timeOut).json()

                    self.init_url = challenge_payload["url"]
                    self.request_url = challenge_payload["result_url"]
                    self.result = challenge_payload["result"]
                    self.name = challenge_payload["name"]
                    self.baseobj = challenge_payload["baseobj"]
                    self.request_pass = challenge_payload["pass"]
                    self.request_r = challenge_payload["r"]
                    self.ts = challenge_payload["ts"]
                    if "md" in challenge_payload:
                        self.md = challenge_payload["md"]
                        
                except Exception as e:
                    if self.debug:
                        print(f"Failed submit data to the api: {str(e)}\nmake sure that you have your API KEY assigned")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.initPayloadRetries = 0

                    if self.debug:
                        print("Submitted init payload to the api.")

                    return self.initiate_cloudflare()

    def initiate_cloudflare(self):
        """Initiares the cloudflare challenge"""

        self.initChallengeRetries = 0
        self.initChallengeMaxRetries = 5
        while True:
            if self.debug:
                print(f"Initiating challenge. ({self.initChallengeRetries}/{self.initChallengeMaxRetries})")

            if self.initChallengeRetries == self.initChallengeMaxRetries:
                raise Exception(f"Initiating challenge failed after {self.initChallengeMaxRetries} retries.")
            else:
                self.initChallengeRetries += 1

                if not self.keyStrUriSafe:
                    raise Exception("KeyUri cannot be None.")
                else:
                    try:
                        payload = {
                            self.name: compressToEncodedURIComponent(base64.b64decode(self.result).decode(),
                                                                     self.keyStrUriSafe)
                        }
                        self.adapter.headers = self.challenge_headers
                        self.adapter.headers["CF-Challenge"] = self.init_url.split("/")[-1]
                        self.adapter.headers["Referer"] = self.original_request.url.split("?")[0]
                        self.adapter.headers["Origin"] = f"https://{self.domain}"
                        self.challenge_payload = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut,verify=False)
                    except Exception as e:
                        if self.debug:
                            print(f"Initiating challenge error: {str(e)}")
                        time.sleep(self.errorDelay)
                        continue
                    else:
                        self.initChallengeRetries = 0

                        if self.debug:
                            print("Initiated challenge.")

                        return self.solve_payload()

    def solve_payload(self):
        """Fetches main challenge payload from hawk api"""

        self.fetchingChallengeRetries = 0
        self.fetchingChallengeMaxRetries = 5
        while True:
            if self.debug:
                print(f"Fetching main challenge. ({self.fetchingChallengeRetries}/{self.fetchingChallengeMaxRetries})")

            if self.fetchingChallengeRetries == self.fetchingChallengeMaxRetries:
                raise SolvingError(
                    f"Fetching main challenge failed after {self.fetchingChallengeMaxRetries} retries.\nThis error is mostlikly related to a wring usage of headers.\nIf this exception occurs on an endpoint which is used to peform a carting or a similiar action note that the solving process shell not work here by cloudflare implementation on sites.\nIf this occurs you need to regen the cookie on a get page request or similiar with resettet headers.\nAfter generation you can assign the headers again and cart again.")
            else:
                self.fetchingChallengeRetries += 1

                try:
                    payload = {
                        "body_home": base64.b64encode(self.original_request.text.encode()).decode(),
                        "body_sensor": base64.b64encode(self.challenge_payload.text.encode()).decode(),
                        "result": self.baseobj,
                        "ts": self.ts,
                        "url": self.init_url,
                        "ua": self.adapter.user_agent.custom
                    }

                    cc = self.s.post("https://{}/cf-a/ov1/p2".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    cc = cc.json()
                    self.result = cc["result"]
                except Exception as e:
                    if self.debug:
                        print(f"aaload error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.fetchingChallengeRetries = 0

                    if self.debug:
                        print("Fetched challenge payload.")

                    return self.send_main_payload()

    def send_main_payload(self):
        """Sends the main payload to cf"""

        self.submitChallengeRetries = 0
        self.submitChallengeMaxRetries = 5
        while True:
            if self.debug:
                print(f"Submitting challenge. ({self.submitChallengeRetries}/{self.submitChallengeMaxRetries})")

            if self.submitChallengeRetries == self.submitChallengeMaxRetries:
                raise Exception(f"Submitting challenge failed after {self.submitChallengeMaxRetries} retries.")
            else:
                self.submitChallengeRetries += 1

                try:
                    payload = {
                        self.name: compressToEncodedURIComponent(base64.b64decode(self.result).decode(),
                                                                 self.keyStrUriSafe)
                    }


                    self.mainpayload_response = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(f"Submitting challenge error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitChallengeRetries = 0

                    if self.debug:
                        print("Submitted challenge.")

                    return self.getChallengeResult()

    def getChallengeResult(self):
        """Fetching challenge result"""

        self.challengeResultRetries = 0
        self.challengeResultMaxRetries = 5
        while True:
            if self.debug:
                print(f"Fetching challenge result. ({self.challengeResultRetries}/{self.challengeResultMaxRetries})")

            if self.challengeResultRetries == self.challengeResultMaxRetries:
                raise Exception(f"Fetching challenge result failed after {self.challengeResultMaxRetries} retries.")
            else:
                self.challengeResultRetries += 1

                try:
                    payload = {
                        "body_sensor": base64.b64encode(self.mainpayload_response.text.encode()).decode(),
                        "result": self.baseobj
                    }

                    ee = self.s.post("https://{}/cf-a/ov1/p3".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    self.final_api = ee.json()
                except Exception as e:
                    if self.debug:
                        print(f"Fetching challenge result error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.challengeResultRetries = 0

                    if self.debug:
                        print("Fetched challenge response.")

                    return self.handle_final_api()

    def handle_final_api(self):
        """Handle final API result and rerun if needed"""

        if self.final_api["status"] == "rerun":
            return self.handle_rerun()
        if self.final_api["captcha"]:
            if not self.captcha:
                raise Exception("Cf returned captcha and captcha handling is disabled")
            else:
                return self.handle_captcha()
        else:
            return self.submit()

    def submit(self):
        """Submits the challenge and trys to access target url"""

        self.submitFinalChallengeRetries = 0
        self.submitFinalChallengeMaxRetries = 5
        while True:
            if self.debug:
                print(
                    f"Submitting final challenge. ({self.submitFinalChallengeRetries}/{self.submitFinalChallengeMaxRetries})")

            if self.submitFinalChallengeRetries == self.submitFinalChallengeMaxRetries:
                raise Exception(
                    f"Submitting final challenge failed after {self.submitFinalChallengeMaxRetries} retries.")
            else:
                self.submitFinalChallengeRetries += 1

                self.adapter.headers = self.submit_headers
                self.adapter.headers["referer"] = self.original_request.url
                self.adapter.headers["origin"] = f"https://{self.domain}"

                try:
                    payload = {
                        "r": self.request_r,
                        "jschl_vc": self.final_api["jschl_vc"],
                        "pass": self.request_pass,
                        "jschl_answer": self.final_api["jschl_answer"],
                        "cf_ch_verify": "plat"
                    }
                    # cf added a new flow where they present a 503 followed up by a 403 captcha
                    if "cf_ch_cp_return" in self.final_api:
                        self.captcha = True
                        payload["cf_ch_cp_return"] = self.final_api["cf_ch_cp_return"]

                    if self.md:
                        payload["md"] = self.md

                    if round(time.time() - self.start_time) < 5:
                        # Waiting X amount of sec for CF delay
                        if self.debug:
                            print("Sleeping {} sec for cf delay".format(5 - round(time.time() - self.start_time)))
                        time.sleep(5 - (round(time.time() - self.start_time)))

                    final = self.adapter.post(self.request_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(f"Submitting final challenge error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitFinalChallengeRetries = 0

                    if self.debug:
                        print("Submitted final challange.")

                    if final.status_code == 403:
                        soup = BeautifulSoup(final.text, "lxml")
                        if check_for_captcha(soup):
                            # as this was a 403 post we need to get again dont ask why just do it
                            weird_get_req = self.adapter.get(self.original_request.url, timeout=self.timeOut)
                            return CF_2(self.adapter, weird_get_req, self.key, True, self.debug).solve()

                    return final

    def handle_rerun(self):
        """Handling rerun"""

        self.rerunRetries = 0
        self.rerunMaxRetries = 5
        while True:
            if self.debug:
                print(f"Handling rerun. ({self.rerunRetries}/{self.rerunMaxRetries})")

            if self.rerunRetries == self.rerunMaxRetries:
                raise Exception(f"Rerun failed after {self.rerunMaxRetries} retries.")
            else:
                self.rerunRetries += 1

                try:
                    payload = {
                        "body_home": base64.b64encode(self.original_request.text.encode()).decode(),
                        "body_sensor": base64.b64encode(self.mainpayload_response.text.encode()).decode(),
                        "result": self.baseobj,
                        "ts": self.ts,
                        "url": self.init_url,
                        "rerun": True,
                        "rerun_base": self.result
                    }
                    alternative = self.s.post("https://{}/cf-a/ov1/p2".format(self.api_domain), verify=False,
                                                params=self.auth_params, json=payload, timeout=self.timeOut)
                    alternative = alternative.json()
                    self.result = alternative["result"]
                except Exception as e:
                    if self.debug:
                        print(f"Fetching rerun challenge payload error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.rerunRetries = 0

                    if self.debug:
                        print("Handled rerun.")

                    return self.send_main_payload()

    def handle_captcha(self):
        """Handling captcha
        Note that this function is designed to work with cloudscraper,
        if you are building your own flow you will need to rework this part a bit.
        """

        self.captchaRetries = 0
        self.captchaMaxRetries = 5
        while True:
            if self.debug:
                print(f"Handling captcha. ({self.captchaRetries}/{self.captchaMaxRetries})")

            if self.captchaRetries == self.captchaMaxRetries:
                raise Exception(f"Handling captcha failed after {self.captchaMaxRetries} retries.")
            else:
                self.captchaRetries += 1
                if self.final_api["click"]:
                    token = "click"
                else:
                    if self.debug:
                        print("Captcha needed, requesting token.")
                    try:
                        # ------------------------------------------------------------------------------- #
                        # Pass proxy parameter to provider to solve captcha.
                        # ------------------------------------------------------------------------------- #

                        if self.adapter.proxies and self.adapter.proxies != self.adapter.captcha.get('proxy'):
                            self.adapter.captcha['proxy'] = self.adapter.proxies

                        # ------------------------------------------------------------------------------- #
                        # Pass User-Agent if provider supports it to solve captcha.
                        # ------------------------------------------------------------------------------- #

                        self.adapter.captcha['User-Agent'] = self.adapter.headers['User-Agent']

                        # check which captcha service is assigned
                        provider = self.adapter.captcha["provider"]
                        if self.debug:
                            print(f"Using {provider} as captcha provider")

                        # importing the fitting captcha module from cloudscraper
                        Captchalib = importlib.import_module(f'cloudscraper.captcha.{provider}').captchaSolver()
                        token = Captchalib.getCaptchaAnswer(
                            "hCaptcha",
                            self.original_request.url,
                            self.final_api["sitekey"],
                            self.adapter.captcha
                        )
                    except Exception as e:
                        if self.debug:
                            print(f"Failed to get captcha token from 2cap: {str(e)}")
                    else:
                        if self.debug:
                            print(f"Got captcha token from 2cap.")

                try:
                    payload = {
                        "result": self.result,
                        "token": token,
                        "h-captcha-response": token,
                        "data": self.final_api["result"]
                    }

                    # first captcha api call
                    ff = self.s.post("https://{}/cf-a/ov1/cap1".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    self.first_captcha_result = ff.json()
                except Exception as e:
                    if self.debug:
                        print(f"First captcha API call error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    try:
                        payload = {
                            self.name: compressToEncodedURIComponent(
                                base64.b64decode(self.first_captcha_result["result"]).decode(), self.keyStrUriSafe)
                        }
                        self.adapter.headers = self.challenge_headers
                        self.adapter.headers["Referer"] = self.original_request.url
                        self.adapter.headers["Origin"] = self.domain
                        self.adapter.headers["CF-Challenge"] = self.init_url.split("/")[-1]

                        gg = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut)
                    except Exception as e:
                        if self.debug:
                            print(f"Posting to cloudflare challenge endpoint error: {str(e)}")
                        time.sleep(self.errorDelay)
                        continue
                    else:
                        try:
                            payload = {
                                "body_sensor": base64.b64encode(gg.text.encode()).decode(),
                                "result": self.baseobj
                            }

                            hh = self.s.post("https://{}/cf-a/ov1/cap2".format(self.api_domain),
                                               params=self.auth_params, json=payload, verify=False,
                                               timeout=self.timeOut)
                            self.captcha_response_api = hh.json()
                        except Exception as e:
                            if self.debug:
                                print(f"Second captcha API call error: {str(e)}")
                            time.sleep(self.errorDelay)
                            continue
                        else:
                            self.captchaRetries = 0
                            if self.captcha_response_api["valid"]:
                                if self.debug:
                                    print("Captcha is accepted.")
                                return self.submit_captcha()
                            else:
                                raise Exception("Captcha was not accepted - most likly wrong token")

    def submit_captcha(self):
        """Submits the challenge + captcha and trys to access target url"""

        self.submitCaptchaRetries = 0
        self.submitCaptchaMaxRetries = 5
        while True:
            if self.debug:
                print(f"Submitting captcha challenge. ({self.submitCaptchaRetries}/{self.submitCaptchaMaxRetries})")

            if self.submitCaptchaRetries == self.submitCaptchaMaxRetries:
                raise Exception(f"Submitting captcha challenge failed after {self.submitCaptchaMaxRetries} retries.")
            else:
                self.submitCaptchaRetries += 1

                try:
                    self.adapter.headers = self.submit_headers
                    self.adapter.headers["Referer"] = self.original_request.url
                    self.adapter.headers["Origin"] = f"https://{self.domain}"

                    payload = {
                        "r": self.request_r,
                        "cf_captcha_kind": "h",
                        "vc": self.request_pass,
                        "captcha_vc": self.captcha_response_api["jschl_vc"],
                        "captcha_answer": self.captcha_response_api["jschl_answer"],
                        "cf_ch_verify": "plat"
                    }

                    if "cf_ch_cp_return" in self.captcha_response_api:
                        payload["cf_ch_cp_return"] = self.captcha_response_api["cf_ch_cp_return"]

                    if self.md:
                        payload["md"] = self.md

                    payload["h-captcha-response"] = "captchka"

                    if round(time.time() - self.start_time) < 5:
                        # Waiting X amount of sec for CF delay
                        if self.debug:
                            print("Sleeping {} sec for cf delay".format(5 - round(time.time() - self.start_time)))
                        time.sleep(5 - (round(time.time() - self.start_time)))

                    final = self.adapter.post(self.request_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(f"Submitting captcha challenge error: {str(e)}")
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitCaptchaRetries = 0

                    if self.debug:
                        print("Submitted captcha challange.")

                    return final


class Cf_challenge_3:

    def __init__(self, adapter, original, key, debug=False):
        # Config vars
        self.api_domain = "cf-v2.hwkapi.com"
        self.timeOut = 30
        # set up session for negociation
        self.s = requests.Session()
        # Vars
        self.adapter = adapter
        self.original_request = original
        self.domain = extract_domain(original.url)
        self.debug = debug
        self.key = key
        self.auth_params = {
            "auth": self.key
        }

    def solve(self):
        '''
        Solves the cloudflare fingerpringt challenge
        :return:
        '''
        return self.initiate_script()

    def initiate_script(self):
        '''
        iniates the first script from cf fingerprint challenge
        :return:
        '''
        if self.debug:
            print("Receiving fingerprint script")
        url_path = self.original_request.text.split('<script src="')[3].split('"')[0]
        self.init_url = "https://" + self.domain + url_path
        self.init_script = self.adapter.get(self.init_url, timeout=self.timeOut, verify=False)
        return self.get_payload_from_api()

    def get_payload_from_api(self):
        '''
        Recieve the needed fingerprint data from hawk api
        :return:
        '''
        paylaod = {
            "body": base64.b64encode(self.init_script.text.encode()).decode(),
            "url": self.init_url
        }
        if self.debug:
            print("Receiving api payload")
        hawk_api = self.s.post(f"https://cf-v2.hwkapi.com/cf-a/fp/p1", params=self.auth_params, json=paylaod,
                                 timeout=self.timeOut, verify=False).json()
        self.result = hawk_api["result"]
        self.target_url = hawk_api["url"]
        return self.submit()

    def submit(self):
        '''
        Submit the fingerprint data to cloudflare
        :return:
        '''
        if self.debug:
            print("Submitting fingerprint")
        result = self.adapter.post(self.target_url, timeout=self.timeOut, verify=False, json=self.result)
        if result.status_code == 429:
            raise Exception("FP DATA declined")
        elif result.status_code == 404:
            raise Exception("Fp ep changed")

        return self.get_page()

    def get_page(self):
        '''
        Perform the original request
        :return:
        '''
        if self.debug:
            print("Fetching original request target")
        if "?" in self.original_request.url:
            url = self.original_request.url.split("?")[0]
        else:
            url = self.original_request.url
        result = self.adapter.get(url, timeout=self.timeOut, verify=False)
        return result

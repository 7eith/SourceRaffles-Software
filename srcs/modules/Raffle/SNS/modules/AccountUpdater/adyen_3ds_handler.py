import os
import undetected_chromedriver as uc
import time
from utilities import *
import json
import base64


def handle_3ds(payment_action, session, live_token, return_url, redirect_hook):
    try:
        Logger.info("Attempting to solve 3ds authorization")

        options = uc.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--window-size=150,750")

        payment_details_res = None
        threeds_confirmed = False
        if payment_action['type'] == "redirect":
            script = f"""document.write('<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>SourceRaffles</title></head><body><h1>Loading 3DS...<form id="threeds" method="post" action="{payment_action['url']}"><input type="hidden" name="MD" value="{payment_action['data']['MD']}"><input type="hidden" name="PaReq" value="{payment_action['data']['PaReq']}"><input type="hidden" name="TermUrl" value="{payment_action['data']['TermUrl']}"></form><script>document.querySelector("#threeds").submit();</script></body></html>')"""

            driver = uc.Chrome(options=options)
            time.sleep(1)
            driver.execute_script(script)

            if not redirect_hook(driver):
                Logger.error("3DS not confirmed in time.")

        elif payment_action['type'] == "threeDS2":
            if payment_action['subtype'] == "fingerprint":
                fingerprint_payload = {
                    "fingerprintResult": "eyJ0aHJlZURTQ29tcEluZCI6IlkifQ==",
                    "paymentData": payment_action['paymentData']
                }
                submit_fingerprint_res = session.post(
                    f"https://checkoutshopper-live.adyen.com/checkoutshopper/v1/submitThreeDS2Fingerprint?token={live_token}", json=fingerprint_payload)

                threeds_result = submit_fingerprint_res.json()['details']['threeDSResult']

                payment_details_payload = {
                    "details": {
                        "threeDSResult": threeds_result
                    }
                }
                payment_details_res = session.post(
                    return_url, json=payment_details_payload)
            elif payment_action['subtype'] == "challenge":
                token_decoded = json.loads(base64.b64decode(
                    payment_action['token'].encode()).decode('utf-8'))

                if "acsURL" in token_decoded:
                    url = token_decoded['acsURL']
                    token_decoded.pop('acsURL')
                    token_decoded.pop('acsReferenceNumber')
                    token_decoded.pop('threeDSNotificationURL')
                elif "threeDSMethodUrl" in token_decoded:
                    url = token_decoded['threeDSMethodUrl']
                    token_decoded.pop('threeDSMethodUrl')
                    token_decoded.pop('threeDSMethodNotificationURL')
                else:
                    Logger.error(
                        f"This 3DS method is not supported. Please contact a developer and send this so we'll be able to add it: {payment_action['action']}")

                token_decoded['messageType'] = "CReq"
                token_decoded['challengeWindowSize'] = "02"

                send_token = base64.b64encode(json.dumps(
                    token_decoded).encode()).decode("utf-8")

                script = f"""document.write('<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>SourceRaffles</title></head><body><h1>Loading 3DS...<form id="threeds" method="post" action="{url}"> <input type="hidden" name="creq" value="{send_token}"></form> <script>document.querySelector("#threeds").submit();</script></body></html>')"""

                driver = uc.Chrome(options=options, executable_path=os.getcwd() + "/resources/chromedriver")
                time.sleep(1)
                driver.execute_script(script)

                for i in range(300):
                    if driver.title == "3DS 2.0 return page":
                        threeds_confirmed = True

                        time.sleep(1)
                        driver.close()
                        break
                    else:
                        time.sleep(1)

                if not threeds_confirmed:
                    Logger.error("3DS not confirmed in time.")

                threeds_result = {
                    "transStatus": "Y",
                    "authorisationToken": payment_action['authorisationToken']
                }

                threeds_result_encoded = base64.b64encode(
                    json.dumps(threeds_result).encode()).decode('utf-8')

                payment_details_payload = {
                    "details": {
                        "threeDSResult": threeds_result_encoded
                    }
                }
                payment_details_res = session.post(
                    return_url, json=payment_details_payload)
            else:
                Logger.error(
                    f"3DS type {payment_action['subtype']} is not currently supported.")

        else:
            Logger.error(
                f"Payment action: {payment_action['type']} is not supported.")

        Logger.success("3DS successfully solved!")
        return payment_details_res
    finally:
        try:
            driver.close()
        except Exception:
            pass

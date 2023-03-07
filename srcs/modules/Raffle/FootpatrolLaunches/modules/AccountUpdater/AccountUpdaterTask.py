"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountUpdaterTask.py                       """
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
from aws_requests_auth.aws_auth import AWSRequestsAuth
from core.configuration.Configuration import Configuration
import json


class AccountUpdaterTask():

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile) -> None:

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict    = profile

        """ Store """
        self.logIdentifier: str     = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state:         str     = "PENDING"
        self.success:       bool    = False
        self.retry:         int     = 0
        self.maxRetry:      int     = 10
        self.csrfToken:     str     = None
        self.captchaToken:  str     = None

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            self.initSession()
            self.executeTask()
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(f"{self.logIdentifier} {str(error)}")

            self.profile['status'] = "FAILED"
            self.success = False

    def executeTask(self):

        status: int = self.updateAccount()

        if status == 1:

            Logger.info(f"{self.logIdentifier} Successfully updated account ! ")
            self.state = "SUCCESS"
            self.success = True
        else:
            self.state = "FAILED"
            self.success = False

    def updateAccount(self):

        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'x-amz-target': 'AWSCognitoIdentityProviderService.InitiateAuth',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'x-amz-user-agent': 'aws-amplify/0.1.x react-native',
            'Accept-Language': 'fr-fr',
            'User-Agent': 'rafflemobile/1 CFNetwork/1240.0.4 Darwin/20.5.0',
        }

        data = {"AuthFlow": "CUSTOM_AUTH",
                "ClientId": "60skugd7dfshb9qerf70h38e2q",
                "AuthParameters": {
                    "USERNAME": self.profile["email"]
                },
                "ClientMetadata": {}
                }

        Logger.info(f"{self.logIdentifier}Initiating login")
        forcedLogin = False
        try:
            response = self.session.post('https://cognito-idp.eu-west-1.amazonaws.com/', headers=headers, json=data)
            if response.status_code != 200:
                Logger.error(f"{self.logIdentifier}Error while initiating login : {response.status_code} / {response.text}")

                try:
                    message = response.json()["message"]
                    if message == "User does not exist.":
                        Logger.info(f"{self.logIdentifier} Account never logged on the FootpatrolLaunches app, creating session...")

                        headers = {
                            'Content-Type': 'application/x-amz-json-1.1',
                            'x-amz-target': 'AWSCognitoIdentityProviderService.InitiateAuth',
                            'Connection': 'keep-alive',
                            'Accept': '*/*',
                            'x-amz-user-agent': 'aws-amplify/0.1.x react-native',
                            'User-Agent': 'rafflemobile/1 CFNetwork/1240.0.4 Darwin/20.5.0',
                        }
        
                        data = {"AuthFlow": "USER_PASSWORD_AUTH",
                                "ClientId": "60skugd7dfshb9qerf70h38e2q",
                                "AuthParameters": {
                                    "USERNAME": self.profile["email"].lower(),
                                    "PASSWORD": self.profile["password"]
                                },
                                "ClientMetadata": {}
                                }
                        forcedLoginReq = self.session.post('https://cognito-idp.eu-west-1.amazonaws.com/', headers=headers, json=data)
                        if forcedLoginReq.status_code == 200:
                            Logger.info(f"{self.logIdentifier}Forced login succeeded !")
                            Logger.debug(forcedLoginReq.json())
                            idToken = forcedLoginReq.json()['AuthenticationResult']['IdToken']
                            forcedLogin = True
                        else:
                            Logger.error(f"{self.logIdentifier}Error while forcing login : {forcedLoginReq.status_code} / {forcedLoginReq.text}")
                            return -1
                    else:
                        Logger.error("{} Error while initiating login (not forcing login) : {} / {}".format(self.logIdentifier, response.status_code, response.text))
                        return -1
                except Exception as e:
                    Logger.error("{} Error while forcing login : {}".format(self.logIdentifier, str(e)))
                    return -1

        except Exception as e:
            Logger.error("{} Error while initiating login : {}".format(self.logIdentifier, str(e)))
            return -1
        except requests.exceptions.ProxyError:
            Logger.error(f"{self.logIdentifier} Proxy error")
            return -1

        if not forcedLogin:

            session_json = response.json()
            try:
                session = session_json["Session"]
            except KeyError:
                Logger.error(f"{self.logIdentifier} Error while getting session")
                return -1

            headers = {
                'User-Agent': 'rafflemobile/386 CFNetwork/1206 Darwin/20.1.0',
                'content-type': 'application/x-amz-json-1.1',
                'x-amz-target': 'AWSCognitoIdentityProviderService.RespondToAuthChallenge',
                'Connection': 'keep-alive',
            }

            data = {
                "ChallengeName": 'CUSTOM_CHALLENGE',
                "ChallengeResponses": {
                    "USERNAME": self.profile["email"],
                    "ANSWER": self.profile["password"],
                },
                "ClientId": '60skugd7dfshb9qerf70h38e2q',
                "Session": session,
            }

            Logger.info(f"{self.logIdentifier} Logging in")
            try:
                response = self.session.post('https://cognito-idp.eu-west-1.amazonaws.com/', headers=headers, json=data)
                if response.status_code != 200:
                    Logger.error("{} Error while login : {}".format(self.logIdentifier, response.status_code))
                    return -1
            except Exception as e:
                Logger.error("{} Error while login : {}".format(self.logIdentifier, str(e)))
                return -1

            try:
                access_token_json = response.json()
                accessToken = access_token_json['AuthenticationResult']['AccessToken']
                idToken = access_token_json['AuthenticationResult']['IdToken']
            except KeyError:
                Logger.error("Error while getting Access Token")
                return -1

        headers = {
            'amz-sdk-request': 'attempt=1; max=3',
            'Accept': '*/*',
            'x-amz-user-agent': 'aws-sdk-js-v3-react-native-@aws-sdk/client-cognito-identity/1.0.0-gamma.8 aws-amplify'
                                '/3.5.5 react-native',
            'Content-Type': 'application/x-amz-json-1.1',
            'Accept-Language': 'fr-fr',
            'User-Agent': 'rafflemobile/1 CFNetwork/1240.0.4 Darwin/20.5.0',
            'Connection': 'keep-alive',
            'x-amz-target': 'AWSCognitoIdentityService.GetId',
        }

        data = {"IdentityPoolId": "eu-west-1:e189bafd-8e13-4657-8800-68190ed2fac1",
                "Logins":
                    {"cognito-idp.eu-west-1.amazonaws.com/eu-west-1_8ywWI3Ia9": idToken
                     }
                }

        Logger.info(f"{self.logIdentifier} Connecting to database")
        try:
            response = self.session.post('https://cognito-identity.eu-west-1.amazonaws.com/', headers=headers,
                                         json=data)
        except Exception as e:
            Logger.error("{} Error while connecting to database : {}".format(self.logIdentifier, str(e)))
            return -1

        try:
            identity_json = response.json()
            identityId = identity_json["IdentityId"]
        except KeyError:
            Logger.error(f"{self.logIdentifier} Error while getting Database Information")
            return -1

        headers = {
            'amz-sdk-request': 'attempt=1; max=3',
            'Accept': '*/*',
            'x-amz-user-agent': 'aws-sdk-js-v3-react-native-@aws-sdk/client-cognito-identity/1.0.0-gamma.8 '
                                'aws-amplify/3.5.5 react-native',
            'Content-Type': 'application/x-amz-json-1.1',
            'Accept-Language': 'fr-fr',
            'User-Agent': 'rafflemobile/1 CFNetwork/1240.0.4 Darwin/20.5.0',
            'Connection': 'keep-alive',
            'x-amz-target': 'AWSCognitoIdentityService.GetCredentialsForIdentity',
        }

        data = {"IdentityId": identityId,
                "Logins":
                    {"cognito-idp.eu-west-1.amazonaws.com/eu-west-1_8ywWI3Ia9": idToken
                     }
                }

        Logger.info(f"{self.logIdentifier} Getting connection tokens")
        try:
            response = self.session.post('https://cognito-identity.eu-west-1.amazonaws.com/', headers=headers,
                                         json=data)
        except Exception as e:
            Logger.error(f"{self.logIdentifier} Error while Getting connection tokens : {str(e)}")
            return -1

        try:
            secretKey_json = response.json()
            self.accessKeyId = secretKey_json["Credentials"]["AccessKeyId"]
            self.secretKey = secretKey_json["Credentials"]["SecretKey"]
            sessionToken = secretKey_json["Credentials"]["SessionToken"]
        except KeyError:
            Logger.error(f"{self.logIdentifier} Error while getting connection tokens")
            return -1

        auth = AWSRequestsAuth(aws_access_key=self.accessKeyId,
                               aws_secret_access_key=self.secretKey,
                               aws_host='g1ik5r2vf5.execute-api.eu-west-1.amazonaws.com',
                               aws_region='eu-west-1',
                               aws_service='execute-api',
                               aws_token=sessionToken)

        data = {
               "shippingCountryCode": self.profile["country_code"],
               "shippingFirstName": self.profile["first_name"],
               "shippingLastName": self.profile["last_name"],
               "shippingAddress1": self.profile["house_number"] + " " + self.profile["street"],
               "shippingAddress2": self.profile["address2"],
               "shippingCity": self.profile["city"],
               "shippingZip": self.profile["zip"],
               "useOneAddress": True,
               "shippingState": "",
               "isDefault": True
            }

        Logger.info(f"{self.logIdentifier} Adding address")
        try:
            response = self.session.post('https://g1ik5r2vf5.execute-api.eu-west-1.amazonaws.com/Prod/api/signup',
                                         auth=auth,
                                         json=json.dumps(data))
            if response.status_code == 200:
                Logger.success(f"{self.logIdentifier} Address successfully added !")
            else:
                Logger.error("Error while adding address : {} / {}".format(response.status_code, response.text))
                return -1

        except Exception as e:
            Logger.error("Error while adding address to account : {}".format(str(e)))

        Logger.info(f"{self.logIdentifier} Adding credit card to account")

        from py_adyen_encrypt import encryptor

        ADYEN_KEY = "10001|EA3BAFD90ABF8CB6A9055C3081C01F20B978B64CA9A8F7256D251417CDB9CBFBA552BE30C6A6928673404D62CF878BAFA5DE80BD77E53546F68317FF13D1649CA2A1CE7F1B6FE3F314B01DC7DE62EE16E94D2C4313F29F4578026FBF349B1E1BD6F0F0BEDB3B32FDC1149F40D59BDD989972EFF8DEC42EFCCCEFD586A24175443AF5915EFB39558D333553F56BF34BEB5DA36EECC6527F21FD7A608595E9696C876315FBCF85AD9CF59B019682738882C42E25CBAE3A5A808F20E9F4A0D3C60994581A78A18295CFCC6119B4C3B5E142814A92D0457B78FE17B89C8DC0B359765865988B37674863EC0FE2E240427667FA58866196635DB93A0E1D0B3AA84907"

        enc = encryptor(adyen_public_key=ADYEN_KEY, adyen_version='_0_1_25')
        card = enc.encrypt_card(card=self.profile["cc_number"], cvv=self.profile["cc_cvv"],
                                month=self.profile["cc_expiration_month"], year=self.profile["cc_expiration_year"])

        headers = {
            'Content-Type': 'application/json',
            'Origin': 'https://eu.adyen.link',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Referer': 'https://eu.adyen.link/',
            'Accept-Language': 'fr-fr',
        }

        params = (
            ('d', 'PLEEF2BAECA4AFC4C8'),
        )

        data = {
           "riskData":{
              "clientData": "eyJ2ZXJzaW9uIjoiMS4wLjAiLCJkZXZpY2VGaW5nZXJwcmludCI6IjFCMk0yWThBc2cwMDAwMDAwMDAwMDAwMDAwS1piSVFqNmt6czAwMTAwMTE0NTZjVkI5NGlLekJHRktKcE1ZNHdNaDFCMk0yWThBc2cwMDA2QWNuY1hPcEtCMDAwMDBobjVYdjAwMDAweFBXVDBHVnBtN0dpaTJDRm5HSWM6MjAiLCJwZXJzaXN0ZW50Q29va2llIjpbXSwiY29tcG9uZW50cyI6eyJ1c2VyQWdlbnQiOiJhZjI5NmMzMzk1ZTU4YjdhY2ZiMmM0ZTQyZDExNWJhNiIsIndlYmRyaXZlciI6MCwibGFuZ3VhZ2UiOiJmci1mciIsImNvbG9yRGVwdGgiOjMyLCJwaXhlbFJhdGlvIjozLCJzY3JlZW5XaWR0aCI6ODEyLCJzY3JlZW5IZWlnaHQiOjM3NSwiYXZhaWxhYmxlU2NyZWVuV2lkdGgiOjgxMiwiYXZhaWxhYmxlU2NyZWVuSGVpZ2h0IjozNzUsInRpbWV6b25lT2Zmc2V0IjotMTIwLCJ0aW1lem9uZSI6IkV1cm9wZS9QYXJpcyIsInNlc3Npb25TdG9yYWdlIjoxLCJsb2NhbFN0b3JhZ2UiOjEsImluZGV4ZWREYiI6MSwiYWRkQmVoYXZpb3IiOjAsIm9wZW5EYXRhYmFzZSI6MCwicGxhdGZvcm0iOiJpUGhvbmUiLCJwbHVnaW5zIjoiMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAiLCJjYW52YXMiOiJmMGJmYTQzOWQ4NjhmYjRjNmU3NzVhZGZmZTMzNGM1ZSIsIndlYmdsIjoiMjBmNTY4ZDAwYmM5ZTFhZWViZDQzOGY1YWJhMGU3YzAiLCJ3ZWJnbFZlbmRvckFuZFJlbmRlcmVyIjoiQXBwbGUgSW5jLn5BcHBsZSBHUFUiLCJhZEJsb2NrIjowLCJoYXNMaWVkTGFuZ3VhZ2VzIjowLCJoYXNMaWVkUmVzb2x1dGlvbiI6MCwiaGFzTGllZE9zIjowLCJoYXNMaWVkQnJvd3NlciI6MCwiZm9udHMiOiI5YzVlZDFkMWY0ZGU2ZDgzNzA0ODRlZDU2MWU1NmNiNyIsImF1ZGlvIjoiMTJlOTU1YTQ4NWJjN2M0MWQwNDk4NDFjYTYyZGRkYmMiLCJlbnVtZXJhdGVEZXZpY2VzIjoiMTg2YWIyYWQ5Mjg0YTVkMWU3MjEwZjQwYzZiOGY1MWMifX0': '"
           },
           "conversionId": "05465f52-18a2-4303-a67b-fef70c9bb44a1631657734566161a698a16a564060693836372c2e6244e24e3fc72377d0e83dc0f4ce1eeb415",
           "paymentMethod": {
              "type": "scheme",
              "holderName": "",
              "encryptedExpiryMonth": card["month"],
              "encryptedExpiryYear": card["year"],
              "encryptedCardNumber": card["card"],
              "encryptedSecurityCode": card["cvv"],
              "brand": self.profile["cc_type"]
           },
           "browserInfo": {
              "acceptHeader": "*/*",
              "colorDepth": 32,
              "language": "fr-fr",
              "javaEnabled": False,
              "screenHeight": 812,
              "screenWidth": 375,
              "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
              "timeZoneOffset": -120
           },
           "clientStateDataIndicator": True
        }

        response = self.session.post('https://checkoutshopper-live.adyen.com/checkoutshopper/v68/paybylink/payments',
                                     headers=headers, params=params, json=data)

        Logger.debug("response from sending credit card : {}".format(response.text))

        if response.status_code == 200:
            try:
                errorCode = response.json()["resultCode"]
                if errorCode == "Refused":
                    Logger.error(f"{self.logIdentifier} Card refused by FootpatrolLaunches")
                    return -1
            except KeyError:
                Logger.error("Error while decoding response : {}".format(response.text))

            try:
                paymentData = response.json()["action"]["paymentData"]
                authorisationToken = response.json()["action"]["authorisationToken"]

                headers = {
                    'Content-Type': 'application/json',
                    'Origin': 'https://eu.adyen.link',
                    'Connection': 'keep-alive',
                    'Accept': 'application/json, text/plain, */*',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
                    'Referer': 'https://eu.adyen.link/',
                    'Accept-Language': 'fr-fr',
                }

                params = (
                    ('token', 'live_7G47GNRX4BCCJEX7VCJY6MHE7UVIUGIZ'),
                )

                data = {
                   "fingerprintResult": "eyJ0aHJlZURTQ29tcEluZCI6IlkifQ",
                   "paymentData": paymentData,
                }

                response = self.session.post(
                    'https://checkoutshopper-live.adyen.com/checkoutshopper/v1/submitThreeDS2Fingerprint',
                    headers=headers, params=params, data=data)

                if response.status_code == 200:
                    try:
                        authorisationToken2 = response.json()["authorisationToken"]
                        token = response.json()["token"]

                        dataToEncode = {"transStatus": "Y",
                                        "authorisationToken": authorisationToken}

                        import base64
                        message = str(dataToEncode)
                        message_bytes = message.encode('ascii')
                        threeDSResult = base64.b64encode(message_bytes).decode('utf-8')

                        headers = {
                            'Content-Type': 'application/json',
                            'Origin': 'https://eu.adyen.link',
                            'Connection': 'keep-alive',
                            'Accept': '*/*',
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
                            'Referer': 'https://eu.adyen.link/',
                            'Accept-Language': 'fr-fr',
                        }

                        params = (
                            ('d', 'PLEEF2BAECA4AFC4C8'),
                        )

                        data = {
                           "details":{
                              "threeDSResult": threeDSResult
                           }
                        }

                        response = self.session.post(
                            'https://checkoutshopper-live.adyen.com/checkoutshopper/v68/paybylink/paymentsDetails',
                            headers=headers, params=params, data=data)
                        if response.status_code == 200:
                            Logger.success(f"{self.logIdentifier} Card successfully added, profile is ready to enter raffles !")
                            return 1
                        else:
                            Logger.error(f"{self.logIdentifier} Error during last step")
                            return -1

                    except:
                        Logger.error(f"{self.logIdentifier} Second auth tokens not found ")
                        Logger.debug(response.text)
                        return -1

                else:
                    Logger.error("Error while setting up payment")
                    Logger.debug("{} / {}".format(response.status_code, response.text))
                    return -1

            except Exception as e:
                Logger.error("Error while adding credit card 2 : {}".format(str(e)))
                return -1
        else:
            Logger.error(f"{self.logIdentifier} Error while submitting payment !")
            Logger.debug("Response received : {} / {}".format(response.status_code, response.text))
            return -1

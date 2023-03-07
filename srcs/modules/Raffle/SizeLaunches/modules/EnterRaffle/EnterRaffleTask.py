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
from aws_requests_auth.aws_auth import AWSRequestsAuth
import random

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
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
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def executeTask(self):

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

        Logger.info("Initiating login")
        Logger.debug("Email : {}".format(self.profile["email"]))
        try:
            response = self.session.post('https://cognito-idp.eu-west-1.amazonaws.com/', headers=headers, json=data)
            if response.status_code != 200:
                Logger.error("Error while initiating login : {} / {}".format(response.status_code, response.text))
                return
        except Exception as e:
            Logger.error("Error while initiating login : {}".format(str(e)))
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error")
            return

        session_json = response.json()
        try:
            session = session_json["Session"]
        except KeyError:
            Logger.error("Error while getting session")
            return

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

        Logger.info("Logging in")
        try:
            response = self.session.post('https://cognito-idp.eu-west-1.amazonaws.com/', headers=headers, json=data)
            if response.status_code != 200:
                Logger.error("Error while login : {}".format(response.status_code))
                return -1
        except Exception as e:
            Logger.error("Error while login : {}".format(str(e)))
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

        Logger.info("Connecting to database")
        try:
            response = self.session.post('https://cognito-identity.eu-west-1.amazonaws.com/', headers=headers,
                                         json=data)
        except Exception as e:
            Logger.error("Error while connecting to database : {}".format(str(e)))
            return -1

        try:
            identity_json = response.json()
            identityId = identity_json["IdentityId"]
        except KeyError:
            Logger.error("Error while getting Database Information")
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

        Logger.info("Getting connection tokens")
        try:
            response = self.session.post('https://cognito-identity.eu-west-1.amazonaws.com/', headers=headers,
                                         json=data)
        except Exception as e:
            Logger.error("Error while Getting connection tokens : {}".format(str(e)))
            return -1

        try:
            secretKey_json = response.json()
            self.accessKeyId = secretKey_json["Credentials"]["AccessKeyId"]
            self.secretKey = secretKey_json["Credentials"]["SecretKey"]
            sessionToken = secretKey_json["Credentials"]["SessionToken"]
        except KeyError:
            Logger.error("Error while getting connection tokens")
            return -1

        auth = AWSRequestsAuth(aws_access_key=self.accessKeyId,
                               aws_secret_access_key=self.secretKey,
                               aws_host='g1ik5r2vf5.execute-api.eu-west-1.amazonaws.com',
                               aws_region='eu-west-1',
                               aws_service='execute-api',
                               aws_token=sessionToken)

        Logger.info("Getting user info")
        try:
            response = self.session.get('https://g1ik5r2vf5.execute-api.eu-west-1.amazonaws.com/Prod/api/account',
                                        auth=auth)
        except Exception as e:
            Logger.error("Error while Getting user info : {}".format(str(e)))
            return -1

        try:
            user_info_json = response.json()
            paymentId = user_info_json["Payment"]["id"]
            addy_list = user_info_json["Addresses"]
        except KeyError:
            Logger.error("Error while getting connection tokens")
            return -1

        addyId = "notfound"
        for addy in addy_list:
            if addy["isDefault"]:
                addyId = addy["id"]

        if addyId == "notfound":
            Logger.error("Addy details not found, stopping task")
            return -1

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'aws-amplify/3.5.5 react-native',
        }

        Logger.info("Getting raffle details")
        try:
            raffleDetails = self.session.get('https://g1ik5r2vf5.execute-api.eu-west-1.amazonaws.'
                                             'com/Prod/api/configurations',
                                             headers=headers)
        except Exception as e:
            Logger.error("Error while Getting raffle details : {}".format(str(e)))
            return -1

        try:
            rep = raffleDetails.json()
            wantedRaffle = "notfound"
            for elt in rep["configurations"]:
                if elt["configuration"]["raffleId"] == self.raffle["metadata"]["raffleId"]:
                    wantedRaffle = elt["configuration"]
            if wantedRaffle == "notfound":
                Logger.error("Raffle not found, stopping task.")
                return
            self.artNo = wantedRaffle["product"]["artNo"]
            size_list = wantedRaffle["sizes"]
            if self.profile["size"].lower() == "random":
                size_wanted = random.choice(size_list)["externalReference"]
            else:
                size_wanted = "notfound"
                for size in size_list:
                    size_conversions = size["conversions"]
                    for type in size_conversions:
                        if type["type"] == 'EU':
                            current_size = type["value"]
                            if str(current_size) == str(self.profile["size"]):
                                Logger.info("Size found")
                                size_wanted = size["externalReference"]
                if size_wanted == "notfound":
                    Logger.info("Size not found, getting random one")
                    size_wanted = random.choice(size_list)["externalReference"]
        except KeyError as e:
            Logger.error("Error while getting sizes, field {} not found".format(str(e)))
            return -1

        tSubmit = datetime.utcnow()
        self.amzdateSubmitMicroSeconds = (tSubmit.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))[:-4] + "Z"

        request_parameters = {
            "raffleId": self.raffle["metadata"]["raffleId"],
            "addressId": int(addyId),
            "paymentId": int(paymentId),
            "externalReference": size_wanted,
            "pickupLocation": self.profile["pickupLocation"],
            "reDrawAccepted": True,
            "artNo": self.artNo,
            "registeredAt": self.amzdateSubmitMicroSeconds
        }

        Logger.info("Submitting entry")
        try:
            response = self.session.post('https://g1ik5r2vf5.execute-api.eu-west-1.amazonaws.com/Prod/api/signup',
                                         auth=auth,
                                         json=request_parameters)
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1

        if response.status_code == 200:
            return 1
        else:
            Logger.error("Error while submitting entry : {} / {}".format(response.status_code, response.json()))
            return -1
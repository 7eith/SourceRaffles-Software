"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 27/09/2021 16:22:20                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from utilities import *
import random
from core.configuration.Configuration import Configuration
import requests

urlDb = "https://mugiwara-aio-db-default-rtdb.europe-west1.firebasedatabase.app/"
limitUsageParams = r"""?&orderBy="$key"&limitToFirst=1"""

class AccountGeneratorTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy)
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile, createAccounts=True) -> None:

        """ To change with config"""
        self.shapeRequestDelay = 4
        self.shapeDelay = 10

        """ Props """
        self.createAccounts: bool    = createAccounts
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict     = profile

        """ Store """
        self.logIdentifier: str      = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile['email'])
        self.state:         str     = "PENDING"
        self.success:       bool    = False
        self.retry:         int     = 0
        self.maxRetry:      int     = 10

        self.initSession()

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            self.executeTask()
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occurred when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False
            
    def endTask(self, isSuccess=False):
        if isSuccess:
            self.state = "SUCCESS"
            self.success = True
            Logger.success("Account successfully generated !")
        else:
            self.state = "FAILED"
            self.success = False
            Logger.error("Task failed")


    def executeTask(self):
        if self.createAccounts:
            self.create_account()
        else:
            self.getBearer(need_new_headers=True)
            
    def ShapeRequestSleep(self):
        if int(self.shapeRequestDelay) != 0:
            Logger.info("Sleeping during {} seconds before next step".format(self.shapeRequestDelay))
            time.sleep(self.shapeRequestDelay)

    def harvest(self, first=False):

        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/firebase.database"
        ]

        credentialsJson = {
            "type": "service_account",
            "project_id": "mugiwara-aio-db",
            "private_key_id": "62cac82ba84e644ac31ce76fc3d1acc37d4e5d03",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDnr2QrDZP8zKEu\nmkKz4xVoeOocHIuhsGHNAfKcq3PzS+4rvfyJZkJj+IXwEtjNuBahWQIRWHNcqBce\nabTsoZUWqKSii3DNsM0TScOpMVtnQrpoKLajzBaj8aimMmlSRLCpUu2cTVMKdJyR\n73q29ZYpuYzeLwbREmp7op6ECvea/3qqKh3XTwIEZY6HrkiExdyxXDwPau2iAH0u\n2tUvjxqmExFHd8QqfUIWbwkSOIU0LdJWtFHDDUMmflHLmkpVH8bJsq04lC09qHGU\n68BUxRfF4qV5GYgjYezIJTuvHgtBWUIDZ0v+e3ZXyNcQ4fPNe6FBkwkkMYM786Eg\nteHbxgI5AgMBAAECggEAGaDXqkGGwLycCc0rmr2AZT2W3AQ2V+zsbKKOBVGb8mpQ\nTstlz4cdyfQ4UK2tCNiXvEJdzbBklnfLkuQrjM907/w4tfhJwp8PmFYdDC63By2k\n9Beo2GafjIQTXUsPRnftuNVBDnypNmte1G/SucFh2ny5fexiyybH26RJ955E9IKf\nWhTuHjETU7/89EtB5+u59si777Fglg4cD06zs46LTBzKnLEuVZO3JNZ82olAL6tE\n9w1rGYKPhvlZHkBrMtzwLeZTCbXpAMCVBMUDXIY3F69HKQR2ntigTMoK/VXRpTBk\nYHJPIyuPvqzuewwYFRvf/RGUkP56gbROddcVAIm+lwKBgQD364hnMzBkdTcLFghX\n4EDpKXGxi9dbZP87voFhjGUzNMZw39kIrBa2Gb3abQDDuePR3+d9SbTJv7sfyicJ\nLyIUnK2E8j9L/t0OMo9wNXsO0sLtRSM4FQCM9UZN2OftyInRRB1mWfKDm15hcddq\nS8N0sFwwx+J3qkaxGTKTz53PywKBgQDvPGfmPQjlvqqPXqR3rCRpBCO46uP8eqv4\noHi0BWUqAGs8HfcDbzbd5Kg5QYs1rV7d7ziHUW++eNRRm2miLY+NzzYsdUOauE2B\nmXuT6+OEkMzPhEJRkE4Wn5EgCcZZ0jiQcjZCmrYCotNVOPeIxpAtziBYnS1ANsT2\nT1Hoab6tiwKBgQCnRMGWJ2JaFP+bOjVM3N/OsIil6pzVbBIMhB8U6r2Iy+2rUExF\nXp5AJKQEUBD4/V1pR7EOxgD1MagV7bViq+tJjuA/15W/N2h74L8ITP0G5kpf/Yqi\nlwD1GbNiaJsqwmfByjwvxzYpd1U5V66oaA+qlibNPr9cT4U8jayjL6vg+wKBgA5v\n88k2N7o9pmdei8hZEB1yTYGUU0viT0yCyqX6iV9ehRosqMKBTKtZaDmEVhVYMBhu\nnle0N20kN5PxMA/EdhxVu+w0626D3tGKZKXJn4JZhrKjRalMbxn4aTaowFqdUCKP\ncezVD1TbZKuI849ChGLvRI50dc2hQIOox8Wh1Ar/AoGBALBhw1k1t6/pvHX/PhQo\nwct6upP5rsCVFb4TK3Rx/HEpQbDcs2OFyh3BAINPcYp1aAvu/Z1vGt6hSWloPnLB\nTq1TF/6zlEKQMJB09Id88BqvET8uxDNudawdYn+yLJHh3yBuN9jkvIIYIwR5GizC\new00Y9ul4r4J2/OhmEO2ShB1\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-8grxk@mugiwara-aio-db.iam.gserviceaccount.com",
            "client_id": "101197561425469022752",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-8grxk%40mugiwara-aio-db.iam.gserviceaccount.com"
        }

        credentials = service_account.Credentials.from_service_account_info(
            credentialsJson, scopes=scopes)

        authed_session = AuthorizedSession(credentials)

        Logger.info("Handling Shape")
        url = urlDb + "/{}.json".format(Configuration().getConfiguration()["LicenseKey"]) + limitUsageParams
        PersHeadersJson = authed_session.get(url).json()
        if PersHeadersJson is not None:
            Logger.info("Getting sessions in personal database")
            headers_list = []
            for weirdId in PersHeadersJson:
                if PersHeadersJson[weirdId]:
                    headers_list.append(PersHeadersJson[weirdId])
            shape_headers = random.choice(headers_list)
            for name, value in PersHeadersJson.items():
                if value == shape_headers:
                    authed_session.delete(urlDb + "{}/{}.json".format(Configuration().getConfiguration()["LicenseKey"], name)).json()
            try:
                t = shape_headers["exj5WzXnUF-d"]
                t = shape_headers["exj5WzXnUF-b"]
                t = shape_headers["exj5WzXnUF-z"]
                t = shape_headers["exj5WzXnUF-f"]
                t = shape_headers["exj5WzXnUF-c"]
                t = shape_headers["exj5WzXnUF-a"]
            except KeyError:
                Logger.error("Unvalid session, retrying")
                return self.harvest()
            return shape_headers

        else:
            headers_json = authed_session.get(urlDb + "/.json" + limitUsageParams).json()
            headers_list = []
            if headers_json is None:
                Logger.error("Database is empty, please use the extension on the End website")
                return {
                        'exj5WzXnUF-b': '',
                        'exj5WzXnUF-a': '',
                        'exj5WzXnUF-c': '',
                        'exj5WzXnUF-d': '',
                        'exj5WzXnUF-f': '',
                        'exj5WzXnUF-z': ''
                }
            for weirdId in headers_json:
                if headers_json[weirdId]:
                    headers_list.append(headers_json[weirdId])
            shape_headers = random.choice(headers_list)
            for name, value in headers_json.items():
                if value == shape_headers:
                    authed_session.delete(urlDb + "/{}.json".format(name)).json()
            try:
                t = shape_headers["exj5WzXnUF-d"]
                t = shape_headers["exj5WzXnUF-b"]
                t = shape_headers["exj5WzXnUF-z"]
                t = shape_headers["exj5WzXnUF-f"]
                t = shape_headers["exj5WzXnUF-c"]
                t = shape_headers["exj5WzXnUF-a"]
            except KeyError:
                Logger.error("Unvalid session, retrying")
                return self.harvest()
            return shape_headers

    def emailAvailable(self):

        headers = {
            'authority': 'api2.endclothing.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
            'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
            'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
            'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
            'sec-gpc': '1',
            'origin': 'https://www.endclothing.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.endclothing.com/',
        }

        data = {"customerEmail": self.profile["email"]}

        try:
            response = self.session.post('https://api2.endclothing.com/rest/V1/customers/isEmailAvailable',
                                     headers=headers, data=data)
            if response.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.emailAvailable()
                return
            if response.status_code == 200:
                if "false" in response.text:
                    Logger.info("Email not available, not creating account and updating account details")
                    self.getBearer()
                    return
                else:
                    Logger.info("Email available, creating account...")
                    self.create_account()
                    return
        except Exception as e:
            Logger.error("Error during creation : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            self.endTask(isSuccess=False)
            return

    def create_account(self):
        self.shape_headers = self.harvest(first=True)
        Logger.info("Creating account")
        try:
            headers = {
                'authority': 'api2.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
                'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
                'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/92.0.4515.107 Safari/537.36',
                'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
                'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
                'sec-gpc': '1',
                'origin': 'https://www.endclothing.com',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.endclothing.com/',
                'accept-language': 'fr-FR,fr;q=0.9',
            }

            data = {
                "customer": {
                    "email": self.profile["email"],
                    "firstname": self.profile["first_name"],
                    "lastname": self.profile["last_name"],
                    "extension_attributes": {
                        "is_subscribed": False
                    }
                },
                "password": self.profile["password"]
            }

            r = self.session.post('https://api2.endclothing.com/rest/V1/customers', headers=headers, json=data)
            if r.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.create_account()
                return
            if r.status_code == 200:
                Logger.success("Account created")
        except Exception as e:
            Logger.error("Error during creation : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            self.endTask(isSuccess=False)
            return
        self.ShapeRequestSleep()
        self.getBearer()
        return

    def getBearer(self, need_new_headers=False):
        Logger.info("Getting Account Token")
        if need_new_headers:
            self.shape_headers = self.harvest()
        try:
            headers = {
                'authority': 'api2.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
                'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
                'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
                'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
                'sec-gpc': '1',
                'origin': 'https://www.endclothing.com',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.endclothing.com/',
                'accept-language': 'fr-FR,fr;q=0.9',
            }

            data = {
                "username": self.profile["email"],
                "password": self.profile["password"]
            }
            response = self.session.post('https://api2.endclothing.com/rest/V1/integration/customer/token',
                                         headers=headers,
                                         json=data)
            if response.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.getBearer(need_new_headers=True)
                return
            elif response.status_code == 200:
                self.bearer_token = response.text.replace('"', '')
            else:
                Logger.error("Error while logging in : \nstatus code : {} \n "
                              "response : {}".format(response.status_code, response.text))
                self.endTask(isSuccess=False)
                return
        except Exception as e:
            Logger.error("Error during login : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            self.endTask(isSuccess=False)
            return

        self.getCountries()
        return

    def getCountries(self):
        Logger.info("Getting Country informations")
        import requests
        country_list = requests.get("https://source-raffles-api.herokuapp.com/raffles/End").json()
        regionWanted = "notfound"

        for country in country_list:
            if country["country_name"] == self.profile["country"]:
                if country["available_regions"] is not None:
                    list_region = country['available_regions']
                    for region in list_region:
                        current_region = region["region"]
                        if current_region == self.profile["region_name"]:
                            regionWanted = region["region"]
                            self.regionName = region["region"]
                            self.region = region["region"]
                            self.region_code = region["region_code"]
                            self.region_id = region["region_id"]
                            self.countryCode = country["country_code"]
                            self.countryId = country["id"]
                else:
                    regionWanted = "notneeded"
                    self.region_code = self.profile["region_name"]
                    self.regionName = self.profile["region_name"]
                    self.region_id = 0
                    self.countryCode = country["country_code"]
                    self.countryId = country["id"]
        if regionWanted == "notfound":
            Logger.error("Region not found, stopping task")
            self.endTask(isSuccess=False)
            return
        self.getAccountInformations()
        return

    def getAccountInformations(self, need_new_headers=False, addy_saved=False):
        if need_new_headers:
            self.shape_headers = self.harvest()
        Logger.info("Getting account informations")
        try:
            headers = {
                'authority': 'api2.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'authorization': 'Bearer {}'.format(self.bearer_token),
                'accept': 'application/json, text/plain, */*',
                'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
                'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
                'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) '
                              'Chrome/92.0.4515.107 Safari/537.36',
                'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
                'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
                'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
                'sec-gpc': '1',
                'origin': 'https://launches.endclothing.com',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://launches.endclothing.com/',
                'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            r = self.session.get('https://api2.endclothing.com/rest/V1/customers/me', headers=headers)
            if r.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.getAccountInformations(need_new_headers=True)
                return
            if r.status_code != 200:
                Logger.error("Error while getting account informations : {} / {}".format(r.status_code, r.text))
                self.endTask(isSuccess=False)
                return

            account_info = r.json()
            self.customer_id = account_info["id"]
            self.addresses = account_info["addresses"]
            self.updated_at = account_info["updated_at"]
            self.created_at = account_info["created_at"]
            self.created_in = account_info["created_in"]
            self.email = account_info["email"]
            self.firstname = account_info["firstname"]
            self.lastname = account_info["lastname"]
            self.store_id = account_info["store_id"]
            self.website_id = account_info["website_id"]

            if addy_saved:
                for elt in self.addresses:
                    try:
                        if elt["default_billing"] or elt["default_shipping"]:
                            self.addyId = elt["id"]
                            self.updatePayment()
                            return
                    except KeyError:
                        Logger.error("Error while getting addressId, account badly set up")
                        self.endTask(isSuccess=False)
                        return
            elif self.profile["street"] != "":
                self.ShapeRequestSleep()
                self.updateShippingInformations()
                return
            else:
                Logger.info("Skipping update of shipping details")
                for elt in self.addresses:
                    try:
                        if elt["default_billing"] or elt["default_shipping"]:
                            self.addyId = elt["id"]
                            self.getAccessToken()
                            return
                    except KeyError:
                        Logger.error("Error while getting addressId, account badly set up")
                        self.endTask(isSuccess=False)
                        return
                self.getAccessToken()
                return

        except Exception as e:
            Logger.error("Error while getting account informations : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            self.endTask(isSuccess=False)
            return

    def updateShippingInformations(self, need_new_headers=False):
        if need_new_headers:
            self.shape_headers = self.harvest()
        Logger.info("Updating shipping / billing details")
        headers = {
            'authority': 'api2.endclothing.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'authorization': 'Bearer {}'.format(self.bearer_token),
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
            'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
            'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
            'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
            'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
            'sec-gpc': '1',
            'origin': 'https://www.endclothing.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.endclothing.com/',
            'accept-language': 'fr-FR,fr;q=0.9',
        }
        data = {
            "customer": {
                "id": self.customer_id,
                "group_id": 1,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "created_in": self.created_in,
                "email": self.email,
                "firstname": self.firstname,
                "lastname": self.lastname,
                "store_id": int(self.store_id),
                "website_id": int(self.website_id),
                "addresses": [
                    {
                        "country_id": self.countryCode,
                        "street": [
                            self.profile["street_number"] + " " + self.profile["street"],
                            self.profile["address2"]
                        ],
                        "telephone": self.profile["phone"],
                        "firstname": self.profile["first_name"],
                        "lastname": self.profile["last_name"],
                        "postcode": self.profile["zip"],
                        "city": self.profile["city"],
                        "default_billing": True,
                        "default_shipping": True,
                        "region": {
                            "region_id": self.region_id,
                            "region_code": self.region_code,
                            "region": self.regionName
                        }
                    }
                ],
                "disable_auto_group_change": 0,
                "extension_attributes": {
                    "storecredit_balance": 0
                },
                "custom_attributes": [
                    {
                        "attribute_code": "group",
                        "value": "1"
                    }
                ]
            }
        }
        try:
            response = self.session.put('https://api2.endclothing.com/rest/V1/customers/me',
                                        headers=headers,
                                        json=data)
            if response.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.updateShippingInformations(need_new_headers=True)
                return
            if response.status_code != 200:
                Logger.error("Error while updating account informations : {} / {}".format(response.status_code,
                                                                                           response.text))
                self.endTask(isSuccess=False)
                return
        except Exception as e:
            Logger.error("Error while updating shipping informations : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return
        except requests.exceptions.ProxyError:
            Logger.error("Proxy error, stopping task")
            self.endTask(isSuccess=False)
            return

        if self.profile["cc_number"] == "":
            Logger.info("Not updating payment informations")
            self.endTask(isSuccess=True)
            return
        else:
            self.ShapeRequestSleep()
            self.getAccessToken()
            return

    def getAccessToken(self, need_new_headers=False):
        if need_new_headers:
            self.shape_headers = self.harvest()
        Logger.info("Getting access token")
        headers = {
            'authority': 'api2.endclothing.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
            'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
            'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
            'exj5wzxnuf-d': self.shape_headers["exj5WzXnUF-d"],
            'exj5wzxnuf-c': self.shape_headers["exj5WzXnUF-c"],
            'exj5wzxnuf-a': self.shape_headers["exj5WzXnUF-a"],
            'sec-gpc': '1',
            'origin': 'https://www.endclothing.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.endclothing.com/',
            'accept-language': 'fr-FR,fr;q=0.9',
        }
        params = (
            ('websiteId', self.website_id),
        )
        response = self.session.get('https://api2.endclothing.com/rest/V1/end/braintree/clienttoken',
                                    headers=headers,
                                    params=params)
        if response.status_code == 416:
            Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
            time.sleep(self.shapeDelay)
            self.getAccessToken(need_new_headers=True)
            return
        if response.status_code != 200:
            Logger.error("Error while getting access token : {} / {}".format(response.status_code, response.text))
            self.endTask(isSuccess=False)

        tokenb64 = response.text.replace('"', "")

        import base64
        import json
        token_decoded = base64.b64decode(tokenb64).decode('utf-8')
        auth_token = json.loads(token_decoded)['authorizationFingerprint']

        data = {
            "clientSdkMetadata": {
                "source": "client",
                "integration": "custom",
                "sessionId": "51f9938a-dd56-4969-aa29-c485e7a397a0"
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input)"
                     " { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData "
                     "{ prepaid healthcare debit durbinRegulated commercial payroll issuingBank "
                     "countryOfIssuance productId } } } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": self.profile["cc_number"],
                        "expirationMonth": self.profile["cc_month"],
                        "expirationYear": self.profile["cc_year"],
                        "cvv": self.profile["cc_cvv"]
                    },
                    "options": {
                        "validate": False
                    }
                }
            },
            "operationName": "TokenizeCreditCard"
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'Authorization': 'Bearer {}'.format(auth_token),
            'Braintree-Version': '2018-05-10',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Sec-GPC': '1',
            'Origin': 'https://assets.braintreegateway.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://assets.braintreegateway.com/',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }
        Logger.info("Getting CC token")
        response = self.session.post('https://payments.braintree-api.com/graphql', headers=headers, json=data)
        json_braintree = response.json()
        self.token_nonce = json_braintree["data"]["tokenizeCreditCard"]["token"]
        self.ShapeRequestSleep()
        self.updatePayment(first=True)
        return

    def updatePayment(self, need_new_headers=False, first=False):
        if need_new_headers:
            self.shape_headers = self.harvest()
        Logger.info("Saving payment method")
        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Authorization': 'Bearer {}'.format(self.bearer_token),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'exj5WzXnUF-b': self.shape_headers["exj5WzXnUF-b"],
            'exj5WzXnUF-z': self.shape_headers["exj5WzXnUF-z"],
            'exj5WzXnUF-f': self.shape_headers["exj5WzXnUF-f"],
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'exj5WzXnUF-d': self.shape_headers["exj5WzXnUF-d"],
            'exj5WzXnUF-c': self.shape_headers["exj5WzXnUF-c"],
            'exj5WzXnUF-a': self.shape_headers["exj5WzXnUF-a"],
            'Sec-GPC': '1',
            'Origin': 'https://www.endclothing.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.endclothing.com/',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }
        if first:
            Logger.info("Getting Address Id")
            self.getAccountInformations(addy_saved=True)
            return

        data = {
            "customer_id": self.customer_id,
            "website_id": str(self.website_id),
            "default_payment": True,
            "payment_method_nonce": self.token_nonce,
            "device_data": '{\"device_session_id\":\"66d1dadc2373a67b9ab09688bb26330f\",\"fraud_merchant_id\":\"600810\",\"correlation_id\":\"ddeb17e6cb3680c0a70b2020e7737b12\"}',
            "billing_address": {
                  "id": self.addyId,
                  "firstName": self.firstname,
                  "lastName": self.lastname,
                  "telephone": self.profile["phone"],
                  "street1": self.profile["street"],
                  "city": self.profile["city"],
                  "regionName": self.regionName,
                  "regionId": int(self.region_id),
                  "postCode": self.profile["zip"],
                  "countryId": self.countryId,
                  "countryCode": self.countryCode,
                  "braintreeAddressId": None
               }
            }

        SaveCard = self.session.post('https://launches-api.endclothing.com/api/payment-methods',
                                     headers=headers,
                                     json=data)
        if SaveCard.status_code == 416:
            Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
            time.sleep(self.shapeDelay)
            self.updatePayment(need_new_headers=True)
            return
        elif SaveCard.status_code == 201:
            self.endTask(isSuccess=True)
            return
        elif SaveCard.status_code in [500, 501, 502]:
            Logger.error("Error while adding card entry : {} / {}".format(SaveCard.status_code, SaveCard.text))
            Logger.info("Retrying to submit after 30 seconds sleep")
            time.sleep(30)
            self.updatePayment()
            return
        else:
            self.endTask(isSuccess=False)
            return


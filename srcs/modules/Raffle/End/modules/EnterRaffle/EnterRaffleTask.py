"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 03:29:24                                     """
"""   Updated: 11/09/2021 17:29:56                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from utilities import *
import json
from bs4 import BeautifulSoup
import random
from core.configuration.Configuration import Configuration

urlDb = "https://mugiwara-aio-db-default-rtdb.europe-west1.firebasedatabase.app/"
limitUsageParams = r"""?&orderBy="$key"&limitToFirst=1"""

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

        if Configuration().getConfiguration()["ProxyLess"] == False:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy)
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

    def __init__(self, index, taskNumber, profile, raffleList) -> None:

        """ To fix from config """
        self.shapeDelay = 10
        self.shapeRequestDelay = 3

        """ Props """
        self.index:         int     = index + 1
        self.taskNumber:    int     = taskNumber
        self.profile:       dict     = profile
        self.raffleList:        dict     = raffleList

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
            # ProxyManager().banProxy(self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception occurred while running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def endTask(self, isSuccess=False):
        if isSuccess:
            Logger.success("Task ended with success !")
            self.state = "SUCCESS"
            self.success = True
        else:
            Logger.error("Task failed.")
            self.state = "FAILED"
            self.success = False

    def executeTask(self):
        self.submit()

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

    def ShapeRequestSleep(self):
        self.shapeRequestDelay = 4
        if int(self.shapeRequestDelay) != 0:
            Logger.info("Sleeping during {} seconds before next step".format(self.shapeRequestDelay))
            time.sleep(self.shapeRequestDelay)

    def login(self):

        Logger.debug("Initiating task to enter {}".format(self.raffleList))

        self.shape_headers = self.harvest()
        Logger.info("Logging into account")
        try:
            headers = {
                'authority': 'api2.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'accept': 'application/json, text/plain, */*',
                'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
                'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
                'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/92.0.4515.107 Safari/537.36',
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

            data = {"username": self.profile["email"],
                    "password": self.profile["password"]}

            r = self.session.post('https://api2.endclothing.com/rest/V1/integration/customer/token',
                                  headers=headers,
                                  json=data)
            if r.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.login()
                return
            if r.status_code != 200:
                Logger.error("Error while logging in : {} / {}".format(r.status_code, r.text))
                self.endTask(isSuccess=False)
                return

            self.bearer_token = r.text.replace('"', '')

        except Exception as e:
            Logger.error("Error while logging into account : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return

        self.ShapeRequestSleep()
        self.getAccountInformations()

    def getAccountInformations(self, need_new_headers=False):

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
                self.login()
                return
            if r.status_code != 200:
                Logger.error("Error while getting account informations : {} / {}".format(r.status_code, r.text))
                self.endTask(isSuccess=False)
                return

            try:
                account_info = r.json()
                self.customer_id = account_info["id"]
                self.default_billing = account_info["default_billing"]
                self.default_shipping = account_info["default_shipping"]
                self.addresses = account_info["addresses"]
                self.website_id = account_info["website_id"]
            except KeyError:
                Logger.error("Error while getting account informations, your account is not set up correctly")
                self.endTask(isSuccess=False)
                return

            for elt in self.addresses:
                try:
                    if elt["default_billing"]:
                        self.postalcode = elt['postcode']
                        self.street = elt["street"][0]
                except KeyError:
                    try:
                        if elt["default_billing"]:
                            self.postalcode = elt['postcode']
                            self.street = elt["street"][0]
                    except KeyError:
                        addy_choice = random.choice(self.addresses)
                        self.postalcode = addy_choice['postcode']
                        self.street = addy_choice["street"][0]
        except Exception as e:
            Logger.error("Error while getting account informations : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return

        self.ShapeRequestSleep()
        self.getPaymentInformations()

    def getPaymentInformations(self, need_new_headers=False):

        if need_new_headers:
            self.shape_headers = self.harvest()

        Logger.info("Getting payment informations")
        try:
            headers = {
                'authority': 'launches-api.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'authorization': 'Bearer {}'.format(self.bearer_token),
                'accept': 'application/json, text/plain, */*',
                'exj5wzxnuf-b': self.shape_headers["exj5WzXnUF-b"],
                'exj5wzxnuf-z': self.shape_headers["exj5WzXnUF-z"],
                'exj5wzxnuf-f': self.shape_headers["exj5WzXnUF-f"],
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) '
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

            r = self.session.get('https://launches-api.endclothing.com/api/payment-methods', headers=headers)
            Logger.debug(r.json())
        except Exception as e:
            Logger.error("Error while getting payment informations (request) : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return

        try:
            if r.status_code == 416:
                Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                time.sleep(self.shapeDelay)
                self.getPaymentInformations(need_new_headers=True)
                return
            elif r.status_code != 200:
                Logger.error("Error while getting account informations : {} / {}".format(r.status_code, r.text))
                self.endTask(isSuccess=False)
                return
            else:
                payment_method_json = r.json()
                self.payment_token = payment_method_json[0]["entity_id"]
        except Exception as e:
            Logger.error("Error while getting payment informations : {}".format(str(e)))
            self.endTask(isSuccess=False)
            return

        Logger.debug("Successfully received payment informations")
        self.getSizes()

    def getSizes(self):

        Logger.info("Getting sizes")

        Logger.debug(self.raffleList)
        self.sizeDict = {}

        for raffleInfo in self.raffleList:

            try:
                metadata = raffleInfo["metadata"][0]
                Logger.debug("Weird thing about metadata format")
                Logger.info("Getting sizes for link : {}".format(metadata["entryUrl"]))
                raffleLink = metadata["entryUrl"]
            except:
                Logger.info("Getting sizes for link : {}".format(raffleInfo["metadata"]["entryUrl"]))
                raffleLink = raffleInfo["metadata"]["entryUrl"]

            headers = {
                'authority': 'launches.endclothing.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/92.0.4515.131 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
                          ',application/signed-exchange;v=b3;q=0.9',
                'sec-gpc': '1',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
            }

            try:
                response = self.session.get(raffleLink, headers=headers)

                html = BeautifulSoup(response.text, 'html.parser')
                review_info_array = html.select('script[id="__NEXT_DATA__"]')  # array of all review info scripts
                info_dict = json.loads(review_info_array[0].string)  # using just one for simplicity
                size_list = info_dict["props"]["initialProps"]["pageProps"]["product"]["productSizes"]

                if self.profile["size"].lower() == "random":
                    self.size_wanted = random.choice(size_list)["id"]
                    self.sizeDict[raffleInfo["name"]] = self.size_wanted
                else:
                    self.size_wanted = "notfound"
                    for size_info in size_list:
                        if size_info["sizeDescription"] == "UK {}".format(self.profile["size"]):
                            self.size_wanted = size_info["id"]
                            self.sizeDict[raffleInfo["name"]] = self.size_wanted
                            Logger.info("Size found")
                    if self.size_wanted == "notfound":
                        Logger.info("Size not found, taking a random one")
                        self.size_wanted = random.choice(size_list)["id"]
                        self.sizeDict[raffleInfo["name"]] = self.size_wanted
            except Exception as e:
                Logger.error("Error while scraping sizes : {}".format(str(e)))
                self.endTask(isSuccess=False)
                return

        self.ShapeRequestSleep()
        self.submitEntry()

    def submitEntry(self, need_new_headers=False):

        while len(self.raffleList) != 0:

            raffleInfo = random.choice(self.raffleList)
            Logger.info("Submitting entry for {}".format(raffleInfo["name"]))

            if need_new_headers:
                self.shape_headers = self.harvest()

            try:
                cookies = {
                    'user_token': self.bearer_token,
                }

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
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) '
                                  'Chrome/92.0.4515.107 Safari/537.36',
                    'exj5WzXnUF-d': self.shape_headers["exj5WzXnUF-d"],
                    'exj5WzXnUF-c': self.shape_headers["exj5WzXnUF-c"],
                    'exj5WzXnUF-a': self.shape_headers["exj5WzXnUF-a"],
                    'Sec-GPC': '1',
                    'Origin': 'https://launches.endclothing.com',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://launches.endclothing.com/',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                }

                data = {
                    "customer_id": self.customer_id,
                    "product_size_id": self.sizeDict[raffleInfo["name"]],
                    "shipping_address_id": self.default_shipping,
                    "billing_address_id": self.default_billing,
                    "payment_method_id": self.payment_token,
                    "shipping_method_id": 238, ## static for the classic delivery
                    "website_id": int(self.website_id),
                    "postcode": self.postalcode,
                    "street": self.street,
                    "subscription_origin": "web"
                }

                r = self.session.post('https://launches-api.endclothing.com/api/subscriptions',
                                      headers=headers,
                                      cookies=cookies,
                                      json=data)

                if r.status_code == 416:
                    Logger.error("Shape banned, rotating session after {} seconds sleeping".format(self.shapeDelay), removeEnd=True)
                    time.sleep(self.shapeDelay)
                    self.submitEntry(need_new_headers=True)
                    return

                elif r.status_code == 201:
                    Logger.success("Entry successful for {}".format(raffleInfo["name"]))
                    self.raffleList.remove(raffleInfo)
                    Logger.info("Removed {} from raffles to enter".format(raffleInfo["name"]))

                elif r.status_code == 403:
                    Logger.success("Payment Information already used, entry already submitted for : {}".format(raffleInfo["name"]))
                    self.raffleList.remove(raffleInfo)
                    Logger.info("Removed {} from raffles to enter".format(raffleInfo["name"]))

                elif r.status_code in [500, 501, 502]:
                    Logger.error("Error while submitting entry : {} / {}".format(r.status_code, r.text))
                    Logger.info("Retrying to submit after 30 seconds sleep")
                    time.sleep(30)
                    self.submitEntry()
                    return
                else:
                    Logger.error("Error while submitting entry : {} / {} for raffle {}".format(r.status_code, r.text, raffleInfo["name"]))
                    self.raffleList.remove(raffleInfo)
                    Logger.info("Removed {} from raffles to enter".format(raffleInfo["name"]))
            except Exception as e:
                Logger.error("Error while submitting entry : {} for raffle : {}".format(str(e), raffleInfo["name"]))
                self.raffleList.remove(raffleInfo)
                Logger.info("Removed {} from raffles to enter".format(raffleInfo["name"]))
        self.endTask(isSuccess=True)
        return

    def submit(self):
        self.login()

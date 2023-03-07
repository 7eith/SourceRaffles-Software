"""********************************************************************"""
"""                                                                    """
"""   [AccountGenerator] AccountGeneratorTask.py                       """
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
import uuid
from requests.exceptions import ProxyError
from core.configuration.Configuration import Configuration


class AccountGeneratorTask:
    
    def initSession(self):

        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
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
        
        self.initSession()

        Logger.info(f"{self.logIdentifier} Starting Task for {self.profile['email']}!")
        
        try:
            
            self.executeTask()
            self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)
            self.profile['status'] = self.state

        except Exception as error:
            Logger.error(f"{self.logIdentifier} Exception has occured when running task!")
            Logger.error(str(error))

            self.profile['status'] = "FAILED"
            self.success = False

    def executeTask(self):
        
        status: int = self.createAccount()

        if (status == 1):
            self.retry = 0

            Logger.success(f"{self.logIdentifier} Successfully created account ! ")

            self.state = "SUCCESS"
            self.success = True

        else:
            self.state = "FAILED"
            self.success = False

    def createAccount(self):

        deviceID = str(uuid.uuid4()).upper()

        sessURL = 'https://ms-api.sivasdescalzo.com/api/locales'

        sessHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.3',
            'app-version': '2.1.1',
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': 'SVDApp/2002252216 CFNetwork/1209 Darwin/20.2.0',
            'bundle-version': '28',
            'Connection': 'keep-alive'
        }

        try:
            r = self.session.get(sessURL, headers=sessHeaders)
            if r.status_code != 200:
                Logger.error("Error while getting main page, code : {}".format(r.status_code))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting main page : {}".format(str(e)))
            return -1

        url = "https://ms-api.sivasdescalzo.com/api/customers"

        loginHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.3',
            'app-version': '2.1.1',
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': 'SVDApp/2002252216 CFNetwork/1209 Darwin/20.2.0',
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }

        data = {
            "customer": {
                "email": self.profile["email"],
                "lastname": self.profile["last_name"],
                "password": self.profile["password"],
                "is_subscribed": False,
                "firstname": self.profile["first_name"]
            }
        }

        Logger.info("Creating account")
        try:
            r = self.session.post(url, json=data, headers=loginHeaders)
            if r.status_code != 200:
                Logger.error("Error while creating account, code : {} / {}".format(r.status_code, r.text))
                return -1
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while creating account : {}".format(str(e)))
            return -1

        Logger.info("Account created, saving address details")

        token = r.json().get("customer_data")["token"]

        Logger.info("Getting region informations")

        try:

            headers = {
                'Accept': 'application/json',
                'device-os': 'I-iOS 15.0.2',
                'app-version': '2.1.2',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'store-code': 'en',
                'User-Agent': 'SVDApp/2002252228 CFNetwork/1312 Darwin/21.0.0',
                'Connection': 'keep-alive',
                'bundle-version': '31',
            }

            r = requests.get('https://ms-api.sivasdescalzo.com/api/regions/{}'.format(self.profile["country_code"]), headers=headers)
            if r.status_code != 200:
                Logger.error("Error while getting region informations, code : {}".format(r.status_code))
                return -1
        except Exception as e:
            Logger.error("Error while getting region informations : {}".format(str(e)))

        try:
            Logger.debug("Response : {}".format(r.json()))
            regionInfo = [region for region in r.json() if region["name"] == self.profile["region"]][0]
            self.regionId = regionInfo["id"]
        except IndexError:
            Logger.error("Error : Region not found, please check the name (and spelling of the region wanted)")
            return -1
        except Exception as e:
            Logger.error("Error while finding region : {}".format(str(e)))
            return -1

        addy_payload = {
            "address": {
                "street": self.profile["street"],
                "city": self.profile["city"],
                "region": self.profile["region"],
                "lastname": self.profile["first_name"],
                "firstname": self.profile["first_name"],
                "postcode": self.profile["zip"],
                "telephone": self.profile["phone"],
                "country_id": self.profile["country_code"],
                "region_id": self.regionId
            }
        }

        updatedHeaders = {
            'Host': 'ms-api.sivasdescalzo.com',
            'Pragma': 'no-cache',
            'Accept': 'application/json',
            'device-os': 'I-iOS 14.3',
            'Authorization': 'Bearer ' + token,
            'app-version': '2.1.1',
            'device-id': deviceID,
            'Accept-Language': 'de-de',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'store-code': 'en',
            'User-Agent': 'SVDApp/2002252216 CFNetwork/1209 Darwin/20.2.0',
            'bundle-version': '28',
            'Connection': 'keep-alive',
        }

        try:
            r = self.session.post('https://ms-api.sivasdescalzo.com/api/customers/addresses', headers=updatedHeaders,
                                  json=addy_payload)
            if r.status_code == 200:
                return 1
            else:
                Logger.error("Error while saving address : {} / {}".format(r.status_code, r.text))
        except ProxyError:
            Logger.error("Proxy error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while creating account : {}".format(str(e)))
            return -1
if __name__ == '__main__':
    regions = [{'id': '182', 'name': 'Ain'}, {'id': '183', 'name': 'Aisne'}, {'id': '184', 'name': 'Allier'}, {'id': '185', 'name': 'Alpes-de-Haute-Provence'}, {'id': '187', 'name': 'Alpes-Maritimes'}, {'id': '188', 'name': 'Ardèche'}, {'id': '189', 'name': 'Ardennes'}, {'id': '190', 'name': 'Ariège'}, {'id': '191', 'name': 'Aube'}, {'id': '192', 'name': 'Aude'}, {'id': '193', 'name': 'Aveyron'}, {'id': '249', 'name': 'Bas-Rhin'}, {'id': '194', 'name': 'Bouches-du-Rhône'}, {'id': '195', 'name': 'Calvados'}, {'id': '196', 'name': 'Cantal'}, {'id': '197', 'name': 'Charente'}, {'id': '198', 'name': 'Charente-Maritime'}, {'id': '199', 'name': 'Cher'}, {'id': '200', 'name': 'Corrèze'}, {'id': '201', 'name': 'Corse-du-Sud'}, {'id': '203', 'name': "Côte-d'Or"}, {'id': '204', 'name': "Côtes-d'Armor"}, {'id': '205', 'name': 'Creuse'}, {'id': '261', 'name': 'Deux-Sèvres'}, {'id': '206', 'name': 'Dordogne'}, {'id': '207', 'name': 'Doubs'}, {'id': '208', 'name': 'Drôme'}, {'id': '273', 'name': 'Essonne'}, {'id': '209', 'name': 'Eure'}, {'id': '210', 'name': 'Eure-et-Loir'}, {'id': '211', 'name': 'Finistère'}, {'id': '212', 'name': 'Gard'}, {'id': '214', 'name': 'Gers'}, {'id': '215', 'name': 'Gironde'}, {'id': '250', 'name': 'Haut-Rhin'}, {'id': '202', 'name': 'Haute-Corse'}, {'id': '213', 'name': 'Haute-Garonne'}, {'id': '225', 'name': 'Haute-Loire'}, {'id': '234', 'name': 'Haute-Marne'}, {'id': '252', 'name': 'Haute-Saône'}, {'id': '256', 'name': 'Haute-Savoie'}, {'id': '269', 'name': 'Haute-Vienne'}, {'id': '186', 'name': 'Hautes-Alpes'}, {'id': '247', 'name': 'Hautes-Pyrénées'}, {'id': '274', 'name': 'Hauts-de-Seine'}, {'id': '216', 'name': 'Hérault'}, {'id': '217', 'name': 'Ille-et-Vilaine'}, {'id': '218', 'name': 'Indre'}, {'id': '219', 'name': 'Indre-et-Loire'}, {'id': '220', 'name': 'Isère'}, {'id': '221', 'name': 'Jura'}, {'id': '222', 'name': 'Landes'}, {'id': '223', 'name': 'Loir-et-Cher'}, {'id': '224', 'name': 'Loire'}, {'id': '226', 'name': 'Loire-Atlantique'}, {'id': '227', 'name': 'Loiret'}, {'id': '228', 'name': 'Lot'}, {'id': '229', 'name': 'Lot-et-Garonne'}, {'id': '230', 'name': 'Lozère'}, {'id': '231', 'name': 'Maine-et-Loire'}, {'id': '232', 'name': 'Manche'}, {'id': '233', 'name': 'Marne'}, {'id': '235', 'name': 'Mayenne'}, {'id': '236', 'name': 'Meurthe-et-Moselle'}, {'id': '237', 'name': 'Meuse'}, {'id': '238', 'name': 'Morbihan'}, {'id': '239', 'name': 'Moselle'}, {'id': '240', 'name': 'Nièvre'}, {'id': '241', 'name': 'Nord'}, {'id': '242', 'name': 'Oise'}, {'id': '243', 'name': 'Orne'}, {'id': '257', 'name': 'Paris'}, {'id': '244', 'name': 'Pas-de-Calais'}, {'id': '245', 'name': 'Puy-de-Dôme'}, {'id': '246', 'name': 'Pyrénées-Atlantiques'}, {'id': '248', 'name': 'Pyrénées-Orientales'}, {'id': '251', 'name': 'Rhône'}, {'id': '253', 'name': 'Saône-et-Loire'}, {'id': '254', 'name': 'Sarthe'}, {'id': '255', 'name': 'Savoie'}, {'id': '259', 'name': 'Seine-et-Marne'}, {'id': '258', 'name': 'Seine-Maritime'}, {'id': '275', 'name': 'Seine-Saint-Denis'}, {'id': '262', 'name': 'Somme'}, {'id': '263', 'name': 'Tarn'}, {'id': '264', 'name': 'Tarn-et-Garonne'}, {'id': '272', 'name': 'Territoire-de-Belfort'}, {'id': '277', 'name': "Val-d'Oise"}, {'id': '276', 'name': 'Val-de-Marne'}, {'id': '265', 'name': 'Var'}, {'id': '266', 'name': 'Vaucluse'}, {'id': '267', 'name': 'Vendée'}, {'id': '268', 'name': 'Vienne'}, {'id': '270', 'name': 'Vosges'}, {'id': '271', 'name': 'Yonne'}, {'id': '260', 'name': 'Yvelines'}]
    for region in regions:
        print(region["name"])
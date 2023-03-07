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
import requests
from requests.exceptions import ProxyError
import random
import json
from bs4 import BeautifulSoup
from services.captcha import CaptchaHandler
from utilities import *

class EnterRaffleTask:

    def initSession(self):

        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
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
        self.raffleLink: str = raffle

        """ Adding email to profile """
        self.profile["email"] = "Task-{}".format(taskNumber)

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.proxyLess = False

        """ Utilities """
        self.initSession()

        try:

            status = self.enter_typeform()

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
                f"{self.logIdentifier} Exception occurred while running task!"
            )

            Logger.error(str(error))

            self.profile["status"] = "FAILED"
            self.success = False

    def bot_typeform(self, answers_data, form_id, authority='form.typeform.com'):
        authority = authority

        headers_to_start = {
            'authority': authority,
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                      'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-gpc': '1',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
        }

        try:
            self.session.get('https://{}/to/{}'.format(authority, form_id), headers=headers_to_start)
        except ProxyError:
            Logger.error("Proxy error, stopping...")
            return
        except Exception as e:
            Logger.error("Error while starting submission : {}".format(str(e)))
            return -1

        Logger.info("Generating session")

        headers = {
            'authority': authority,
            'content-length': '0',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-gpc': '1',
            'origin': 'https://' + authority,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://{}/to/{}'.format(authority, form_id),
            'accept-language': 'en-US,en;q=0.9',
        }

        try:
            response = self.session.post('https://{}/forms/{}/start-submission'.format(authority, form_id), headers=headers)
        except Exception as e:
            Logger.error("Error while creating session : {}".format(str(e)))
            return -1

        try:
            rep_json = response.json()
            signature = rep_json["signature"]
            landed_at = rep_json["submission"]["landed_at"]
        except KeyError:
            Logger.error("Error while accessing first page : blocked by site")
            return -1

        headers = {
            'authority': authority,
            'accept': 'application/json',
            'content-type': 'application/json; charset=UTF-8',
            'sec-gpc': '1',
            'origin': 'https://' + authority,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://{}/to/{}'.format(authority, form_id),
            'accept-language': 'en-US,en;q=0.9',
        }

        Logger.info("Sleeping before submitting")
        time.sleep(random.randint(1, 5))
        payload = {"signature": signature, "landed_at": landed_at, "form_id": form_id, "answers": answers_data}

        Logger.info("Submitting...")
        try:
            response = self.session.post('https://{}/forms/{}/complete-submission'.format(authority, form_id),
                                         headers=headers, json=payload)
        except ProxyError:
            Logger.error("Proxy error, stopping...")
            return -1
        except Exception as e:
            Logger.error("Error while submitting : {}".format(str(e)))
            return -1
        try:
            rep = response.json()["type"]
            if rep == "completed":
                Logger.success("Entry submitted")
                return 1
            else:
                Logger.error('Error with submission \n' + str(response.json()))
                return -1
        except KeyError:
            Logger.error('Error with submission \n' + str(response.json()))
            return -1

    def get_type(self, type):
        if type == "short_text":
            return "text"
        elif type == "long_text":
            return "text"
        elif type == "email":
            return "email"
        elif type == "dropdown":
            return "text"
        elif type == "date":
            return "date"
        elif type == "phone_number":
            return "phone_number"
        elif type == "multiple_choice":
            return "choices"
        else:
            return None

    def enter_typeform(self):

        try:
            r = requests.get(self.raffleLink)
            soup = BeautifulSoup(r.content, "html.parser")
            scripts = soup.find_all("script")
            script = str(scripts[2])
            jsonData = script.split("form: ")[1].split("messages:")[0].rsplit(',', 1)[0]
            jsonData = json.loads(jsonData)

            fieldDict = {}
            for field in jsonData["fields"]:
                id = field['id']
                type = field['type']
                name = field['title']
                fieldDict[name] = {}
                fieldDict[name]["id"] = id
                fieldDict[name]["type"] = type
                if type in ["multiple_choice", "dropdown"]:
                    fieldDict[name]["choices"] = field["properties"]["choices"]
            for elt in fieldDict:
                Logger.debug(elt)
                Logger.debug(fieldDict[elt])
            answers = []
            for title, value in self.profile.items():
                Logger.debug("handling {} / {} field".format(title, value))
                if title == "email" or title == "status" or title == "Product":
                    pass
                else:
                    name = title
                    id = fieldDict[name]["id"]
                    type = fieldDict[name]["type"]
                    other_type = self.get_type(type)
                    if other_type:
                        if other_type == "choices":
                            try:
                                choices = fieldDict[name]['choices']
                                if value.lower() == "random":
                                    choiceInfo = random.choice(choices)
                                else:
                                    choiceInfo = "notfound"
                                    for choice in choices:
                                        if choice["id"] == value:
                                            choiceInfo = choice
                                    if choiceInfo == "notfound":
                                        Logger.error("Error while choosing answers for field : {}, id not found".format(name))
                                        return None
                                value = [{"id": choiceInfo["id"],
                                          "label": choiceInfo["label"]}]
                                answers.append(
                                    {'field': {"id": id, 'type': type}, 'type': other_type, other_type: value})

                            except Exception as e:
                                Logger.error("Error while pasring choices for field : {} / {}".format(title, str(e)))
                                return None
                        else:
                            answers.append({'field': {"id": id, 'type': type}, 'type': other_type, other_type: value})
                    else:
                        Logger.error("Error while getting answer type : {} is not in the supported question type ! (Please open a ticket so we can add it to the supported list)".format(other_type))
                        return None

            Logger.debug("Answers payload : {}".format(answers))

            form_id = jsonData["id"]
            if "footpatrol" in self.raffleLink:
                authority = "footpatrol.typeform.com"
                return self.bot_typeform(answers_data=answers, form_id=form_id, authority=authority)
            else:
                return self.bot_typeform(answers_data=answers, form_id=form_id)
        except KeyError as e:
            Logger.error("Key error : {}".format(str(e)))
            return -1

        except Exception as e:
            Logger.error("Error while making payload : {}".format(str(e)))
            return -1

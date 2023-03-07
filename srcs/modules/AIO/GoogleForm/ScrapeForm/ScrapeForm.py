"""********************************************************************"""
"""                                                                    """
"""   [ScrapeForm] ScrapeForm.py                                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 20/09/2021 14:49:11                                     """
"""   Updated: 04/11/2021 12:14:12                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary
import requests
import json
import re

from questionary import Choice
from datetime import datetime

from utilities import *
from .utils import *

from services.notifier.Discord.GoogleFormNotifier import *

class ScrapeForm():

    def setupEmailInput(self):
        Choices = []

        for page in self.formSettings['pages']:

            for field in page:

                if ("TEXT" in field['type']):
                    Choices.append(Choice(
                        title=[
                            ("class:purple", field['name']),
                            ("class:text", " ["),
                            ("class:blue", field['type']),
                            ("class:text", "]")
                        ],
                        value={
                            "name": field['name'],
                            "field": field
                        }
                    ))

        answer = questionary.select(
            "Which input is requiring email",
            choices=Choices,
        ).ask()

        # print(answer)

        if (answer is None):
            return self.setupEmailInput()

        if (not questionary.confirm(f"Are you sure you want to use {answer['name']} as field which contains emails?").ask()):
            return self.setupEmailInput()

        for page in self.formSettings['pages']:

            for field in page:

                if (field['id'] == answer['field']['id']):
                    field['name'] = "email"

        Logger.success(f"Replaced Email field!")

    def __init__(self) -> None:
        now = datetime.now()
        date = '{:02d}-{:02d}_{:02d}h{:02d}'.format(now.day, now.month, now.hour, now.minute)

        self.url = PromptGoogleFormURL("")

        self.formSettings = self.scrapeForm()

        if (self.formSettings is None):
            return

        self.formSettings['created'] = date

        title = self.formSettings['title'].replace("\"", "'").strip()

        if (title in os.listdir("shops/GoogleForm")):
            Logger.warning(f"You have already scraped this form, the new form title is [{date}] {title}")
            title = f"[{date}] {title}"

        try:
            os.mkdir(f"shops/GoogleForm/{title}")
        except FileExistsError:
            Logger.error("Can't create this directory because you have already scraped this form today!")
            return

        if (self.formSettings['email'] is False):
            Logger.info("We haven't detected the input which asking for Email, you need to select it.")
            self.setupEmailInput()

        columnNames = ""
        exampleColumn = ""
        profileFd = open(f"shops/GoogleForm/{title}/profile.csv", "w", encoding="utf-8")

        if (self.formSettings['email'] is True):
            columnNames += "email"
            exampleColumn += "seith@sourceraffles.com"

        for page in self.formSettings['pages']:
            for field in page:
                if (len(columnNames) == 0):
                    columnNames += f"{field['name']}"
                else:
                    columnNames += f",{field['name']}"

                if (field['type'] == "DROPDOWN" or field['type'] == "CHECKBOX" or field['type'] == "MULTIPLE_CHOICE"):
                    if (len(exampleColumn) == 0):
                        exampleColumn += f"#RANDOM#"
                    else:
                        exampleColumn += f",#RANDOM#"
                elif (field['type']) == "DATE":
                    if (len(exampleColumn) == 0):
                        exampleColumn += f"#RANDOM#"
                    else:
                        exampleColumn += f",#RANDOM#"
                else:
                    if (field['required']):
                        if (len(exampleColumn) == 0):
                            exampleColumn += f"!! REQUIRED !!"
                        else:
                            exampleColumn += f",!! REQUIRED !!"
                    else:
                        if (len(exampleColumn) == 0):
                            pass
                        else:
                            exampleColumn += f","

        profileFd.write(columnNames + "\n")
        profileFd.write(exampleColumn + "\n")
        profileFd.close()

        configurationFd = open(f"shops/GoogleForm/{title}/configuration.json", "w", encoding="utf-8")
        configurationFd.write(json.dumps(self.formSettings, indent=4))
        configurationFd.close()

        proxyFd = open(f"shops/GoogleForm/{title}/proxies.txt", "w", encoding="utf-8")
        proxyFd.write("")
        proxyFd.close()

        NotifyScrappedGoogleForm(self.formSettings)
        Logger.success(f"[GoogleForm] Successfully scrapped {title}!")

    def scrapeForm(self):

        response = requests.get(self.url)

        if ("FB_PUBLIC_LOAD_DATA_" not in response.text):
            Logger.error(f'The form is closed!')
            return (None)

        data = re.search('var FB_PUBLIC_LOAD_DATA_ = (.+?)</script>', response.text).group(1)[:-1]
        FormData = json.loads(data)

        title = FormData[1][8]
        fields = FormData[1][1]

        # for index, value in enumerate(FormData[1]):
        #     print(f"{index} - [{value}]")

        try:
            collectEmail = FormData[1][10][4] == 1
        except IndexError:
            collectEmail = 0

        needLogin = FormData[1][10][1]
        hasCaptcha = FormData[1][10][3] == 3 or FormData[1][10][3] == 1

        if (needLogin):
            Logger.error(f"Unsupported Form! This form require to be login!")
            return (None)

        lexerFields = []

        for field in fields:
            fieldType = getFieldType(field[3])
            fieldName = str(field[1]).replace(",", "").strip()
            fieldChoices = []

            if (fieldType != "NEW_PAGE" and fieldType != "IMAGE" and fieldType != "TEXT"):
                fieldIdentifier = field[4][0][0]
                fieldRequired = field[4][0][2]

                if (fieldType == "MULTIPLE_CHOICE" or fieldType == "DROPDOWN" or fieldType == "CHECKBOX"):
                    choices = field[4][0][1]

                    for choice in choices:
                        fieldChoices.append(choice[0])
            else:
                fieldIdentifier = None
                fieldRequired = None

            payload = {
                "id": fieldIdentifier,
                "type": fieldType,
                "name": fieldName,
            }

            if (fieldRequired == 1):
                payload['required'] = True
            else:
                payload['required'] = False

            if (len(fieldChoices) > 0):
                payload['choices'] = fieldChoices

            if (fieldType != "IMAGE" and fieldType != "TEXT" and fieldType != "NEW_PAGE"):
                lexerFields.append(payload)

        pages = []
        pageIndex = 0
        pages.append([])

        for field in lexerFields:
            if (field['type'] == "NEW_PAGE"):
                pageIndex += 1
                pages.append([])
            else:
                pages[pageIndex].append(field)

        formId = self.url.split("/")[6]

        return {
            "identifier": formId,
            "title": title,
            "url": self.url,
            "postingURL": f"https://docs.google.com/forms/u/0/d/e/{formId}/formResponse",
            "email": collectEmail,
            "captcha": hasCaptcha,
            "pages": pages,
            "pageCount": pageIndex
        }

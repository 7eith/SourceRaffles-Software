"""********************************************************************"""
"""                                                                    """
"""   [Settings] Settings.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 00:21:31                                     """
"""   Updated: 11/10/2021 03:53:05                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from user.User import User
from modules.Controller import ModuleController

import questionary
import requests

from questionary import Choice

from services.mail import MailManager
from utilities import Logger

class Settings():

    def initializatingModule(self):
        self.moduleName = "Settings"
        self.actions = [
            {
                "name": "[Admin] Lock Module",
                "slug": "LockModule",
                "permission": "admin",
                "locked": False
            },
            {
                "name": "[Admin] Update Client -> Server Modules",
                "slug": "UpdateModules",
                "permission": "admin",
                "locked": False
            },
            {
                "name": "Edit Webhooks",
                "slug": "EditWebhook",
                "permission": "default",
                "locked": False
            },
            {
                "name": "Import Emails",
                "slug": "ImportEmails",
                "permission": "default",
                "locked": False
            }
        ]

    def chooseSubmodule(self):

        Choices = []

        for module in self.actions:

            if (User().hasPermissions(module['permission'])):
                if (module['locked']):
                    Choices.append(Choice(
                        title=[
                            ("class:purple", module['name']),
                            ("class:text", " ["),
                            ("class:red", "Locked"),
                            ("class:text", "]")
                        ],
                        value={
                            "slug": module['slug'],
                        },
                        disabled=module['locked']
                    ))
                else:
                    Choices.append(Choice(
                    title=[
                        ("class:purple", module['name'])
                    ],
                    value={
                        "slug": module['slug'],
                    }
                ))

        Choices.append(Choice(
            title=[("class:red", "Exit")],
            value={
                "slug": "Exit"
            }
        ))

        answer = questionary.select(
            "Which modules do you want to launch?",
            choices=Choices,
        ).ask()

        if answer is None:
            return
        elif answer['slug'] == "LockModule":
            self.lockModule()
        elif answer['slug'] == "UpdateModules":
            self.updateModules()
        elif answer['slug'] == "ImportEmails":
            MailManager().importEmails()
        else:
            return (None)

    def __init__(self) -> None:
        self.initializatingModule()
        self.chooseSubmodule()

    def updateModules(self):
        Modules = ModuleController().getModules()

        for module in Modules:
            # response = requests.post(
            #     "http://api.seithh.fr/v1/module/",
            #     json={
            #         "apiKey": "pk_5zNpm422U3bULtfC",
            #         "id": "UselessId",
            #         "name": module['name'],
            #         "url": module['url'],
            #         "logo": module['logo'],
            #         "version": "1.0.0",
            #         "permission": "default",
            #     }
            # )

            # if (response.status_code == 201):
            #     Logger.success(f"Successfully created {module['name']}")

            for subModule in module['subModules']:
                response = requests.post(
                    "http://api.seithh.fr/v1/submodule",
                    json={
                        "apiKey": "pk_5zNpm422U3bULtfC",
                        "id": "1",
                        "moduleName": module['name'],
                        "name": subModule['name'],
                        "slug": subModule['slug'], 
                        "fields": subModule['fields'],
                        "permission": subModule['permission']
                    }
                )

                print(response.status_code)
                print(response.text)

    def lockModule(self):
        Choices = []

        for module in ModuleController().getModules():

            if (module['locked']):
                Choices.append(Choice(
                    title=[
                        ("class:purple", module['name']),
                        ("class:text", " ["),
                        ("class:red", "Locked"),
                        ("class:text", "]")
                    ],
                    value={
                        "slug": module['name'],
                    }
                ))
            else:
                Choices.append(Choice(
                title=[
                    ("class:purple", module['name'])
                ],
                value={
                    "slug": module['name'],
                }
            ))

        Choices.append(Choice(
            title=[("class:red", "Exit")],
            value={
                "slug": "Exit"
            }
        ))

        answer = questionary.select(
            "Which modules do you want to launch?",
            choices=Choices,
        ).ask()

        
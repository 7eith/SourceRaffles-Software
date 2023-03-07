"""********************************************************************"""
"""                                                                    """
"""   [GoogleForm] GoogleFormMain.py                                   """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 20/09/2021 14:40:16                                     """
"""   Updated: 04/11/2021 12:15:39                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from user.User import User
from modules.Controller import ModuleController

import questionary
import os

from utilities import Logger
from questionary import Choice

class GoogleFormMain():

    def initializatingModule(self):
        self.moduleName = "GoogleForm"
        self.module = ModuleController().getModule(self.moduleName)

        try:
            os.mkdir(f"shops/GoogleForm/")
        except FileExistsError:
            pass

    def chooseSubmodule(self):

        Choices = []

        for module in self.module['subModules']:

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
        if answer['slug'] == "Scraper":
            from .ScrapeForm import ScrapeForm
            
            ScrapeForm()
            return (self.chooseSubmodule())
        if answer['slug'] == "EnterForm":
            from .EnterForm import EnterForm

            EnterForm()
            return (self.chooseSubmodule())
        else:
            return (None)

    def __init__(self) -> None:
        self.initializatingModule()
        self.chooseSubmodule()

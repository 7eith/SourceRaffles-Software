"""********************************************************************"""
"""                                                                    """
"""   [Impact] ImpactMain.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 09:35:39                                     """
"""   Updated: 17/09/2021 09:43:38                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from user.User import User
from modules.Controller import ModuleController

import questionary
from questionary import Choice

class ImpactMain():

    def initializatingModule(self):
        self.moduleName = "Impact"
        self.module = ModuleController().getModule(self.moduleName)

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
        elif answer['slug'] == "EnterRaffle":
            from .modules import EnterRaffleModule

            EnterRaffleModule()
        else:
            return (None)

    def __init__(self) -> None:
        self.initializatingModule()
        self.chooseSubmodule()

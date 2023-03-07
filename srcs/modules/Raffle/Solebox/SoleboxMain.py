"""SoleboxMain.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 01/12/2021	 15:25	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

"""********************************************************************"""
"""                                                                    """
"""   [Afew] AfewMain.py                                             """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 31/08/2021 23:30:08                                     """
"""   Updated: 11/09/2021 16:51:06                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from user.User import User
from modules.Controller import ModuleController

import questionary
from questionary import Choice

class SoleboxMain():

    def initializatingModule(self):
        self.moduleName = "Solebox"
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


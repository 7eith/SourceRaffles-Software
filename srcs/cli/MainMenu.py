"""********************************************************************"""
"""                                                                    """
"""   [cli] MainMenu.py                                                """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 25/08/2021 14:33:02                                     """
"""   Updated: 11/10/2021 03:49:15                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import os
from modules.Controller.ModuleController import ModuleController

from user import *
from utilities import *

class MainMenu():

    def __init__(self) -> None:
        setTitle(f"SourceRaffles [{getVersion()}] - {User().getFullUsername()}")

        self.showMainWindow()

    def showMainWindow(self):

        clearConsole()
        modules = ModuleController().getModules()

        rowsModules = list(chunk(modules, 10))

        strings = ['' for i in range(10)]

        printHeader()

        width = os.get_terminal_size().columns

        print(f"Welcome back {User().getFullUsername()}, which site do you want to kill today? \n".center(width))

        for row in rowsModules:
            index = 0
            for module in row:

                moduleName = ""

                if (module['locked'] is True):
                    moduleName += f"{Colors.YELLOW}{module['name']}{Colors.RESET}"
                elif (User().hasPermissions(module['permission']) is False):
                    moduleName += f"{Colors.RED}Hidden{Colors.RESET}"
                else:
                    moduleName += f"{Colors.BEIGE}{module['name']}{Colors.RESET}"

                strings[index] += '{:{width}}'.format("{:2} - {}".format(module['id'], moduleName), width='35')
                index += 1
        
        for string in strings:
            calc = (width // 2) - 50
            spacer = " " * calc
            print(f"{spacer} {string}")
        
        print("")
        module = PromptModule(offset=calc)

        if (module is None):
            exit(0)
            
        moduleName = ModuleController().getModuleById(module)['name']
        ModuleController().launchModule(moduleName)

        return self.showMainWindow()
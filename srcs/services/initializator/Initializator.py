"""********************************************************************"""
"""                                                                    """
"""   [initializator] Initializator.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 31/08/2021 23:25:50                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import os

from utilities import Logger
from modules.Controller import ModuleController

class Initializator():

    def __init__(self) -> None:
        self.createRequiredFolders()
        
        """ variables """
        self.modules = ModuleController().getModules()

        """ init functions """
        self.createModulesRequiredFolders()
        self.createProfileFiles()

    def createRequiredFolders(self):
        folders = ["shops", "proxies", "logs", "resources", "resources/AutoConfirmer"]

        for directory in folders:
            try:
                os.mkdir(directory)
            except FileExistsError:
                pass

    def createModulesRequiredFolders(self):
        modules = self.modules

        for module in modules:
            try:
                Logger.debug(f"Creating default folder for {module['name']}")
                os.mkdir(f"shops/{module['name']}")
                os.mkdir(f"logs/{module['name']}")
                os.mkdir(f"proxies/{module['name']}")
                os.mkdir(f"tools")
            except FileExistsError:
                pass
        
    def createProfileFiles(self):
        modules = self.modules

        for module in modules:
            moduleName = module['name']

            for subModule in module['subModules']:
                fileName = "{}_example.csv".format(subModule['name'].replace(" ", ""))

                file = open(f"shops/{moduleName}/{fileName}", "w")
                file.write(",".join(subModule['fields']) + "\n")
                file.close()
                
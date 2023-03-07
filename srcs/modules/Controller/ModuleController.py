"""********************************************************************"""
"""                                                                    """
"""   [Controller] ModuleController.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 09/08/2021 04:57:31                                     """
"""   Updated: 14/11/2021 13:13:13                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from typing import Set
from .Settings import *

from core.singletons.ModuleSingleton import ModuleSingletonMeta
from utilities import *

class ModuleController(metaclass=ModuleSingletonMeta):

    def __init__(self) -> None:
        self.modules = []

        self.modules.append(NakedModule)
        self.modules.append(FootShopModule)
        self.modules.append(EndModule)
        self.modules.append(NittyGrittyModule)
        self.modules.append(AfewModule)
        self.modules.append(SOTFModule)
        self.modules.append(KithModule)
        self.modules.append(Stress95Module)
        self.modules.append(UrbanstaromaModule)
        self.modules.append(BSTNModule)
        self.modules.append(WoodWoodModule)
        self.modules.append(CourirModule)
        self.modules.append(SacaiModule)
        self.modules.append(OqiumModule)
        self.modules.append(JuiceStoreModule)
        self.modules.append(UnderCoverModule)
        self.modules.append(SizeLaunchesModule)
        self.modules.append(FootPatrolLaunchesModule)

        """
            Apps
        """

        self.modules.append(AsphaltGoldModule)
        self.modules.append(FootLockerModule)
        self.modules.append(SNSModule)
        self.modules.append(SVDModule)
        
        """
            Lowkey
        """
        
        self.modules.append(BeamHillModule)
        self.modules.append(KellerModule)
        self.modules.append(ImpactModule)
        self.modules.append(TheBrokenArmModule)
        self.modules.append(RezetStoreModule)
        self.modules.append(SoleboxModule)


        """
            Forms
        """
        
        self.modules.append(TypeFormsModule)
        self.modules.append(GoogleFormsModule)
        self.modules.append(MicrosoftFormsModule)

        """
            Tools
        """

        self.modules.append(AddressJiggerModule)
        self.modules.append(GeoCoderModule)
        self.modules.append(SettingsModule)
        self.modules.append(OutlookGeneratorModule)

        self.modules.sort(key=lambda x: x.get('id'))

    def getModule(self, name):
        """
            getModule by Name or Id
                supported kwargs: id: int | name: string
        """

        try:
            return [module for module in self.modules if module["name"] == name][0]
        except IndexError:
            return None

    def getModuleById(self, id):
        try:
            return [module for module in self.modules if module["id"] == id][0]
        except IndexError:
            return None

    def getSubModule(self, module, name):
        try:
            return [module for module in module['subModules'] if module["slug"] == name][0]
        except IndexError:
            return None
            
    def moduleIsAvailable(self, name):
        userPermissions = User().permissions
        module = self.getModule(name)

        if (module is None):
            Logger.debug("Module is None")
            return False

        if ("admin" in userPermissions):
            return True
        if (module['locked'] == True and "admin" not in userPermissions):
            Logger.debug("Module locked and no permissions granted !")
            return False
        if (module['permission'] not in userPermissions):
            Logger.debug("Not enough permissions to access !")
            return False
            
        return True

    def createProfiles(self, module):

        if (module['name'] == "GoogleForm"):
            return
            
        for subModule in module['subModules']:

            fileName = "{}_example.csv".format(subModule['name'].replace(" ", ""))

            try:
                fd = open(f"shops/{module['name']}/{fileName}", "r", encoding="utf-8")

                lines = fd.readlines()

                if (len(lines) == 1):
                    Logger.debug(f"[ModuleChecker] File is empty {fileName}")
                    file = open(f"shops/{module['name']}/{fileName}", "w")
                    file.write(",".join(subModule['fields']) + "\n")
                    file.close()
            except FileNotFoundError:
                Logger.debug(f"[ModuleChecker] Default files for {module['name']} doesn't exist. Creating...")

                file = open(f"shops/{module['name']}/{fileName}", "w")
                file.write(",".join(subModule['fields']) + "\n")
                file.close()
        
    def launchModule(self, moduleName):
        clearConsole()
        printHeader()

        module = self.getModule(moduleName)

        notNeededFolders = ["GeoCoder", "Address Jigger"]

        if module['name'] not in notNeededFolders:
            try:
                Logger.debug(f"Creating default folder for {module['name']}")
                os.mkdir(f"logs/{module['name']}")
                os.mkdir(f"shops/{module['name']}")
                os.mkdir(f"proxies/{module['name']}")

            except FileExistsError:
                pass

            try:
                self.createProfiles(module)
            except Exception as error:
                Logger.error(str(error))
                Logger.error("[ModuleChecker] Error while creating profiles!")

        if moduleName == "UnderCover":
            from modules.Raffle.UnderCover import UnderCoverMain

            UnderCoverMain()
        if moduleName == "Settings":
            from tools.Settings import Settings

            Settings()
        if moduleName == "Oqium":
            from modules.Raffle.Oqium import OqiumMain

            OqiumMain()
            
        if moduleName == "Sacai":
            from modules.Raffle.Sacai import SacaiMain

            SacaiMain()
        if moduleName == "Courir":
            from modules.Raffle.Courir import CourirMain
            CourirMain()
        if moduleName == "GoogleForm":
            from modules.AIO.GoogleForm import GoogleFormMain
            GoogleFormMain()
        if moduleName == "Naked":
            from modules.Raffle.Naked import NakedMain
            NakedMain()
        if moduleName == "FootShop":
            from modules.Raffle.FootShop import FootshopMain
            FootshopMain()
        if moduleName == "Impact":
            from modules.Raffle.Impact import ImpactMain
            ImpactMain()
        if moduleName == "End":
            from modules.Raffle.End import EndMain
            EndMain()
        if moduleName == "WoodWood":
            from modules.Raffle.WoodWood import WoodwoodMain
            WoodwoodMain()
        if moduleName == "Nittygritty":
            from modules.Raffle.Nittygritty import NittygrittyMain
            NittygrittyMain()
        if moduleName == "SNS":
            from modules.Raffle.SNS import SNSMain
            SNSMain()
        if moduleName == "Kith":
            from modules.Raffle.Kith import KithMain
            KithMain()
        if moduleName == "Afew":
            from modules.Raffle.Afew import AfewMain
            AfewMain()
        if moduleName == "SVD":
            from modules.Raffle.SVD import SVDMain
            SVDMain()
        if moduleName == "SOTF":
            from modules.Raffle.SOTF import SOTFMain
            SOTFMain()
        if moduleName == "TypeForms":
            from modules.Raffle.Typeforms import TypeformsMain
            TypeformsMain()
        if moduleName == "Keller":
            from modules.Raffle.Keller import KellerMain
            KellerMain()
        if moduleName == "Rezet":
            from modules.Raffle.Rezet import RezetMain
            RezetMain()
        if moduleName == "BSTN":
            from modules.Raffle.BSTN import BSTNMain
            BSTNMain()
        if moduleName == "GeoCoder":
            from modules.Raffle.Geocoding import GeocodingMain
            GeocodingMain()
        if moduleName == "AddyJigger":
            from modules.Raffle.AddyJigger import AddyJiggerMain
            AddyJiggerMain()
        if moduleName == "JuiceStore":
            from modules.Raffle.JuiceStore import JuiceStoreMain
            JuiceStoreMain()
        if moduleName == "Sacai":
            from modules.Raffle.Sacai import SacaiMain
            SacaiMain()
        if moduleName == "Urbanstaroma":
            from modules.Raffle.Urbanstaroma import UrbanstaromaMain
            UrbanstaromaMain()
        if moduleName == "Address Jigger":
            from modules.Raffle.AddyJigger import AddyJiggerMain
            AddyJiggerMain()
        if moduleName == "Stress95":
            from modules.Raffle.Stress95 import Stress95Main
            Stress95Main()
        if moduleName == "SizeLaunches":
            from modules.Raffle.SizeLaunches import SizeLaunchesMain
            SizeLaunchesMain()
        if moduleName == "FootpatrolLaunches":
            from modules.Raffle.FootpatrolLaunches import FootpatrolLaunchesMain
            FootpatrolLaunchesMain()
        if moduleName == "Beamhill":
            Logger.info("Module is locked !")
            # from modules.Raffle.Beamhill import BeamhillMain
            # BeamhillMain()
        if moduleName == "Outlook Generator":
            from modules.Raffle.OutlookGenerator import OutlookGeneratorMain
            OutlookGeneratorMain()
        if moduleName == "Solebox":
            from modules.Raffle.Solebox import SoleboxMain
            SoleboxMain()

        else:
            Logger.debug("Module : {} is not linked to any function".format(moduleName))

    def getModules(self):
        return (self.modules)
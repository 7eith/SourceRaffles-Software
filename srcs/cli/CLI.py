"""********************************************************************"""
"""                                                                    """
"""   [cli] CLI.py                                                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 11/10/2021 00:47:05                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import colorama
import platform

if "darwin" not in platform.system().lower():
    import helheim
from updater import AutoUpdater
from utilities import *
from license import License
from services.notifier import *
from services.rpc import DiscordRPC
from services.captcha import *
from services.mail import *

from cli.MainMenu import MainMenu

class CLI():

    def __init__(self) -> None:
        colorama.init()

        clearConsole()
        
        setTitle("Initializating SourceRaffles")
        Logger.info("Initializating SourceRaffles")

        Configuration()

        # License()

        User({
            "discordId": "667",
            "role": "admin",
            "username": "Seith",
            "discriminator": "0001",
            "permissions": ["admin"],
        }, "SLT")

        # AutoUpdater()

        DiscordRPC()
        
        MainMenu()
        # state = MailController().fetchMail("service@bstn.com", "PhearsdorfDwana@outlook.com", "Verify your email", False, "verify")

        # print(state)

        # MailManager().importEmails()

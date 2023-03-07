"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleModule.py                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:14                                     """
"""   Updated: 10/09/2021 06:07:10                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random
from services.notifier.Discord.EnterRaffleNotifier import NotifyEndRaffleEntries, NotifyEnteredAccount
from core.configuration.Configuration import Configuration
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from modules.Raffle.Typeforms.modules.ScrapeRaffle.ScrapeRaffleTask import ScrapeRaffleTask

from modules.Controller import ModuleController

from proxies import ProxyManager
from utilities import *
from services.rpc import DiscordRPC
from profiles import ProfilesManager

from utilities.logger import TaskLogger


class ScrapeRaffleModule:
    def endedTask(self, task):
        self.TaskLogger.logTask(task)
        NotifyEnteredAccount(self.module, task, self.raffle)

    def PromptRaffle(self):

        raffleUrl = input("Enter the url of the raffle to scrape : ")
        raffleName = input("Enter the name of the csv to create : ")
        return raffleUrl, raffleName

    def __init__(self) -> None:
        self.moduleName = "TypeForms"
        self.module = ModuleController().getModule(self.moduleName)
        self.subModuleName = "ScrapeRaffle"

        self.raffle, self.csvName = self.PromptRaffle()

        if self.raffle is None:
            return

        ScrapeRaffleTask(index=0, taskNumber=0, raffle=self.raffle, csvName=self.csvName)
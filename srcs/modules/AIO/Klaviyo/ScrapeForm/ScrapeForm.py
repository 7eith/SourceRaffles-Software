"""********************************************************************"""
"""                                                                    """
"""   [ScrapeForm] ScrapeForm.py                                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 07/10/2021 04:39:20                                     """
"""   Updated: 10/10/2021 07:46:49                                     """
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

    def __init__(self) -> None:
        now = datetime.now()
        date = '{:02d}-{:02d}_{:02d}h{:02d}'.format(now.day, now.month, now.hour, now.minute)
        
        self.url = PromptGoogleFormURL("")

        self.formSettings = self.scrapeForm()
        
        if (self.formSettings is None):
            return 
            
        self.formSettings['created'] = date

        title = self.formSettings['title'].replace("\"", "'")

        if (title in os.listdir("tools/GoogleForm")):
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
        pass

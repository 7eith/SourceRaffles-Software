"""********************************************************************"""
"""                                                                    """
"""   [mail] MailManager.py                                            """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 14/08/2021 05:32:40                                     """
"""   Updated: 11/10/2021 03:54:41                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary

from utilities import ReadCSV, Logger
from .MailController import MailController

class MailManager():

    importFile = "resources/AutoConfirmer/import.csv"

    def checkFile(self):
        try:
            open(self.importFile)
            return True
        except FileNotFoundError:
            return False
            
    def __init__(self) -> None:
        pass

    def importEmails(self):
        if (self.checkFile() is False):
            Logger.error("[AutoConfirmer] Can't import emails when import.csv is not existing!")
            input("Press enter to leave")
            return 

        rows = ReadCSV(self.importFile)

        chunks = []
        chunks.append([])
        index = 0
        
        for row in rows:
            if (len(row['username']) == 0):
                chunks.append([])
                index += 1
            else:
                chunks[index].append(row)
                
        if (questionary.confirm(f"[AutoConfirmer] Are you sure to import {len(chunks)} master emails?").ask()):
            Logger.info(f"[AutoConfirmer] Importing emails...")

            for chunk in chunks:
                username = chunk[0]['username']
                password = chunk[0]['password']

                del chunk[0]
                childs = []
                for child in chunk:
                    childs.append(child['username'])

                MailController().addMails(username, password, childs)

            MailController().saveMails()
            Logger.success(f"[AutoConfirmer] Successfully added emails to database!")
        input("Press enter to leave")

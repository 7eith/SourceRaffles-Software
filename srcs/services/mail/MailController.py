"""********************************************************************"""
"""                                                                    """
"""   [mail] MailController.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 14/08/2021 03:31:29                                     """
"""   Updated: 11/10/2021 00:45:53                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import imaplib
import os
import json
import regex as re

from json.decoder import JSONDecodeError
from imap_tools import MailBox, A
import imap_tools

from core.singletons.MailSingleton import MailSingletonMeta
from utilities import Logger, EXCEPTION, FAILED, SUCCESS

class MailController(metaclass=MailSingletonMeta):

    mailFilePath = "resources/AutoConfirmer/mails.json"

    imapProviders = {
        "gmail": "imap.gmail.com",
        "outlook": "outlook.office365.com"
    }

    def __init__(self) -> None:

        self.mails = None

        if (self.mails is None):
            self.loadMails()

    def loadMails(self):

        try: 

            mailFile = open(self.mailFilePath, "r", encoding="utf-8", newline="")
            self.mails = json.load(mailFile)['mails']
            mailFile.close()

        except FileNotFoundError:

            Logger.info("Mail file not found, creating new one!")

            emptyConfiguration = {
                "mails": [
                    {
                        "username": "email address",
                        "password": "password",
                        "logged": None,
                        "childs": [
                            "*@seith.fr",
                            "seith@gmail.com"
                        ]
                    }
                ]
            }

            with open(self.mailFilePath, "w") as MailFile:
                MailFile.write(json.dumps(emptyConfiguration, indent=4))

            self.mails = None

        except JSONDecodeError:
            Logger.error("Invalid Mails files (check: resources/AutoConfirmer/mails.json)")

    def saveMails(self):
        Logger.debug("[AutoConfirmer] Saving Mails to mail File...")

        mailFile = open(self.mailFilePath, "w", encoding="utf-8", newline="")
        mailFile.write(json.dumps({"mails": self.mails}, indent=4))
        mailFile.close()

        Logger.debug("[AutoConfirmer] Successfully saved mail file!")

    """ 
        @Getters / @Setters
    """

    def addMails(self, username, password, mails):
        
        self.mails.append({
            "username": username,
            "password": password,
            "logged": None,
            "childs": mails
        })
        
        Logger.debug(f"[AutoConfirmer] Added {username}:{password} to mails!")
        
    def getMails(self):
        return self.mails

    def isLoaded(self):
        if (self.mails is not None):
            return True
        return False

    def getMailCredentials(self, email):

        if ("@" not in email):
            return (FAILED)

        for masterEmail in self.mails:
            
            # is parent and not child
            if (email == masterEmail['username']):
                return (masterEmail)

            if (email in masterEmail['childs']):
                return (masterEmail)

            domain = email.split("@")[1]
            catchallName = f"*@{domain}"

            if (catchallName in masterEmail['childs']):
                return (masterEmail)
                    
        return (None)

    def fetchMail(self, sender, email, subject, seen=False, requiredContent=""):
        Logger.debug(f"[MailService] Fetching mail for {email} sent by {sender}")
        Logger.debug(f"[MailService] sender={sender}, to={email}, subject={subject}, seen={seen}, requiredText={requiredContent}")
        credentials = self.getMailCredentials(email)

        if (credentials is False):
            return {"status": False, "message": "Invalid emails!"}
        
        if (credentials is None):
            return {"status": False, "message": "Email not existing in database!"}

        provider = credentials['username'].split("@")[1].split(".")[0]

        if (provider in self.imapProviders.keys()):
            Logger.debug(f"[MailService] Supported provider, using {provider} as provider.")

            providerImap = self.imapProviders[provider]

            try:
                with MailBox(providerImap).login(credentials['username'], credentials['password'], "INBOX") as mailInbox:

                    mails = mailInbox.fetch(A(seen=seen, subject=subject, from_=sender, to=email))
                    
                    if (provider == "gmail"):
                        folderName = "[Gmail]/Spam"
                    else:
                        folderName = "Junk"
                    
                    try:
                        mailInbox.folder.set(folderName)

                        Logger.debug(f"Fetching in Spam using {folderName} for {provider}")
                        mails += mailInbox.fetch(A(seen=seen, subject=subject, from_=sender, to=email))
                        Logger.debug(f"Fetched in Spam using {folderName} for {provider}")

                    except Exception as error:
                
                        if ("NONEXISTENT" in str(error)):
                            Logger.debug(f"This folder doesn't exist")

                    for mail in mails:
                        content = mail.text or mail.html

                        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                        url = re.findall(regex, content)
                        urls = [x[0] for x in url]

                        for url in urls:
                            
                            if (requiredContent in url):
                                return {"status": True, "link": url, "mail": True}
                        
                        return {"status": True, "link": None, "mail": True}
                    return {"status": True, "link": None}

            except Exception as error:
                
                try:
                    errName = error.args[0].decode("utf-8")
                    if ("AUTHENTICATIONFAILED" in errName):
                        Logger.error(f"Invalid Credentials!")
                        return {"status": False, "message": "Invalid Credentials!"}

                    else:
                        Logger.error(f"[MailService] Unknow error: {errName}")
                        return {"status": False, "message": "Error has happen!"}
                        
                except Exception:
                    Logger.error(f"[MailService] Unknow error: {error}")
                    return {"status": False, "message": "Error has happen!"}

        else:
            Logger.error(f"[MailService] Unsupported provider! {provider} not supported.")
            return {"status": False, "message": "Unsupported provider"}

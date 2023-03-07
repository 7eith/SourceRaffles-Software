"""********************************************************************"""
"""                                                                    """
"""   [logger] TaskLogger.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 03/09/2021 05:47:18                                     """
"""   Updated: 13/11/2021 17:08:33                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import csv
from utilities.files.FileReader import ReadCSV

from .Logger import Logger

from threading import Semaphore

from pprint import pprint

lock = Semaphore(1)

class TaskLogger():

    def __init__(self, loggerFile) -> None:
        self.loggerFile = loggerFile

    def createLogger(self, profiles, newRows: list = []):
        Logger.debug(f"[TaskLogger] Creating {self.loggerFile}..")

        fd = open(self.loggerFile, "w", encoding="utf-8")
        headers = []

        for key in profiles[0].keys():
            headers.append(key)

        for row in newRows:
            if (row not in headers):
                headers.append(row)

        try:
            self.header = ",".join(headers) + "\n"
        except TypeError:
            Logger.error("Invalid Profiles [some columns got error!]")
            return (None)
            
        fd.write(self.header)
        
        for profile in profiles:
            for row in newRows:
                profile[row] = ""
                
            fd.write(",".join(profile.values()) + "\n")

        Logger.debug(f"[TaskLogger] Successfully created Logger!")

        fd.close()
        return (True)

    def logTask(self, task):
        try:
            lock.acquire()
            updatedLines = []

            ReadedCSV = ReadCSV(self.loggerFile)

            for row in ReadedCSV:
                if (row['email'] == task.profile['email']):
                    for key in task.profile.keys():
                        row[key] = task.profile[key]
                updatedLines.append(row)

            fd = open(self.loggerFile, "w", encoding="utf-8")
            fd.write(self.header)

            for line in updatedLines:
                items = list(line.values())
                for elt in items:
                    if type(elt) == dict or type(elt) == list:
                        items.remove(elt)
                    else:
                        if elt is None:
                            items[items.index(elt)] = "Unknown"
                fd.write(",".join(items) + "\n")
            fd.close()
            lock.release()

        except Exception as e:
            Logger.error("Error while saving logs : {}".format(str(e)))

    def logLink(self, task):
        try:
            lock.acquire()
            updatedLines = []

            ReadedCSV = ReadCSV(self.loggerFile)

            for row in ReadedCSV:
                if (row['link'] == task.profile['link']):
                    for key in task.profile.keys():
                        row[key] = task.profile[key]
                updatedLines.append(row)

            fd = open(self.loggerFile, "w", encoding="utf-8")
            fd.write(self.header)

            for line in updatedLines:
                items = list(line.values())
                for elt in items:
                    if elt is None:
                        items[items.index(elt)] = "Unknown"
                fd.write(",".join(items) + "\n")

            fd.close()
            lock.release()

        except Exception as e:
            lock.release()
            Logger.error("Error while saving logs : {}".format(str(e)))

    def logProfile(self, profile):
        lock.acquire()
        updatedLines = []
        
        ReadedCSV = ReadCSV(self.loggerFile)
        
        for row in ReadedCSV:
            if (row['email'] == profile['email']):
                for key in profile.keys():
                    row[key] = profile[key]
            updatedLines.append(row)
            
        fd = open(self.loggerFile, "w", encoding="utf-8")
        fd.write(self.header)

        for line in updatedLines:
            items = list(line.values())

            lineToWrite = ""
            for item in items:
                lineToWrite += f",{item}"
            
            fd.write(f"{lineToWrite[1:]}\n")

        fd.close()
        lock.release()
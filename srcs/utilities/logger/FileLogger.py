"""********************************************************************"""
"""                                                                    """
"""   [logger] FileLogger.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 01/09/2021 04:32:40                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import utilities

"""
    logDebugMessage
        message: message to write to debug file
"""

def logDebugMessage(message):
    logIntoFile("debug.log", message)

"""
    logIntoFile
        file: file to log into
        message: message to write into the file
"""

def logIntoFile(file, message, mode="a"):
    file = open(file, mode, encoding="utf-8")
    file.write(utilities.escape_ansi(message))
    file.write("\n")
    file.close()
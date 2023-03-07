"""********************************************************************"""
"""                                                                    """
"""   [logger] Logger.py                                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 10/09/2021 07:38:54                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import utilities

from utilities import Colors, getTime, isDebug

from threading import Semaphore

lock = Semaphore(1)

class Logger:

    def log(message, removeEnd=False):
        lock.acquire()
        formatedMessage = f"[{Colors.PURPLE}{getTime()}{Colors.RESET}] {message}{Colors.RESET}"

        if (isDebug()):
            utilities.logDebugMessage(formatedMessage)

        if removeEnd:
            print(f"\r{formatedMessage}", end="")
        else:
            print(formatedMessage)
        lock.release()

    def info(message, removeEnd=False):
        Logger.log(f"{Colors.BLUE}{message}", removeEnd=removeEnd)

    def error(message, removeEnd=False):
        Logger.log(f"{Colors.RED}{message}", removeEnd=removeEnd)
        
    def success(message, removeEnd=False):
        Logger.log(f"{Colors.GREEN}{message}", removeEnd=removeEnd)

    def warning(message, removeEnd=False):
        Logger.log(f"{Colors.YELLOW}{message}", removeEnd=removeEnd)

    def debug(message, removeEnd=False):
        if (isDebug()):
            Logger.log(f"{Colors.YELLOW}{message}", removeEnd=removeEnd)

    def formatForInput(message, color=Colors.BLUE):
        formatedMessage = f"[{Colors.PURPLE}{getTime()}{Colors.RESET}] {color}{message}{Colors.RESET}"
        return formatedMessage
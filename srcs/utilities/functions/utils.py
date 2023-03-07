"""********************************************************************"""
"""                                                                    """
"""   [functions] utils.py                                             """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 08/08/2021 02:41:49                                     """
"""   Updated: 13/10/2021 03:20:56                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import os
import ctypes
import time

from itertools import islice
from utilities.ui import *
from datetime import datetime

SUCCESS = 1
FAILED = 0
EXCEPTION = -1

def isDebug():
    return "debug.sr" in os.listdir()

"""
	setTitle(title)
		set title to Console
"""

def setTitle(title):
	if (os.name == "nt"):
		ctypes.windll.kernel32.SetConsoleTitleW(title)
	else:
		print(f"\33]0;{title}\a", end='', flush=True)

"""
	clearConsole()
		clear Console
"""

def clearConsole():
	if (os.name == "nt"):
		os.system("cls")
	else:
		os.system("clear")

def printHeader():

	banners = [
		"    _____                            ____        __________         ",
		"   / ___/____  __  _______________  / __ \____ _/ __/ __/ /__  _____",
		"   \__ \/ __ \/ / / / ___/ ___/ _ \/ /_/ / __ `/ /_/ /_/ / _ \/ ___/",
		"  ___/ / /_/ / /_/ / /  / /__/  __/ _, _/ /_/ / __/ __/ /  __(__  ) ",
		" /____/\____/\__,_/_/   \___/\___/_/ |_|\__,_/_/ /_/ /_/\___/____/  ",
		"                                                                    "
	]

	width = os.get_terminal_size().columns
	
	for line in banners:
		lineFormat = f"{Colors.PURPLE}{line}{Colors.RESET}"
		print(lineFormat.center(width))

	print("---------------\n".center(width))

def printSeparator():
	print("------------------------------------------------------------------------------------------------------------------------")

def getCurrentTime():
	return datetime.now().strftime("%H:%M:%S:%f")[:-3]

def waitUntil(delay, threads=False):
	
	if (threads is True):
		print(f"[{Colors.PURPLE}{getCurrentTime()}{Colors.RESET}] {Colors.BEIGE}Sleeping for {delay} s...{Colors.RESET}")
		time.sleep(delay)
		print(f"[{Colors.PURPLE}{getCurrentTime()}{Colors.RESET}] {Colors.BEIGE}Sleeped for {delay} s. Continuing..{Colors.RESET}")
		return 

	while delay > -1:
		time.sleep(1)
		print("\r               {}s left before continuing..".format(delay), end="")
		delay = delay - 1

	print("\r               Continuing...                 ")

def getAPI():

	return "https://api.seithh.fr"

def chunk(it, size):
	it = iter(it)
	return iter(lambda: tuple(islice(it, size)), ())
	
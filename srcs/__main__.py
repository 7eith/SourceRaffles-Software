import platform
import os
import ctypes

if "darwin" not in platform.system().lower():
	print("Initializating SourceRaffles...")

	if (os.name == "nt"):
		ctypes.windll.kernel32.SetConsoleTitleW("Initializating SourceRaffles...")

	import helheim
	try:
		helheim.auth('bd1e84ee-9ffe-4d77-a0bd-a83774107533', debug=False)
	except Exception as error:
		pass

from cli.CLI import CLI
os.chdir(os.getcwd())
CLI()
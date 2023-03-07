"""********************************************************************"""
"""                                                                    """
"""   [Toast] CreateToastNotification.py                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 11/09/2021 16:40:14                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import platform

from utilities import getPackedFile

if (platform.system().lower() == "windows"):
	from win10toast_click import ToastNotifier 
	toaster = ToastNotifier()

	def callback():
		print("HELLO LOULOU")
		toaster.show_toast(
			"SourceRaffles - FootShop [3DS]",
			"Successfully solved 3DS!",
			icon_path=getPackedFile("resources/Logo.ico"),
			duration=5,
			threaded=False,
		)

	def FootShop_ThreeDS_Ready_Notifications():
		toaster.show_toast(
			"SourceRaffles - FootShop [3DS]",
			"Awaiting 3D Secure!\n Click here to handle it!",
			icon_path=getPackedFile("resources/Logo.ico"),
			duration=None,
			threaded=False,
			callback_on_click=callback
		)

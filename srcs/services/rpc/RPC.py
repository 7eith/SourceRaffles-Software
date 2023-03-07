"""********************************************************************"""
"""                                                                    """
"""   [rpc] RPC.py                                                     """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 08:35:42                                     """
"""   Updated: 01/09/2021 04:12:44                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import time

from pypresence import Presence

from core.singletons.RPCSingleton import RPCSingletonMeta
from core import Core
from utilities import Logger, getVersion

from core.configuration import Configuration

class DiscordRPC(metaclass=RPCSingletonMeta):

	def __init__(self) -> None:

		if (Configuration().getUserSettings()['DiscordPresence']):
			self.RPC = Presence("830165397810577479")
			
			try: 
				self.RPC.connect()
				
				self.RPC.update(
					buttons=[{"label": "Twitter", "url": "https://twitter.com/sourceraffles"}],
					details="Beta", 
					state=getVersion(),
					large_image='sourceraffles', 
					large_text="SourceRaffles",
					start=int(time.time())
				)

			except Exception as error:
				self.RPC = None
				Logger.error("Error has occured when trying to enable DiscordRichPresence")
				Logger.error(error)
		else:
			Logger.debug("[Presence] Skipped initializating DiscordRichPresence due to User Settings.")
			self.RPC = None
	
	def updateRPC(self, details='Destroying Hidden'):
		if (self.RPC):
			Logger.debug("[Presence] Updating Presence...")

			self.RPC.update(
				buttons=[{"label": "Twitter", "url": "https://twitter.com/sourceraffles"}],
				details=details,
				state=getVersion(), 
				large_image="sourceraffles",
				large_text="SourceRaffles",
				start=int(time.time())
			)

			Logger.debug("[Presence] Updated Presence!")
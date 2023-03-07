"""********************************************************************"""
"""                                                                    """
"""   [core] Core.py                                                   """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 02/08/2021 07:22:53                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from datetime import datetime

from .singletons.CoreSingleton import CoreSingletonMeta

class Core(metaclass=CoreSingletonMeta):

    def __init__(self) -> None:

        """ 
            Setup Date 
        """

        now = datetime.now()
        self.startDate = '{:02d}_{:02d}_{:02d}-{:02d}-{:02d}'.format(now.day, now.month, now.hour, now.minute, now.second)
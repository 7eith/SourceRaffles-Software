"""********************************************************************"""
"""                                                                    """
"""   [timer] Time.py                                                  """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/07/2021 05:17:22                                     """
"""   Updated: 02/08/2021 07:22:16                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from datetime import datetime

def getTime():
	return datetime.now().strftime("%H:%M:%S:%f")[:-3]
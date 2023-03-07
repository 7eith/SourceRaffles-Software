"""********************************************************************"""
"""                                                                    """
"""   [tasks] TaskLogger.py                                            """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 04:25:30                                     """
"""   Updated: 02/09/2021 11:37:19                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities.logger.FileLogger import logIntoFile

def createLogger(loggerFileName, fields):
    header = ",".join(fields.keys())
    
    logIntoFile(loggerFileName, "status,{}".format(header), mode="w")
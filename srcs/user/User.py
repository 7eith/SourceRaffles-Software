"""********************************************************************"""
"""                                                                    """
"""   [user] User.py                                                   """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 31/08/2021 23:38:16                                     """
"""   Updated: 03/11/2021 00:49:51                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from core.singletons.UserSingleton import UserSingletonMeta

class User(metaclass=UserSingletonMeta):

    def __init__(self, userProfile, token) -> None:
        self.logged = True

        self.discordIdentifier = userProfile['discordId']
        self.role = userProfile['role']
        self.username = userProfile['username']
        self.discriminator = userProfile['discriminator']
        self.permissions = userProfile['permissions']

        self.token = token

    def hasPermissions(self, permissionName):
        if ("admin" in self.permissions):
            return (True)
        if (permissionName in self.permissions):
            return (True)
        return False
        
    def getFullUsername(self):
        return f"{self.username}#{self.discriminator}"

    def getToken(self):
        return self.token
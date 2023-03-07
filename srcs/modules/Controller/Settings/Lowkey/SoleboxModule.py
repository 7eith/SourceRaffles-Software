"""********************************************************************"""
"""                                                                    """
"""   [Lowkey] SoleboxModule.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 03:35:17                                     """
"""   Updated: 01/10/2021 14:13:48                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

SoleboxModule = {
    "id": 21,
    "name": "Solebox",
    "slug": "TheBrokenArm",
    "url": "https://www.the-broken-arm.com/fr/",
    "logo": "https://www.the-broken-arm.com/img/the-broken-arm-logo-1594886707.jpg",
    "version": "1.0.0",
    "locked": False,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "first_name", "last_name", "phone", "country", "day", "month", "gender", "instagram", "shop", "size"]
        }
    ]
}

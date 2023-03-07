"""********************************************************************"""
"""                                                                    """
"""   [Raffle] SacaiModule.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 04/10/2021 06:51:29                                     """
"""   Updated: 22/10/2021 19:07:06                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

UnderCoverModule = {
    "id": 26,
    "name": "UnderCover",
    "slug": "UnderCover",
    "url": "https://store.undercoverism.com/",
    "logo": "https://store.undercoverism.com/assets/front/img/logo.svg?1624030387",
    "version": "1.0.0",
    "locked": False,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Account Generator",
            "slug": "AccountGenerator",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password"],
        },
        {
            "id": 2,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password"]
        },
        {
            "id": 3,
            "name": "Account Confirmer",
            "slug": "AccountConfirmer",
            "locked": False,
            "permission": "default",
            "fields": ["email", "password", "masterEmail", "masterPassword", "link"]
        }
    ]
}
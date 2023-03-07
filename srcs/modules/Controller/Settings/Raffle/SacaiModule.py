"""********************************************************************"""
"""                                                                    """
"""   [Raffle] SacaiModule.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 04/10/2021 06:51:29                                     """
"""   Updated: 04/10/2021 14:04:17                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

SacaiModule = {
    "id": 23,
    "name": "Sacai",
    "slug": "Sacai",
    "url": "https://store.sacai.jp",
    "logo": "https://store.sacai.jp/assets/front/img/common/sacai-logo.jpg?1628838577",
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
            "fields": ["email", "password", "first_name", "last_name", "house_number", "street", "zip", "city", "additional", "state", "country", "phone"],
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
            "fields": ["email", "password", "password_account", "link"]
        }
    ]
}
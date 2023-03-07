"""********************************************************************"""
"""                                                                    """
"""   [Apps] FootLockerModule.py                                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 03:13:55                                     """
"""   Updated: 29/09/2021 03:31:37                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

FootLockerModule = {
    "id": 6,
    "name": "FootLocker",
    "slug": "FootLocker",
    "url": "https://www.sneakersnstuff.com/",
    "logo": "https://www.nouvelobs.com/codepromo/static/shop/35979/logo/code-promo-sneakersnstuff.png",
    "version": "1.0.0",
    "locked": True,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Account Generator",
            "slug": "AccountGenerator",
            "permission": "default",
            "locked": False,
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code"],
        },
        {
            "id": 2,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "size","pickupLocation"],
        },
    ]
}
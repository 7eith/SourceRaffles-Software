"""********************************************************************"""
"""                                                                    """
"""   [Raffle] SOTFModule.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 00:12:44                                     """
"""   Updated: 29/09/2021 03:33:07                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

SOTFModule = {
    "id": 16,
    "name": "Sotf",
    "slug": "Sotf",
    "url": "https://www.sotf.com/en/raffle.php",
    "logo": "https://www.shoppingmap.it/storage/boutiques/6261-sotf.html/6261-sotf_logo.jpg",
    "version": "1.0.0",
    "locked": True,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code"],
        },
    ]
}
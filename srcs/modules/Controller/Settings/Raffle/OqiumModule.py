"""********************************************************************"""
"""                                                                    """
"""   [Raffle] OqiumModule.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 06/10/2021 18:40:58                                     """
"""   Updated: 10/10/2021 07:32:53                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

OqiumModule = {
    "id": 24,
    "name": "Oqium",
    "slug": "Oqium",
    "url": "https://oqium.com/",
    "logo": "https://cdn.shopify.com/s/files/1/0039/0096/4953/t/77/assets/logo.svg?v=1027763802310293649",
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
            "fields": ["email", "size", "first_name", "last_name", "address", "additional", "zip", "city", "country", "phone_number", "instagram"]
        }
    ]
}
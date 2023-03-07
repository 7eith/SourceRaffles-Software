"""********************************************************************"""
"""                                                                    """
"""   [Raffle] FootShopModule.py                                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 09/08/2021 05:25:18                                     """
"""   Updated: 01/10/2021 14:03:05                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

FootShopModule = {
    "id": 7,
    "name": "FootShop",
    "slug": "FootShop",
    "url": "https://releases.footshop.com/",
    "logo": "https://www.p3parks.com/-a15972---YW7-BM5R/footshop",
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
            "fields": ["email", "size", "first_name", "last_name", "phone_prefix", "phone", "house_number", "street", "zip", "city", "country_code",
                "additional",
                "state",
                "cc_number",
                "cc_month",
                "cc_year",
                "cc_cvv",
                "cc_type",
                "instagram"
            ]
        },
        {
            "id": 2,
            "name": "Account Generator",
            "slug": "AccountGenerator",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name"]
        }
    ]
}
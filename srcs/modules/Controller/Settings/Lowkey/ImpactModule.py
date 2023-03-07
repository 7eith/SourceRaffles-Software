"""********************************************************************"""
"""                                                                    """
"""   [Raffle] ImpactPremium.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 09:24:07                                     """
"""   Updated: 01/10/2021 14:13:37                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

ImpactModule = {
    "id": 8,
    "name": "Impact",
    "slug": "Impact",
    "url": "https://www.impact-premium.com/",
    "logo": "https://www.impact-premium.com/img/impact-premium-logo-1614674807.jpg",
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
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code", "country", "payment", "shipping"]
        }
    ]
}
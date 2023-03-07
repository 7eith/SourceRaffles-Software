"""********************************************************************"""
"""                                                                    """
"""   [Lowkey] BeamhillModule.py                                       """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 03:18:37                                     """
"""   Updated: 29/09/2021 03:25:50                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

BeamHillModule = {
    "id": 4,
    "name": "BeamHill",
    "slug": "BeamHill",
    "url": "https://www.impact-premium.com/",
    "logo": "https://www.impact-premium.com/img/impact-premium-logo-1614674807.jpg",
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
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code", "country", "payment", "shipping"]
        }
    ]
}
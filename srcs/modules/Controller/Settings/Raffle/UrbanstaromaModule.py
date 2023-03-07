"""********************************************************************"""
"""                                                                    """
"""   [Raffle] ImpactPremium.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 09:24:07                                     """
"""   Updated: 29/09/2021 03:33:23                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

UrbanstaromaModule = {
    "id": 19,
    "name": "Urbanstaroma",
    "slug": "Urbanstaroma",
    "url": "https://www.urbanstaroma.com/en",
    "logo": "https://pbs.twimg.com/profile_images/1182729330088140803/rGyL21us.jpg",
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
            "fields": ["email", "first_name", "last_name", "size", "message"]
        }
    ]
}
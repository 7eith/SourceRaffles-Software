"""********************************************************************"""
"""                                                                    """
"""   [Raffle] ImpactPremium.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 17/09/2021 09:24:07                                     """
"""   Updated: 29/09/2021 03:32:00                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

KellerModule = {
    "id": 9,
    "name": "Keller",
    "slug": "Keller",
    "url": "https://www.keller-x.de/",
    "logo": "https://www.keller-x.fr/keller.x/images/ksx-logo.svg",
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
            "fields": ["email", "size", "instagram", "country_code", "message"]
        }
    ]
}
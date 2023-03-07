"""********************************************************************"""
"""                                                                    """
"""   [Raffle] NakedModule.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 09/08/2021 04:59:32                                     """
"""   Updated: 03/10/2021 09:13:53                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

NakedModule = {
    "id": 11,
    "name": "Naked",
    "slug": "Naked",
    "url": "https://nakedcph.com",
    "logo": "https://img.rule.io/2880/60cc3ee8615ca",
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
            "fields": ["email", "first_name", "password"],
        },
        {
            "id": 2,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code", "instagram"]
        },
        {
            "id": 3,
            "name": "Account Verifier",
            "slug": "AccountVerifier",
            "locked": False,
            "permission": "default",
            "fields": ["email", "password"]
        }
    ]
}
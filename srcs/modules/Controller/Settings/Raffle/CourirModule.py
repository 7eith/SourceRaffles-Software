"""********************************************************************"""
"""                                                                    """
"""   [Raffle] CourirModule.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 03:12:09                                     """
"""   Updated: 03/10/2021 05:18:20                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

CourirModule = {
    "id": 22,
    "name": "Courir",
    "slug": "Courir",
    "url": "https://courir.fr",
    "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Courir_%28logo%29.svg/1200px-Courir_%28logo%29.svg.png",
    "version": "1.0.0",
    "locked": False,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Enter Raffle [Instore]",
            "slug": "EnterRaffleInstore",
            "permission": "default",
            "locked": False,
            "fields": ["email", "first_name", "last_name"]
        },
    ]
}
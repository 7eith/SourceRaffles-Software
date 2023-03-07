"""SVDModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 12/09/2021	 19:05	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

SVDModule = {
    "id": 15,
    "name": "SVD",
    "slug": "SVD",
    "url": "https://www.sivasdescalzo.com",
    "logo": "https://play-lh.googleusercontent.com/9_bf6BscrrTE6LC50IbtFIiS2mob173jy7bF5l_73NkL9VhrQLi6bqKyYOICfap-uIM",
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
            "fields": ["email", "password", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "region", "country_code"],
        },
        {
            "id": 2,
            "name": "Enter Raffle",
            "slug": "EnterRaffle",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "size"],
        },
    ]
}

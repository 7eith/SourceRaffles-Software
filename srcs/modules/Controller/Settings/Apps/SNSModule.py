"""SNSModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 12/09/2021	 11:03	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

SNSModule = {
    "id": 14,
    "name": "SNS",
    "slug": "SNS",
    "url": "https://www.sneakersnstuff.com/",
    "logo": "https://www.nouvelobs.com/codepromo/static/shop/35979/logo/code-promo-sneakersnstuff.png",
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
            "fields": ["email", "password", "size", "pickupLocation"],
        },
{
            "id": 2,
            "name": "Account Updater",
            "slug": "AccountUpdater",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name", "phone", "house_number", "street", "address2", "zip", "city", "country_code", "cc_number", "cc_expiration_month", "cc_expiration_year", "cc_cvv", "cc_type"],
        }
    ]
}
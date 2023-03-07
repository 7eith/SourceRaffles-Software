"""NittygrittyModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 12/09/2021	 10:43	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

NittyGrittyModule = {
    "id": 12,
    "name": "Nittygritty",
    "slug": "Nittygritty",
    "url": "https://nittygrittystore.com/",
    "logo": "https://nittygrittystore.com/assets/images/MainLogo.svg",
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
            "fields": ["email", "first_name", "last_name", "address", "zip", "city", "phone", "country_code", "size"],
        },
{
            "id": 2,
            "name": "Email Scraper",
            "slug": "EmailScraper",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password"]
        },
        {
            "id": 3,
            "name": "Email Confirmer",
            "slug": "EmailConfirmer",
            "permission": "default",
            "locked": False,
            "fields": ["link"]
        }
    ]
}

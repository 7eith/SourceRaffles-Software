"""BSTNModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 12/09/2021	 11:33	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

BSTNModule = {
    "id": 3,
    "name": "BSTN",
    "slug": "BSTN",
    "url": "https://raffle.bstn.com/",
    "logo": "https://thesneakersbible.fr/wp-content/uploads/2021/04/logo-bstn.jpeg",
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
            "fields": ["email", "first_name", "last_name", "house_number", "street", "additional", "city", "zip", "country", "gender", "instagram", "size"],
        },
        {
            "id": 3,
            "name": "Email Confirmer",
            "slug": "EmailConfirmer",
            "permission": "default",
            "locked": False,
            "fields": ["link"],
        },
{
            "id": 2,
            "name": "Email Scraper",
            "slug": "EmailScraper",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password"]
        }
    ]
}

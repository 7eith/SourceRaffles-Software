"""WoodWood.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 12/09/2021	 01:03	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

WoodWoodModule = {
    "id": 20,
    "name": "WoodWood",
    "slug": "WoodWood",
    "url": "https://www.woodwood.com/",
    "logo": "https://visitfrederiksberg.dk/wp-content/uploads/2019/09/Wood-Wood-Frederiksberg.jpg",
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
            "fields": ["email", "first_name", "last_name", "phone", "house_number", "street", "zip", "city", "country_code"]
        },
        {
            "id": 3,
            "name": "Email Scraper",
            "slug": "EmailScraper",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password"]
        },
        {
            "id": 4,
            "name": "Email Confirmer",
            "slug": "EmailConfirmer",
            "permission": "default",
            "locked": False,
            "fields": ["link"]
        }
    ]
}
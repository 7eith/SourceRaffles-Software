"""********************************************************************"""
"""                                                                    """
"""   [Raffle] AfewModule.py                                           """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 11/09/2021 16:42:19                                     """
"""   Updated: 29/09/2021 02:57:39                                     """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

AfewModule = {
    "id": 1,
    "name": "Afew",
    "slug": "Afew",
    "url": "https://en.afew-store.com/collections/sneaker-releases",
    "logo": "https://pbs.twimg.com/profile_images/1415268935935610882/5cCmTBDb_400x400.jpg",
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
            "fields": ["email", "size","first_name", "last_name", "phone", "address1", "address2", "zip", "city", "country_code", "province", "instagram"]
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
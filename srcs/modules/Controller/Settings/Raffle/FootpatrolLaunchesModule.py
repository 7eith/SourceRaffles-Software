"""EndModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 11/09/2021	 22:05	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

FootPatrolLaunchesModule = {
    "id": 38,
    "name": "FootpatrolLaunches",
    "slug": "FootpatrolLaunches",
    "url": "https://launches.footpatrol.com/",
    "logo": "https://www.footpatrol.com/skins/footpatrolgb-desktop/public/img/logos/logo-large-en.png",
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
            "fields": ["email", "password", "size"]
        },
        {
            "id": 2,
            "name": "Account Generator",
            "slug": "AccountGenerator",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name"]
        },
{
            "id": 3,
            "name": "Account Updater",
            "slug": "AccountUpdater",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name"]
        }
    ]
}
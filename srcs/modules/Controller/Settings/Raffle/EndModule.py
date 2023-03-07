"""EndModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 11/09/2021	 22:05	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

EndModule = {
    "id": 5,
    "name": "End",
    "slug": "End",
    "url": "https://endclothing.com/",
    "logo": "https://endtelevision.fr/wp-content/uploads/2020/05/END_TELEVIION_LOGO_2020.png",
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
            "fields": ["email", "password", "first_name", "last_name", "phone", "street_number", "street" ,"address2", "city", "region_name",
                       "zip", "country", "cc_number", "cc_month", "cc_year", "cc_cvv"]
        },
{
            "id": 3,
            "name": "Account Updater",
            "slug": "AccountUpdater",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name", "phone", "street_number", "street" ,"address2", "city", "region_name",
                       "zip", "country", "cc_number", "cc_month", "cc_year", "cc_cvv"]
        }
    ]
}
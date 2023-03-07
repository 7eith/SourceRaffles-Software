"""Stress95Module.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 22/09/2021	 11:35	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


KithModule = {
    "id": 10,
    "name": "Kith",
    "slug": "Kith",
    "url": "https://kith.com/",
    "logo": "https://journalduluxe.fr/files/kith-logo_86d8b72d09708ce73bef700055313953.png",
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
            "fields": ["email", "first_name", "last_name", "password"],
        },

    ]
}

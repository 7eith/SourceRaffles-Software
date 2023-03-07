"""Stress95Module.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 22/09/2021	 11:35	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


Stress95Module = {
    "id": 17,
    "name": "Stress95",
    "slug": "Stress95",
    "url": "https://stress95.com/",
    "logo": "https://stress95.com/static/assets/images/stress-logo-black.svg",
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

    ]
}

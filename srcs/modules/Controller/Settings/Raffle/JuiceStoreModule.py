"""JuiceStoreModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 04/10/2021	 13:37	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


JuiceStoreModule = {
    "id": 25,
    "name": "JuiceStore",
    "slug": "JuiceStore",
    "url": "https://juicestore.com/",
    "logo": "https://cdn.shopify.com/s/files/1/1417/5782/files/juice_e0e80a18-45c3-4b95-b77c-47fc4d14d62c_large.png?v=16387245306150966197",
    "version": "1.0.0",
    "locked": True,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Account Generator",
            "slug": "AccountGenerator",
            "permission": "default",
            "locked": False,
            "fields": ["email", "password", "first_name", "last_name", "password"],
        },

    ]
}

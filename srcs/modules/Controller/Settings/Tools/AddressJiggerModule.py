"""GeocodingModule.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 23/09/2021	 16:35	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

AddressJiggerModule = {
    "id": 34,
    "name": "Address Jigger",
    "slug": "AddressJigger",
    "url": "https://locationiq.com/",
    "logo": "https://locationiq.com/static/v2/images/logo.png",
    "version": "1.0.0",
    "locked": False,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "AddyJigger",
            "slug": "AddyJigger",
            "permission": "default",
            "locked": False,
            "fields": ["country", "address", "number"]
        }
    ]
}
"""Rezet.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 24/09/2021	 00:32	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

RezetStoreModule = {
    "id": 13,
    "name": "Rezet",
    "slug": "RezetStore",
    "url": "https://rezetstore.dk/en",
    "logo": "https://rezetstore.dk/static/media/rezet-logo--original.19790820.svg",
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
            "fields": ["email", "phone_number", "sku", "size", "country_code"],
        },
    ]
}
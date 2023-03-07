"""********************************************************************"""
"""                                                                    """
"""   [Raffle] BeamhillModule.py                                           """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 11/09/2021 16:42:19                                     """
"""   Updated: 29/09/2021 02:57:39                                     """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

BeamhillModule = {
    "id": 1,
    "name": "Beamhill",
    "slug": "Beamhill",
    "url": "https://en.Beamhill-store.com/collections/sneaker-releases",
    "logo": "https://pbs.twimg.com/profile_images/1415268935935610882/5cCmTBDb_400x400.jpg",
    "version": "1.0.0",
    "locked": True,
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
    ]
}
"""********************************************************************"""
"""                                                                    """
"""   [AIO] KlaviyoModule.py                                           """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 07/10/2021 04:37:20                                     """
"""   Updated: 07/10/2021 04:38:19                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

KlaviyoModule = {
    "id": 42,
    "name": "Klaviyo",
    "slug": "Klaviyo",
    "url": "",
    "logo": "https://e-sols.net/storage/2020/01/optimisation-google-form-integration.jpg",
    "version": "1.0.0",
    "locked": False,
    "permission": "default",
    "subModules": [
        {
            "id": 1,
            "name": "Scrape Form",
            "slug": "Scraper",
            "permission": "default",
            "locked": False,
            "fields": []
        },
        {
            "id": 2,
            "name": "Enter Form",
            "slug": "EnterForm",
            "permission": "default",
            "locked": False,
            "fields": [],
        }
    ]
}
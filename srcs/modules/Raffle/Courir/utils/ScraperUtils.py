"""********************************************************************"""
"""                                                                    """
"""   [utils] ScraperUtils.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 03/10/2021 02:07:34                                     """
"""   Updated: 03/10/2021 05:34:03                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import cloudscraper

import re
import json

from core.configuration import Configuration
from utilities import *

def scrapeRaffle(link):

    session = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome', # we want a chrome user-agent
            'mobile': True,
            'platform': 'android' # pretend to be a desktop by disabling mobile user-agents
        },
    )

    loyaltyRequired = "loyalty" in link

    response = session.get(link)

    try:
        storesData = re.search('const STORES = \'(.+?)\';', response.text).group(1)
        sizesData = re.search('const SIZES = \'(.+?)\';', response.text).group(1)

        stores = json.loads(storesData)
        sizes = json.loads(sizesData)
    except json.JSONDecodeError:
        Logger.error("Error while decoding Raffle!")

    productId = list(sizes.keys())[0]

    countryCode = link.split("/")[3]

    newLink = f"https://courir.captainwallet.com/{countryCode}/raffle-dunk-team-green"
    return {
        "link": link,
        "productId": productId,
        "stores": stores,
        "sizes": sizes,
        "loyalty": loyaltyRequired,
        "product": "Nike Dunk Low - Spartan Green",
        "image": "https://www.sneakerstyle.fr/wp-content/uploads/2021/04/nike-dunk-low-spartan-green-DD1391-101-800x500.jpg",
        "walletBaseURL": newLink
    }
    
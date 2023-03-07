"""********************************************************************"""
"""                                                                    """
"""   [requests] ScraperUtilities.py                                   """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/09/2021 17:32:53                                     """
"""   Updated: 14/11/2021 13:23:40                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import platform
from utilities import *
from core.configuration import Configuration
from proxies.ProxyManager import ProxyManager
import random

if "darwin" not in platform.system().lower():
    import helheim
    import cloudscraper

    macOs = False
else:
    macOs = True

def injection(session, response):
    if helheim.isChallenge(session, response):
        return helheim.solve(session, response)
    else:
        return response

def CreateCFSession():
    proxy = ProxyManager().getProxy()
    favorite: str = Configuration().getConfiguration()['CaptchaServices']['Favorite']

    if macOs:
        Logger.debug("Mac detected, creating hawk session for cloudflare")
        Logger.error("Subscription expired for Mac Cloudflare handling, please alert a staff member")
        input("Press a key to quit the bot")
        sys.exit()
        # time.sleep(5)
        # sys.exit()
        # import cf_clouscraper
        #
        # session = cf_clouscraper.inject_example.CreateHawkSession(
        #     provider=favorite.lower(),
        #     key=random.choice(Configuration().getConfiguration()['CaptchaServices'][favorite]))
        # session.proxies.update(proxy['proxy'])

    else:

        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome', # we want a chrome user-agent
                'mobile': False, # pretend to be a desktop by disabling mobile user-agents
                'platform': 'windows', # pretend to be 'windows' or 'darwin' by only giving this type of OS for user-agents
                'debug': True
            },
            requestPostHook=injection,
            # Add a hCaptcha provider if you need to solve hCaptcha
            captcha={
                'provider': favorite.lower(),
                'api_key': random.choice(Configuration().getConfiguration()['CaptchaServices'][favorite])
            }
        )

        helheim.wokou(session, random.choice(["chrome", "firefox"]))
        try:
            session.bifrost_clientHello = 'chrome'
            helheim.bifrost(session,'./bifrost.dll')
        except Exception as e:
            Logger.info(("Error while initiating session using bifrost : {}".format(str(e))))

        session.proxies.update(proxy['proxy'])

    return (session, proxy)
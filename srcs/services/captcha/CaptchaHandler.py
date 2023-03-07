"""********************************************************************"""
"""                                                                    """
"""   [captcha] CaptchaHandler.py                                      """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 05/09/2021 23:59:08                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import random

from core.configuration import Configuration
from .providers.TwoCaptcha import *
from .providers.CapMonster import *
# from srcs.services.captcha.providers import CapMonster

class CaptchaHandler():

    def __init__(self) -> None:

        self.configuration = Configuration().getConfiguration()['CaptchaServices']
        self.favoriteHandler = self.configuration['Favorite']

    def getBalance(self, providers="ALL"):

        if (providers == "2Captcha"):
            return (TwoCaptchaService(self.configuration['2Captcha'][0]).getBalance())

        if (providers == "CapMonster"):
            return (CapMonsterService(self.configuration['CapMonster'][0]).getBalance())

    def handleRecaptcha(self, siteKey, url, version="v2", invisible=0, proxy=None, pollingInterval=5):

        """
            handleRecaptcha
                siteKey = siteKey of website
                url = url of page
                version = version of captcha (V2|V3 - default: V2)
                invisible = is invisible? (True|False - default:False)
                proxy = use proxy? 
                pollingInterval = refresh rate
        """

        if (self.favoriteHandler == "2Captcha"):
            apiKey = random.choice(self.configuration['2Captcha'])

            return TwoCaptchaService(apiKey, pollingInterval).solveReCaptcha(siteKey, url, version, invisible, proxy)

        if (self.favoriteHandler == "CapMonster"):
            apiKey = random.choice(self.configuration['CapMonster'])
            
            return CapMonsterService(apiKey, pollingInterval).solveReCaptcha(siteKey, url, version, invisible, proxy)
            
    def handleHCaptcha(self, siteKey, url, invisible=0, proxy=None, pollingInterval=5):
        
        """
            handleHCaptcha
                siteKey = siteKey of website
                url = url of page
                invisible = is invisible? (1|0 - default:0)
                proxy = use proxy? 
                pollingInterval = refresh rate
        """

        if (self.favoriteHandler == "2Captcha"):
            apiKey = random.choice(self.configuration['2Captcha'])

            return TwoCaptchaService(apiKey, pollingInterval).solveHCaptcha(siteKey, url, invisible)

        if (self.favoriteHandler == "CapMonster"):
            apiKey = random.choice(self.configuration['CapMonster'])
            
            return CapMonsterService(apiKey, pollingInterval).solveHCaptcha(siteKey, url, invisible)
            
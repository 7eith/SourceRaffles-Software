"""********************************************************************"""
"""                                                                    """
"""   [EnterRaffle] EnterRaffleTask.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 00:21:21                                     """
"""   Updated: 10/09/2021 05:43:30                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import *
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
from services.captcha import CaptchaHandler


class EnterRaffleTask:

    def __init__(self, index, taskNumber, profile, raffle) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.profile: dict = profile
        self.raffle: dict = raffle

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, self.profile["email"])
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.captchaToken: str = None
        self.proxyLess = False

        """ Utilities """
        self.profile["Product"] = raffle["product"]
        self.link = raffle["link"]

        self.session, self.proxy = CreateCFSession()

        try:
            status = self.MainPage()
            if status == 1:
                Logger.success(f"{self.logIdentifier} Accessed main page !")
                self.success = False
                self.profile['status'] = "FAILED"
                
            else:
                self.success = False
                self.profile['status'] = "FAILED"
                
            if (not self.proxyLess):
                self.proxy = ProxyManager().rotateProxy(self.session, self.proxy)

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )
            Logger.error(str(error))
            self.profile["status"] = "FAILED"
            self.success = False

    def MainPage(self):

        Logger.info('Solving Cloudflare Challenge')
        try:
            r = self.session.get('https://www.sotf.com/en/raffle.php')
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while solving cloudflare : {}".format(str(e)))
            return -1
        if r.status_code != 200:
            Logger.error("Error while solving Cloudflare, stopping task")
        Logger.info('Successful solved Cloudflare Challenge')
        soup = BeautifulSoup(r.text, "html.parser")
        self.contatto_lang = soup.find('input', {'name': 'contatto_lang'})["value"]
        self.nome_campagne = soup.find('input', {"name": "nome_campagna"})["value"]

        color = soup.find('select', {"name": "reg_form_color"})
        try:
            color_choice = color.findAll("option")
            if len(color_choice) > 1:
                Logger.info("Colors found")
                Logger.info("Make sure to have colors in your csv in the Additional column !")
                self.color_needed = True
        except:
            Logger.info("No need to choose colors")
            self.color_needed = False
        return self.submit()

    def captcha(self):
        if (self.captchaToken == None):
            Logger.log(f"{self.logIdentifier} Solving Captcha...")

            captcha = CaptchaHandler().handleRecaptcha(
                '6Lf28x4UAAAAAKLEx3FwY67Cbvob4FkHBGaRvfiF',
                'https://www.sotf.com/en/raffle.php',
                invisible=1
            )

            if (captcha['success']):
                self.captchaToken = captcha['code']
                Logger.info(f"{self.logIdentifier} Successfully solved Captcha!")
            else:
                self.retry += 1

                Logger.warning(f"{self.logIdentifier} Invalid Captcha! Solving another Captcha... ({self.retry}/3)")
                Logger.error(f"{self.logIdentifier} {captcha['error']}")

                if (self.retry <= 3):
                    return self.captcha()
                else:
                    return -1
        
    def submit(self):

        captcha = self.captcha()
        if captcha == -1:
            Logger.error("Unvalid captcha received")
            return -1

        try:
            URL = 'https://www.sotf.com/en/raffle.php'
            if self.color_needed:
                final_data = {
                    'contatto_lang': self.contatto_lang,
                    'nome_campagna': self.nome_campagne,
                    'submitted': 'true',
                    'reg_form_email': self.profile["email"],
                    'reg_form_instagram_profile': self.profile["instagram"],
                    'reg_form_name': self.profile["first_name"],
                    'reg_form_surname': self.profile["last_name"],
                    'reg_form_email_pay': self.profile["paypal"],
                    'reg_form_nation': self.profile["country_code"],
                    'reg_form_fc': '',
                    'reg_form_city': self.profile["city"],
                    'reg_form_address': self.profile["street"],
                    'reg_form_address_number': self.profile["house_number"],
                    'reg_form_cap': self.profile["zip"],
                    'reg_form_province': self.profile["state"],
                    'reg_form_ph': self.profile["phone"],
                    'reg_form_size': self.profile["size"],
                    'reg_form_color': self.profile["additional"],
                    'g-recaptcha-response': captcha,
                    'button': 'send'
                }

            else:
                final_data = {
                    'contatto_lang': self.contatto_lang,
                    'nome_campagna': self.nome_campagne,
                    'submitted': 'true',
                    'reg_form_email': self.profile["email"],
                    'reg_form_instagram_profile': self.profile["instagram"],
                    'reg_form_name': self.profile["first_name"],
                    'reg_form_surname': self.profile["last_name"],
                    'reg_form_email_pay': self.profile["paypal"],
                    'reg_form_nation': self.profile["country_code"],
                    'reg_form_fc': '',
                    'reg_form_city': self.profile["city"],
                    'reg_form_address': self.profile["street"],
                    'reg_form_address_number': self.profile["house_number"],
                    'reg_form_cap': self.profile["zip"],
                    'reg_form_province': self.profile["state"],
                    'reg_form_ph': self.profile["phone"],
                    'reg_form_size': self.profile["size"],
                    'g-recaptcha-response': captcha,
                    'button': 'send'
                }

            Logger.info('Submitting Raffle Entry')
            try:
                r = self.session.post(URL, data=final_data)
            except ProxyError:
                Logger.error("Proxy Error, stopping task")
                return -1
            if r.status_code == 200:
                return 1
            else:
                Logger.error("Error while submitting entry, Status Code : " + str(r.status_code))
                return -1
        except ProxyError:
            Logger.error('Proxy Error, stopping task')
            return -1
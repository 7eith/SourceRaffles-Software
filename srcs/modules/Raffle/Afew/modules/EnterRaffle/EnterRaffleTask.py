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

from core.configuration.Configuration import Configuration
from utilities import *
from bs4 import BeautifulSoup
import random
from requests.exceptions import ProxyError


class EnterRaffleTask:

    def initSession(self):
        self.session = requests.Session()

        if not Configuration().getConfiguration()["ProxyLess"]:
            self.proxy = ProxyManager().getProxy()
            self.session.proxies.update(self.proxy['proxy'])
        else:
            self.proxy = "Localhost"
            self.proxyLess = True

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
        self.link = raffle["metadata"]["entryUrl"]

        self.initSession()

        try:
            status = self.submit()
            if status == 1:
                Logger.success(f"{self.logIdentifier} Entry submitted !")
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

    def submit(self):
        Logger.info("Getting sizes")
        try:
            self.rafflelink = self.link.replace("en.afew-store.com", "raffles.afew-store.com") \
                .replace("de.afew-store.com", "en.afew-store.com")
            json_link = self.rafflelink + ".json"
            response = self.session.get(json_link)
            variant_wanted = "not found"

            temp = response.json()["product"]["variants"]

            if self.profile["size"].lower() == "random":
                size_info = random.choice(temp)
                variant_wanted = size_info["id"]
            for size in temp:
                if size["title"] == self.profile["size"]:
                    variant_wanted = size["id"]
            if variant_wanted == "not found":
                Logger.info("Size not found, getting random one")
                size_info = random.choice(temp)
                variant_wanted = size_info["id"]

        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting sizes, stopping task : {}".format(str(e)))
            return -1

        if response.status_code != 200:
            Logger.error("Error while getting sizes {}".format(response.status_code))
            return -1

        Logger.info("Adding to cart...")
        try:
            response = self.session.get('https://raffles.afew-store.com/cart/{}:1'.format(variant_wanted))
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1

        if response.status_code != 200:
            Logger.error("Error while adding to cart, check the size chosen")
            return -1

        soup = BeautifulSoup(response.text, "html.parser")
        token = soup.find('input', {'name': 'authenticity_token'})["value"]
        link = soup.find('form', {'class': 'edit_checkout'})["action"]
        checkout_url = "https://raffles.afew-store.com" + link

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://raffles.afew-store.com',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }

        data = [
            ('_method', 'patch'),
            ('authenticity_token', token),
            ('previous_step', 'contact_information'),
            ('step', 'shipping_method'),
            ('checkout[email]', self.profile["email"]),
            ('checkout[attributes][locale]', 'fr'),
            ('checkout[attributes][instagram]', self.profile["instagram"]),
            ('checkout[shipping_address][first_name]', ''),
            ('checkout[shipping_address][first_name]', self.profile["first_name"]),
            ('checkout[shipping_address][last_name]', ''),
            ('checkout[shipping_address][last_name]', self.profile["last_name"]),
            ('checkout[shipping_address][company]', ''),
            ('checkout[shipping_address][company]', ''),
            ('checkout[shipping_address][address1]', ''),
            ('checkout[shipping_address][address1]', self.profile["address1"]),
            ('checkout[shipping_address][address2]', ''),
            ('checkout[shipping_address][address2]', self.profile["address2"]),
            ('checkout[shipping_address][city]', ''),
            ('checkout[shipping_address][city]', self.profile["city"]),
            ('checkout[shipping_address][country]', ''),
            ('checkout[shipping_address][country]', self.profile["country_code"]),
            ('checkout[shipping_address][province]', self.profile["province"]),
            ('checkout[shipping_address][zip]', ''),
            ('checkout[shipping_address][zip]', self.profile["zip"]),
            ('checkout[shipping_address][phone]', ''),
            ('checkout[shipping_address][phone]', self.profile["phone"]),
            ('checkout[remember_me]', ''),
            ('checkout[remember_me]', '0'),
            ('checkout[client_details][browser_width]', str(random.randint(700, 800))),
            ('checkout[client_details][browser_height]', str(random.randint(700, 800))),
            ('checkout[client_details][javascript_enabled]', '1'),
            ('checkout[client_details][color_depth]', '24'),
            ('checkout[client_details][java_enabled]', 'false'),
            ('checkout[client_details][browser_tz]', '-120'),
        ]

        try:
            response = self.session.post(checkout_url, headers=headers, data=data)
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1

        if response.status_code != 200:
            Logger.error("Error while submitting informations")
            return -1
        else:
            Logger.info("Informations submitted")

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            token = soup.find('input', {'name': 'authenticity_token'})["value"]
        except Exception as e:
            Logger.error("Error while getting authenticity token : {}".format(str(e)))
            return -1

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }

        params = (
            ('previous_step', 'contact_information'),
            ('step', 'shipping_method'),
        )

        Logger.info("Getting shipping methods")
        try:
            response = self.session.get(checkout_url,
                                        headers=headers, params=params)
        except ProxyError:
            Logger.error("Proxy Error, stopping task")
            return -1
        except Exception as e:
            Logger.error("Error while getting shipping methods : {}".format(str(e)))
            return -1

        if response.status_code != 200:
            Logger.error("Error while getting shipping methods")
            return -1
        try:
            page_html = response.text
            page_soup = BeautifulSoup(page_html, 'html.parser')
            shipping_rate = page_soup.find("div", {"class": "radio-wrapper"})['data-shipping-method']
        except:
            Logger.error("Error while getting shipping rates, to fix it add a province to your csv")
            return -1

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://raffles.afew-store.com',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            '_method': 'patch',
            'authenticity_token': token,
            'previous_step': 'shipping_method',
            'step': 'payment_method',
            'checkout[shipping_rate][id]': shipping_rate,
            'checkout[client_details][browser_width]': '711',
            'checkout[client_details][browser_height]': '746',
            'checkout[client_details][javascript_enabled]': '1',
            'checkout[client_details][color_depth]': '24',
            'checkout[client_details][java_enabled]': 'false',
            'checkout[client_details][browser_tz]': '-120'
        }

        try:
            response = self.session.post(checkout_url, headers=headers, data=data)

        except ProxyError:
            Logger.error("Proxy Error")
            return -1

        if response.status_code != 200:
            Logger.error("Error while submitting shipping method")
            return -1
        else:
            Logger.info("Shipping method submitted, submitting the entry...")

        soup = BeautifulSoup(response.text, "html.parser")
        token = soup.find('input', {'name': 'authenticity_token'})["value"]

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
        }

        params = (
            ('previous_step', 'payment_method'),
            ('step', 'review'),
        )
        try:
            response = self.session.get(checkout_url, headers=headers, params=params)
        except ProxyError:
            Logger.error("Proxy Error")
            return -1

        if response.status_code != 200:
            Logger.error("Error while submiting payment")
            return -1

        page_soup = BeautifulSoup(response.text, 'html.parser')
        price = page_soup.find("input", {"name": "checkout[total_price]"})['value']

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://raffles.afew-store.com',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            '_method': 'patch',
            'authenticity_token': token,
            'previous_step': 'payment_method',
            'step': 'review',
            's': '',
            'checkout[payment_gateway]': '39963820118',
            'checkout[different_billing_address]': 'false',
            'checkout[client_details][browser_width]': '711',
            'checkout[client_details][browser_height]': '746',
            'checkout[client_details][javascript_enabled]': '1',
            'checkout[client_details][color_depth]': '24',
            'checkout[client_details][java_enabled]': 'false',
            'checkout[client_details][browser_tz]': '-120'
        }

        try:
            response = self.session.post(checkout_url, headers=headers, data=data)
        except ProxyError:
            Logger.error("Proxy Error")
            return -1
        if response.status_code != 200:
            Logger.error("Error while submitting payment (gateway)")
            return -1

        soup = BeautifulSoup(response.text, "html.parser")
        token = soup.find('input', {'name': 'authenticity_token'})["value"]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://raffles.afew-store.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://raffles.afew-store.com',
            'Alt-Used': 'raffles.afew-store.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            '_method': 'patch',
            'authenticity_token': token,
            'checkout[total_price]': price,
            'complete': '1',
            'checkout[client_details][browser_width]': '711',
            'checkout[client_details][browser_height]': '746',
            'checkout[client_details][javascript_enabled]': '1',
            'checkout[client_details][color_depth]': '24',
            'checkout[client_details][java_enabled]': 'false',
            'checkout[client_details][browser_tz]': '-120'
        }

        try:
            response = self.session.post(checkout_url, headers=headers, data=data)
        except ProxyError:
            Logger.error("Proxy Error")
            return -1
        except Exception as e:
            Logger.error("Error while submitting entry : {}".format(str(e)))
            return -1

        if response.status_code != 200:
            Logger.error("Error while finishing entry")
            return -1
        else:
            return 1

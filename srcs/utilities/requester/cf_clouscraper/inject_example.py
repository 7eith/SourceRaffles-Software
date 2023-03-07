import ssl
import cloudscraper
from .hawk_cf import CF_2, Cf_challenge_3
import re

def perform_request(self, method, url, *args, **kwargs):
    if "proxies" in kwargs or "proxy" in kwargs:
        return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs)
    else:
        return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs,proxies=self.proxies)
# monkey patch the method in
cloudscraper.CloudScraper.perform_request = perform_request

#cap challenge
@staticmethod
def is_New_Captcha_Challenge(resp):
    try:
        return (
                resp.headers.get('Server', '').startswith('cloudflare')
                and resp.status_code == 403
                and re.search(
                    r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/.*/v1',
                    resp.text,
                    re.M | re.S
                )
                and re.search(r'window._cf_chl_opt', resp.text, re.M | re.S)
        )
    except AttributeError:
        pass

    return False
cloudscraper.CloudScraper.is_New_Captcha_Challenge = is_New_Captcha_Challenge

#normal challenge
@staticmethod
def is_New_IUAM_Challenge(resp):
    try:
        return (
                resp.headers.get('Server', '').startswith('cloudflare')
                and resp.status_code in [429, 503]
                and re.search(
                    r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/jsch/v1',
                    resp.text,
                    re.M | re.S
                )
                and re.search(r'window._cf_chl_opt', resp.text, re.M | re.S)
        )
    except AttributeError:
        pass

    return False
cloudscraper.CloudScraper.is_New_IUAM_Challenge = is_New_IUAM_Challenge


def is_fingerprint_challenge(resp):
    try:
        if resp.status_code == 429:
            if "/fingerprint/script/" in resp.text:
                return True
        return False
    except:
        pass


def injection(session, response):
    if session.is_New_IUAM_Challenge(response):
        return CF_2(session,response,key="test_1fdcce24-5733-42a2-8313-04e590cd3393",captcha=False,debug=True).solve() # FALSE is actually the default value but is displayed here to show that you need to have it true for captcha handling
                                                    # note that currently no captcha token getter is provided you can edit the file and add your solution
    elif session.is_New_Captcha_Challenge(response):
        return CF_2(session, response, key="test_1fdcce24-5733-42a2-8313-04e590cd3393", captcha=True,
                    debug=True).solve()
    elif is_fingerprint_challenge(response):
        return Cf_challenge_3(session,response,key="test_1fdcce24-5733-42a2-8313-04e590cd3393",debug=True).solve()
    else:
        return response

# ------------------------------------------------------------------------------- #


# update our ssl settings
ssl_context = ssl.create_default_context()
ssl_context.set_ciphers('ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:AECDH-AES128-SHA:AECDH-AES256-SHA')
ssl_context.set_ecdh_curve('prime256v1')
ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
ssl_context.check_hostname = False


def createHawkSession(provider, key):
    scraper = cloudscraper.create_scraper(
        browser={
            'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            'platform': 'darwin'
        },
        captcha={'provider': provider,
                 'api_key': key
                 },
        doubleDown=False,
        requestPostHook=injection,
        debug=False,
        ssl_context=ssl_context
    )
    return scraper

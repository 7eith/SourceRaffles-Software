"""scrapeRaffles.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 01/12/2021	 15:13	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


def fetchSoleboxRaffles():
    headers = {
        "authority": "blog.solebox.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "dnt": "1",
    }

    response = requests.get("https://blog.solebox.com/", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    raffles = [
        link
        for link in soup.find_all("a")
        if link.has_attr("title") and "instore" in link["title"].lower()
    ]

    formatedRaffles = list()
    for raffle in raffles:
        formatedRaffles.append(
            {
                "url": raffle["href"],
                "name": raffle["title"],
                "image": raffle.find("img")["src"],
            }
        )

    return formatedRaffles

def parseSoleboxForm(raffle):

    headers = {
        "authority": "blog.solebox.com",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://blog.solebox.com/",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7",
        "dnt": "1",
    }

    response = requests.get(raffle["url"], headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    formContainer = soup.select("form")[0]
    formURL = formContainer["action"]
    qs = parse_qs(urlparse(formURL).query)

    raffle["formURL"] = formURL
    raffle["u"] = qs["u"][0]
    raffle["id"] = qs["id"][0]

    raffleParams = dict()
    print(raffle['formURL'])

    for formInput in formContainer.find_all("div", class_="mc-field-group"):
        # print(formInput.span)
        if "MMERGE" in formInput.label["for"]:
            # formInput.span.decompose()
            if "month" in formInput.label["for"]:
                raffleParams["Birthday"] = formInput.label["for"].split("-")[1]
            if "Instagram" in formInput.label.text:
                raffleParams["Instagram"] = formInput.label["for"].split("-")[1]

            if "Store" in formInput.label.text:
                values = list()

                for store in formInput.find_all("option"):
                    if len(store) != 0:
                        values.append(store["value"].strip())

                raffleParams["Store"] = {
                    "fieldName": formInput.label["for"].split("-")[1],
                    "values": values,
                }

            if "Size" in formInput.label.text:
                values = list()

                for size in formInput.find_all("option"):
                    if len(size) != 0:
                        values.append(size["value"].strip())

                raffleParams["Sizes"] = {
                    "fieldName": formInput.label["for"].split("-")[1],
                    "values": values,
                }

    raffle["params"] = raffleParams
    print(raffle)

if __name__ == '__main__':
    # raffles = fetchSoleboxRaffles()
    # print(raffles)

    r = [{'url': 'https://blog.solebox.com/dunklowgoldenrod/', 'name': 'NIKE DUNK LOW ‚GOLDENROD‘ – INSTORE RAFFLE', 'image': 'https://blog.solebox.com/wp-content/uploads/2021/11/IG_1151293-1051639-Dunk-Low-Retro-black-goldenrod-white-1-400x500.jpg'}, {'url': 'https://blog.solebox.com/amamanierexnikeairjordan/', 'name': 'A MA MANIERE X NIKE AIR JORDAN 1 HIGH – INSTORE RAFFLE', 'image': 'https://blog.solebox.com/wp-content/uploads/2021/11/DO7097-100_E_PREM-400x400.png'}]
    for elt in r:
        parseSoleboxForm(elt)
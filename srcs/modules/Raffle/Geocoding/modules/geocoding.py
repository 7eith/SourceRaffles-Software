"""geocoding.py                                                        """
"""                                                                    """
"""   Author: loulou <louisamorosbessede@gmail.com>                    """
"""                                                                    """
"""   Created: 14/09/2021	 00:51	                                   """
"""                                                                    """
"""   Source Group. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


import random, csv, os, time
import numpy as np
from colorama import Fore
import sys
from utilities import *


class Geocoding:
    def __init__(self):
        self.generate_addresses()

    def get_address_from_coordinates(self, lat, lon):
        pk = "pk.2964a7f649a02d966c7739e6d2bae82b"
        url = "https://eu1.locationiq.com/v1/reverse.php?key={}&lat={}&lon={}&format=json".format(pk, lat, lon)
        response = requests.get(url)
        if response.status_code == 200:
            Logger.debug("Response received : {}".format(response.json()))
            address = response.json()["address"]
            try:
                number = address["house_number"]
            except KeyError:
                number = random.randint(1, 10)
            try:
                road = address["road"]
                try:
                    city = address["city"]
                except KeyError:
                    city = "notfound"
                if city == "notfound":
                    try:
                        city = address['village']
                    except KeyError:
                        city = "notfound"
                if city == "notfound":
                    try:
                        city = address['town']
                    except KeyError:
                        city = "notfound"
                country = address["country"]
                postcode = address["postcode"]
                return number, road, city, country, postcode
            except KeyError as e:
                Logger.error("{} field not valid".format(str(e)))
                return None
        else:
            if response.json()["error"] == "Invalid key":
                Logger.error("Invalid api key, please check if your key is the good one.")

    def get_coordinates_from_zip(self, country, zipcode):
        country_list = ['AT', 'CH', 'DE', 'DK', 'ES', 'FI', 'FR', 'GB', 'HR', 'HU', 'IE', 'IT', 'SE', 'US']
        if country.lower() == "random":
            country = random.choice(country_list)
        r = requests.get("https://sourceraffles-db-default-rtdb.europe-west1.firebasedatabase.app/Geocoding/{}.json".format(country)).json()
        if r is None:
            Logger.error("Country not found")
            time.sleep(3)
            sys.exit()
        else:
            Logger.info("Country found")
            if zipcode.lower() == "random":
                postalCodeInfo = random.choice(list(r.values()))
            else:
                try:
                    postalCodeInfo = r.get(zipcode)
                except:
                    Logger.info("Zipcode not found")
                    time.sleep(3)
                    sys.exit()
            long, lat = float(postalCodeInfo[0]), float(postalCodeInfo[1])
            return long, lat

    def create_random_point(self, x0, y0):
        distance = random.randint(30, 1000)
        r = distance / 111300
        u = np.random.uniform(0, 1)
        v = np.random.uniform(0, 1)
        w = r * np.sqrt(u)
        t = 2 * np.pi * v
        x = w * np.cos(t)
        x1 = x / np.cos(y0)
        y = w * np.sin(t)
        return x0 + x1, y0 + y
    
    def get_addy_from_zip(self, country, zipcode):
        lat, lon = self.get_coordinates_from_zip(country, zipcode)
        lat, lon = self.create_random_point(lat, lon)
        addy = self.get_address_from_coordinates(lat, lon)
        if addy:
            return list(addy)
        else:
            return None
    
    def generate_addresses(self):
        country = input(f'{Fore.MAGENTA}CountryCode to scrape addresses from : ')
        zip_code = input(f'{Fore.MAGENTA}Zipcode to scrape addresses from : ')
        while True:
            try:
                number_to_generate = int(input(f'{Fore.MAGENTA}Number of addresses to scrape : '))
                break
            except TypeError:
                Logger.error("Please enter a valid number !")
    
        Logger.info("Scraping addresses")
        counter = 0
        while counter < number_to_generate:
            result = self.get_addy_from_zip(country, zip_code)
            if result:
                path = r"/tools/addresses-{}-{}.csv".format(country, zip_code)
                path_to_folder = os.getcwd()
                with open(path_to_folder + path, 'a', newline='', encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow(result) # it's a list
                time.sleep(1)
                counter += 1
                Logger.info("Address found, sleeping...")
            else:
                Logger.error("Unvalid address, retrying...")
                time.sleep(1)
        Logger.success("Addresses successfully scraped !")
        time.sleep(2)
        Logger.info("Press any key to go back to the menu.")
        input()


if __name__ == '__main__':
    import requests
    os.chdir(r"/Users/louis/Desktop/SourceRaffles-main")
    # generate_addresses()
    # saveCsv()
    # generate_addresses()

    def saveCsv(self):
        path = "/Users/louis/Desktop/countries"
        jsonFile = {}
        list_csv = []
        os.chdir(r"/Users/louis/Desktop/countries")
        for file in os.listdir(path):
            if "csv" in file:
                list_csv.append(file)
        for csvName in list_csv:
            csvPath = path + "/" + csvName
            countryInfo = {}
            print("handling csv : {}".format(csvName))
            try:
                with open(csvPath, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=',')
                    for row in csv_reader:
                        country = row["Country_code"]
                        postal_code = row["Postal_code"]
                        Latitude = row["Latitude"]
                        Longitude = row["Longitude"]
                        countryInfo[postal_code] = [Latitude, Longitude]
                jsonFile[country] = countryInfo
            except Exception as e:
                print("error for csv : {} ".format(csvName) + str(e))
        import json
        with open("JsonCountry.json", "w") as file:
            json.dump(jsonFile, file)
        r = requests.put("https://sourceraffles-db-default-rtdb.europe-west1.firebasedatabase.app/Geocoding.json", json=jsonFile)

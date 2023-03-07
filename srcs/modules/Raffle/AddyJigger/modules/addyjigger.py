"""AddyJigger.py                                                        """
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



class Addyjigger:
    def __init__(self):

        self.street_name = {
            "France": ['rue', 'r', 'boulevard', 'blvd', 'avenue', 'av', 'chemin', 'ch']

        }
        self.list_letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        self.list_double_letter = ['a', 'e', 'i', 'o', 'u', 'n', 'm', 'p']
        self.jig_to_csv()

    def jig_address(self, jig, address, number):

        if random.randint(1, 3) == 2:
            point = ". "
        else:
            point = " "

        choice = random.randint(1, 4)
        if choice == 3 and len(address) > 5:
            address = address[:-1]
        elif choice == 4 and len(address) > 5:
            address = address[1:]
        elif choice == 1:
            for letter in address:
                if letter.lower() in self.list_double_letter:
                    try:
                        index = address.index(letter)
                        address = address[:index] + letter + address[index:-1]
                    except:
                        pass
                    finally:
                        break
        else:
            if random.randint(1, 3) == 2:
                address = address + address[-1]
            else:
                address = address[0] + address

        if random.randint(1, 3) == 1:
            number = random.choice(self.list_letter) + random.choice(self.list_letter) + ' n' + point + number
        else:
            number = 'n' + point + number

        address = jig + point + address
        final = address + ' ' + number
        return [address, number, final]

    def jig_to_csv(self):
        try:
            numberTime = int(input("Choose number of time to jig each addresses : "))

            source_information = []
            path = os.getcwd()
            path_to_file = r"/resources/AddyJigger/address_jigger.csv"
            with open(path + path_to_file, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:
                    source_information.append(row)

            list_jigged = []
            for addy in source_information:
                country, address, number = addy['country'], addy['address'], addy['number']

                try:
                    jig_list = self.street_name[country]
                    while len(jig_list) < numberTime:
                        jig_list.append(random.choice(jig_list))
                except KeyError:
                    jig_list = ["" for i in range(numberTime)]

                for jig in jig_list:
                    addy_jig = self.jig_address(jig=jig, address=address, number=number)
                    list_jigged.append(addy_jig)

            path = os.getcwd()
            path_to_file = r"/resources/AddyJigger/jigged_addresses.csv"
            with open(path + path_to_file, mode='w', newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for addy in list_jigged:
                    writer.writerow(addy)

            Logger.success("Addresses successfully jigged !")

        except FileNotFoundError:
            print("Error while finding csv ! Please check the guide and open a ticket if it's still not working")

        except Exception as e:
            print("Error while jigging addys : " + str(e))
        input("Press Enter to continue")
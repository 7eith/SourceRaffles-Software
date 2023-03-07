"""********************************************************************"""
"""                                                                    """
"""   [prompt] PromptRaffle.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 13/11/2021 21:13:59                                     """
"""   Updated: 13/11/2021 21:17:33                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary
import requests

from utilities import *
from user import User

def PromptRaffle(moduleName):
	
	Logger.info("If you see a live raffle not live here contact the Team!")
	
	token = User().getToken()

	response = requests.get(
		f"{getAPI()}/v3/raffles",
		headers={
			"Authorization": f"Bearer {token}",
		},
		json={
			"moduleName": moduleName
		}
	)

	responseData = response.json()

	if (responseData['status'] is False):
		Logger.error("Error has occured! Open ticket please.")
		Logger.debug(response.text)
		input("")
		return None

	raffles = [raffle for raffle in responseData['raffles'] if raffle["active"]]

	if len(raffles) == 0:
		Logger.error(
			"No raffles availables.. If you see a live raffle not live here contact the Team!"
		)
		input("")
		return None

	Choices = []
	for raffle in raffles:
		Choices.append(questionary.Choice(
			title=[
				("class:purple", raffle['name']),
				("class:text", " [ "),
				("class:grey", '{message} successfull entries'.format(message=raffle['entriesCount'])),
				("class:text", " ]")
			],
			value={
				"raffle": raffle
			}
		))

	Choices.append(
		questionary.Choice(title=[("class:red", "Exit")], value={"slug": "Exit"})
	)

	answer = questionary.select(
		"Which raffles do you want to run?",
		choices=Choices,
	).ask()

	if "slug" in answer:
		return None
	else:
		if (len(answer["raffle"]["metadata"]) > 0):
			answer["raffle"]["metadata"] = answer["raffle"]["metadata"][0]
		return answer["raffle"]

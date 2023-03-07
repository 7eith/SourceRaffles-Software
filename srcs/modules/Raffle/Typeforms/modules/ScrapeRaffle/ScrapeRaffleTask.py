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
import requests

from services.captcha import CaptchaHandler
from utilities import *
from bs4 import BeautifulSoup
import json
from dhooks import Webhook, Embed


class ScrapeRaffleTask:

    def initSession(self):

        self.session = requests.Session()

    def __init__(self, index, taskNumber, raffle, csvName) -> None:

        """ Props """
        self.index: int = index + 1
        self.taskNumber: int = taskNumber
        self.raffleUrl: str = raffle
        self.csvName: str = csvName

        """ Store """
        self.logIdentifier: str = "[{}/{} - {}]".format(self.index, self.taskNumber, "Form Scraper")
        self.state: str = "PENDING"
        self.success: bool = False
        self.retry: int = 0
        self.maxRetry: int = 10
        self.captchaToken: str = None
        self.proxyLess = False

        """ Utilities """
        self.initSession()

        try:

            status = self.executeTask()

            if (status == 1):
                Logger.success(f"{self.logIdentifier} Successfully scraped raffle!")
                input("Press a key to continue")
            else:
                print(status)
                Logger.error(f"{self.logIdentifier} Error while scraping raffle!")

        except Exception as error:
            Logger.error(
                f"{self.logIdentifier} Exception has occured when running task!"
            )

            Logger.error(str(error))

    def executeTask(self):

        r = requests.get(self.raffleUrl)
        soup = BeautifulSoup(r.content, "html.parser")
        scripts = soup.find_all("script")
        script = str(scripts[2])
        jsonData = script.split("form: ")[1].split("messages:")[0].rsplit(',', 1)[0]
        jsonData = json.loads(jsonData)

        listChoicesFields = []
        fieldsList = []

        for field in jsonData["fields"]:
            fieldsList.append(field["title"])

        for field in jsonData["fields"]:
            if field["type"] in ["dropdown", "multiple_choice"]:
                listChoicesFields.append(field)

        path_to_folder = os.getcwd()
        path = r"/shops/Typeforms/{}.csv".format(self.csvName)
        with open(path_to_folder + path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(fieldsList)

        Logger.success('Csv created !')
        Logger.info("Sending informations to fill to discord")

        try:
            hook = Webhook(
                Configuration().getConfiguration()['WebhookURL'])
            embed = Embed(
                description='',
                color=7484927,
                timestamp='now',
                title="Custom Typeform Scraper"
            )
            embed.set_author(name="SourceRaffles",
                             icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            for field in listChoicesFields:
                text = "You have to choose an answer for the question : **{}**".format(field["title"]) + '\n'
                text += "You can choose between the following answers : \n"
                choices = field["properties"]["choices"]
                for choice in choices:
                    if field["type"] == 'dropdown':
                        text += "to answer : " + "__{}__".format(choice["label"]) + " fill : `{}` \n".format(
                            choice["label"])
                    if field["type"] == 'multiple_choice':
                        text += "to answer : " + "__{}__".format(choice["label"]) + " fill : `{}` \n".format(choice["id"])
                embed.add_field(name='Field requiring a choice found ! ', value=text, inline=False)
        except Exception as e:
            Logger.error("Error while making webhook : {}".format(str(e)))

        try:
            hook.send(embed=embed)
        except Exception as e:
            Logger.error("Couldn't send informations to fill because there were too many, displaying information on screen, press a key to display them and fill your csv accordingly")
            input()
            for field in listChoicesFields:
                text = "You have to choose an answer for the question : {}".format(field["title"]) + '\n'
                text += "You can choose between the following answers : \n"
                choices = field["properties"]["choices"]
                for choice in choices:
                    if field["type"] == 'dropdown':
                        text += "to answer : " + "{}".format(choice["label"]) + " fill : {} \n".format(
                            choice["label"])
                    if field["type"] == 'multiple_choice':
                        text += "to answer : " + "{}".format(choice["label"]) + " fill : {} \n".format(
                            choice["id"])
                print(text)
        Logger.success("Informations sent !")
        return 1


if __name__ == '__main__':
    
    os.chdir("/Users/louis/Desktop/CLI-master")
    


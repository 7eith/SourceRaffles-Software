"""********************************************************************"""
"""                                                                    """
"""   [Discord] EnterRaffleNotifier.py                                 """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 10/09/2021 05:46:48                                     """
"""   Updated: 22/11/2021 16:34:19                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from discord_webhook import DiscordWebhook, DiscordEmbed
from core.configuration import Configuration

from user import User
from utilities import *
import requests

def NotifyEnteredAccount(module, task, raffle, metadata=None):

    try:
        token = User().getToken()
        
        payload = {
            "moduleName": module['name'],
            "raffleId": raffle['_id'],
            "email": task.profile['email'],
        }

        if ("size" in task.profile):
            payload['size'] = task.profile['size']

        if (metadata is not None):
            payload['metadata'] = metadata

        response = requests.post(
            f"{getAPI()}/v3/raffles/entry",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json=payload
        )

        if (response.status_code != 200):
            Logger.debug(f"Error while log success {response.text}")
            
    except Exception as error:
        Logger.debug(f"Got an error when trying to log Success")
        Logger.debug(f"Error: {error}")
        
    webhookURL = Configuration().getConfiguration()['WebhookURL']
    
    if (Configuration().getUserSettings()['NotifyEachTask'] is False):
        return 

    if (Configuration().getUserSettings()['NotifyFailedTask'] is False and task.success == False):
        return 
        
    try:
        if (webhookURL):
            webhook = DiscordWebhook(
                url=webhookURL,
                username='SourceRaffles',
                avatar_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936'
            )

            embed = DiscordEmbed(
                timestamp="now",
                color=7484927 if task.success else 16724787
            )

            embed.set_thumbnail(
                url=raffle['image']
            )

            embed.set_author(
                name="Successfull entry" if task.success else "Failed entry",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Email', value='||{}||'.format(task.profile['email']), inline=False)

            if ("size" in task.profile):
                embed.add_embed_field(name='Size', value='{}'.format(task.profile['size']), inline=False)
    
            if ("Size" in task.profile):
                embed.add_embed_field(name='Size', value='{}'.format(task.profile['Size']), inline=False)

            embed.add_embed_field(name='Product', value='[{}]({})'.format(raffle['product']['name'], raffle['url']), inline=False)

            if (task.profile['status'] == "CONFIRMED"):
                embed.add_embed_field(name='Confirmed', value='{}'.format("Yes"), inline=False)
                
            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            if (Configuration().getUserSettings()['NotifyEachTask'] is True):
                webhook.add_embed(embed)
                webhook.execute()
                
    except Exception as error:
        pass

def NotifyCourirInstoreEntered(module, task, raffle, walletURL):

    webhookURL = Configuration().getConfiguration()['WebhookURL']

    if (Configuration().getUserSettings()['NotifyEachTask'] is False):
        return 

    if (Configuration().getUserSettings()['NotifyFailedTask'] is False and task.success == False):
        return 
        
    try:
        if (webhookURL):
            webhook = DiscordWebhook(
                url=webhookURL,
                username='SourceRaffles',
                avatar_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936'
            )

            embed = DiscordEmbed(
                timestamp="now",
                color=7484927 if task.success else 16724787
            )

            embed.set_thumbnail(
                url=raffle['image']
            )

            embed.set_author(
                name="Click here to add it to your wallet!",
                url=walletURL,
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[Courir - Instore]({})".format(module['url']), inline=False)
            embed.add_embed_field(name='Email', value='||{}||'.format(task.profile['email']), inline=False)
            embed.add_embed_field(name='Name', value='||{} {}||'.format(task.profile['first_name'], task.profile['last_name']), inline=False)
            embed.add_embed_field(name='Product', value='[{}]({})'.format(raffle['product'], raffle['link']), inline=False)
            embed.add_embed_field(name='Store', value='{}'.format(task.profile['Shop']), inline=False)
            embed.add_embed_field(name='Size', value='{}'.format(task.profile['Size']), inline=False)
            # embed.add_embed_field(name='Add to wallet', value='[Click here to add it to wallet]({})'.format(walletURL), inline=False)

            embed.set_footer(text=f"SourceRaffles [Courir - Instore]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
    except Exception as error:
        pass


def NotifyEndRaffleEntries(module, tasksNumber, failedTasks, successTasks, profileName, logsFile, raffle):
        
    webhookURL = Configuration().getConfiguration()['WebhookURL']

    try:
        if (webhookURL):
            webhook = DiscordWebhook(
                url=webhookURL,
                username=f'SourceRaffles [{module["name"]}] - Raffle Entries',
                avatar_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936'
            )

            embed = DiscordEmbed(
                timestamp="now",
                color=7484927,
                title="Resume for your tasks is available!"
            )

            embed.set_thumbnail(
                url=module['logo']
            )

            embed.set_author(
                name="Raffles Entries is completed!",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Product', value='[{}]({})'.format(raffle['product']['name'], raffle['url']), inline=False)
            embed.add_embed_field(name='Tasks Amount', value='{} tasks'.format(tasksNumber), inline=False)
            embed.add_embed_field(name='Profile', value=profileName, inline=False)
            embed.add_embed_field(name='Logs File', value=logsFile, inline=False)
            embed.add_embed_field(name='Resume', value=f"{successTasks} success • {failedTasks} failed | {tasksNumber} tasks", inline=False)

            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
            
    except Exception as error:
        pass
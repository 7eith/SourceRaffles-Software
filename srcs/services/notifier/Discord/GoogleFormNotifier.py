"""********************************************************************"""
"""                                                                    """
"""   [Discord] GoogleFormNotifier.py                                  """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 27/09/2021 11:27:12                                     """
"""   Updated: 04/11/2021 12:28:42                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""


from discord_webhook import DiscordWebhook, DiscordEmbed
from core.configuration import Configuration
from user import User

def NotifyEnteredGoogleForm(module, task, raffle):

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
                url=module['logo']
            )

            embed.set_author(
                name="Successfull entry" if task.success else "Failed entry",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Form', value='[{}]({})'.format(raffle['title'], raffle['url']), inline=False)

            if ("email" in task.profile):
                embed.add_embed_field(name='Email', value='||{}||'.format(task.profile['email']), inline=False)

            for key, value in task.profile.items():
                if (key != "status" and key != "email"):
                    embed.add_embed_field(name=key, value='{}'.format(value), inline=False)

            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
    except Exception as error:
        pass

def NotifyEndFillGoogleForm(module, tasksNumber, failedTasks, successTasks, logsFile, raffle):
        
    webhookURL = Configuration().getConfiguration()['WebhookURL']

    try:
        if (webhookURL):
            webhook = DiscordWebhook(
                url=webhookURL,
                username=f'SourceRaffles [{module["name"]}]',
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
                name="Form Entries is completed!",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Form', value='[{}]({})'.format(raffle['title'], raffle['url']), inline=False)
            embed.add_embed_field(name='Tasks Amount', value='{} tasks'.format(tasksNumber), inline=False)
            embed.add_embed_field(name='Logs File', value=logsFile, inline=False)
            embed.add_embed_field(name='Resume', value=f"{successTasks} success • {failedTasks} failed | {tasksNumber} tasks", inline=False)

            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
            
    except Exception as error:
        pass

def NotifyScrappedGoogleForm(raffle):
        
    webhookURL = None
    return

    try:
        if (webhookURL):
            webhook = DiscordWebhook(
                url=webhookURL,
                username=f'SourceRaffles Tracker',
                avatar_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936'
            )

            embed = DiscordEmbed(
                timestamp="now",
                color=7484927,
                title="User scrapped a google form!"
            )

            embed.set_author(
                name="Scrapped GForm",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="Google Forms", inline=False)
            embed.add_embed_field(name='Form', value='[{}]({})'.format(raffle['title'], raffle['url']), inline=False)
            embed.add_embed_field(name='User', value='{}'.format(User().username), inline=False)

            embed.set_footer(text=f"SourceRaffles [Google Forms]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
            
    except Exception as error:
        pass

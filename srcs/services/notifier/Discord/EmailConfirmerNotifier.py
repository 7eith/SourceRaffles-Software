"""********************************************************************"""
"""                                                                    """
"""   [Discord] AccountCreateNotifier.py                               """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 02/08/2021 06:52:21                                     """
"""   Updated: 03/10/2021 09:25:06                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from discord_webhook import DiscordWebhook, DiscordEmbed
from core.configuration import Configuration

def NotifyEmailConfirmed(module, task):

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
                name="Successfully confirmed link !" if task.success else "Failed to confirm link !",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Email: ', value='||{}||'.format(task.profile['email']), inline=True)
            embed.add_embed_field(name='Password: ', value='||{}||'.format(task.profile['password']), inline=True)

            if (task.profile['status'] != "SUCCESS" and task.profile['status'] != "FAILED"):
                embed.add_embed_field(name='State: ', value='{}'.format(task.profile['status']), inline=True)

            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
    except Exception as error:
        pass

def NotifyEndEmailConfirmed(module, tasksNumber, failedTasks, successTasks, profileName, logsFile):
    
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
                name="Email confirmation ended!",
                url="https://sourceraffles.com",
                icon_url="https://github.com/SyneziaSoft/Public/blob/main/images/success.gif?raw=true",
            )

            embed.add_embed_field(name="Site", value="[{}]({})".format(module['name'], module['url']), inline=False)
            embed.add_embed_field(name='Tasks Amount', value='{} task(s)'.format(tasksNumber), inline=False)
            embed.add_embed_field(name='Profile:', value=profileName, inline=False)
            embed.add_embed_field(name='Logs File:', value=logsFile, inline=False)
            embed.add_embed_field(name='Task(s) Resume:', value=f"{successTasks}:{failedTasks} / {tasksNumber} | Success - Failed - Amount", inline=False)

            embed.set_footer(text=f"SourceRaffles [{module['name']}]", icon_url='https://media.discordapp.net/attachments/811499422524637204/825517297639882782/Frame_1.png?width=936&height=936')
            embed.set_timestamp()

            webhook.add_embed(embed)
            webhook.execute()
            
    except Exception as error:
        pass

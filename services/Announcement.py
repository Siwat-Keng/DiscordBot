import discord
from operator import methodcaller
from difflib import get_close_matches

class Announcement:

    def __init__(self, title, icon, dictionary):
        self.title = title
        self.icon = icon
        self.dictionary = { int(uid): name for uid, name in dictionary.items() }

    async def announce(self, message):
        messages = [m.strip() for m in message.clean_content.split('\n') if m.strip()]
        spec_index = [idx for idx, msg in enumerate(messages) if '|' in msg]
        spec_msg = list(map(methodcaller('split', '|'), list(filter(lambda msg: '|' in msg, messages))))
        temp_dict = { msg[0]:msg[1] for msg in spec_msg }
        if spec_msg:
            template = ['\n'.join(messages[:spec_index[0]]), 
                '', 
                '\n'.join(messages[spec_index[len(spec_index)-1]+1:])]
        else:
            template = [ '\n'.join(messages), '', '' ]

        for member in message.mentions:
            hasSpecMsg = get_close_matches(self.dictionary[member.id], temp_dict.keys(), 1)
            if hasSpecMsg:
                template[1] = temp_dict[hasSpecMsg[0]]
                embed = discord.Embed(title=self.title,
                description = '\n'.join(template), color=0x00ff00)
                embed.set_footer(text='From '+message.author.name, icon_url=self.icon)
                await member.send(embed=embed)
            else:
                template[1] = ''
                embed = discord.Embed(title=self.title,
                description = '\n'.join(list(filter(lambda msg: msg.strip(), template))), 
                color=0x00ff00)
                embed.set_footer(text='From '+message.author.name, icon_url=self.icon)
                await member.send(embed=embed)
        
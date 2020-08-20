from services.MemberManager import MemberManager

async def handle_intro(message, client, data_collector, guilds):
    if guilds[message.guild.id].members.isIntro(message):
        guilds[message.guild.id].members.collectData(message)
        embed = guilds[message.guild.id].members.getEmbedded(client, message.author)
        if data_collector[message.guild.id]['roles']['waitingIntro'] and\
            data_collector[message.guild.id]['roles']['checkedIntro']:
            waitingIntro = message.guild.get_role(\
                data_collector[message.guild.id]['roles']['waitingIntro'])
            checkedIntro = message.guild.get_role(\
                data_collector[message.guild.id]['roles']['checkedIntro'])
            await message.author.add_roles(checkedIntro)
            await message.author.remove_roles(waitingIntro)
        await message.author.send(embed=embed)
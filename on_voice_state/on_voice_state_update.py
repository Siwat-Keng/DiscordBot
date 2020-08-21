from asyncio import sleep

def set_on_voice_state_update(client, data_collector, guilds):

    @client.event
    async def on_voice_state_update(member, before, after):
        if (not data_collector[member.guild.id]['roles']['checkedIntro']) or \
            (not data_collector[member.guild.id]['channels']['general']):
            return
        if member.id in guilds[member.guild.id].voice_state:
            guilds[member.guild.id].voice_state[member.id] += 1
        else:
            guilds[member.guild.id].voice_state[member.id] = 1

        if guilds[member.guild.id].voice_state[member.id] == 6:
            await member.remove_roles(member.guild.get_role(data_collector\
                [member.guild.id]['roles']['checkedIntro']))
            channel = member.guild.get_channel(data_collector[member.guild.id]\
                ['channels']['general'])
            await channel.send('อย่า Spam สิ {}'.format(member.mention), 
            delete_after=60)
            await sleep(3)
            await member.add_roles(member.guild.get_role(data_collector\
                [member.guild.id]['roles']['checkedIntro']))
            guilds[member.guild.id].voice_state[member.id] = 0
        else:
            await sleep(3)
            guilds[member.guild.id].voice_state[member.id] = 0
        
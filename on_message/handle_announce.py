async def handle_announce(message, data_collector, guilds):
    if (set(message.author.roles).intersection(\
        set(data_collector[message.guild.id]['roles']['admins']))) and \
            message.mentions:
            await guilds[message.guild.id].announcement.announce(message)
            await message.add_reaction('✅')
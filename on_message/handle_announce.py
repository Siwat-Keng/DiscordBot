async def handle_announce(message, data_collector, guilds):
    roles_id = {role.id for role in message.author.roles}
    if (roles_id.intersection(data_collector[message.guild.id]\
        ['roles']['admins'])) and (message.mentions or message.mention_everyone):
            await guilds[message.guild.id].announcement.announce(message)
            await message.add_reaction('✅')
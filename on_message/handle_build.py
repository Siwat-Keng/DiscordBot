async def handle_build(message, data_collector, builds):
    target = message.content[len('{}build'.format(data_collector\
        [message.guild.id]['prefix'])):].strip()
    for embed in builds.getBuild(target, data_collector[message.guild.id]['icon'], 
    data_collector[message.guild.id]['footer']):
        await message.channel.send(embed=embed, delete_after=300)
async def handle_build(message, data_collector, builds):
    target = message.content[len('{}build'.format(data_collector\
        [message.guild.id]['prefix'])):].strip()
    for embed in data_collector[message.guild.id]['build'].getBuild(target):
        await message.channel.send(embed=embed, delete_after=300)
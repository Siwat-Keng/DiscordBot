async def handle_drop(message, data_collector, items):
    embed = items.getDropInfo(message.content[len('{}drop'\
        .format(data_collector[message.guild.id]['prefix'])):].strip().lower())
    embed.set_footer(text=data_collector[message.guild.id]['footer'], 
    icon_url=data_collector[message.guild.id]['icon'])                    
    await message.channel.send(embed=embed)
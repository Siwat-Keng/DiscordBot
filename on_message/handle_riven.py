from services.LiveSearch import LiveSearch, InvalidSearch
from re import compile

async def handle_riven(client, message, data_collector, items, riven_caches):
    target = message.content[len('{}riven'.format(data_collector[message.guild.id]\
        ['prefix'])):].strip()
    searchMessage = await message.channel.send('```Loading...```')
    try:
        riven_caches[searchMessage.id] = LiveSearch(client, searchMessage, 
        target, data_collector[message.guild.id]['footer'], 
        data_collector[message.guild.id]['icon'], 
        list(items.weapons.keys()), message.author)
        await message.add_reaction('✅')
    except InvalidSearch:
        try:
            regex = compile('^[^+-]+')
            target = regex.search(target).group().strip()
            embed = await items.getRivenPrice(target.lower())
            embed.set_footer(text=data_collector[message.guild.id]['footer'], 
            icon_url=data_collector[message.guild.id]['icon']) 
            await searchMessage.clear_reactions()
            await searchMessage.edit(content=None, embed=embed, delete_after=300) 
            await message.add_reaction('✅')
        except:
            await searchMessage.delete()
            await message.add_reaction('❌')
            return
    except:
        await searchMessage.delete()
        await message.add_reaction('❌')
        return
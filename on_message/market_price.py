from services.Container import MarketContainer, MarketRankContainer

async def market_price(data_collector, items, market_caches, message):
    buyMessage = await message.channel.send('```Loading...```', delete_after=300)
    sellMessage = await message.channel.send('```Loading...```', delete_after=300)
    try:
        itemName = items.toName(message.content[len('{}price'\
            .format(data_collector[message.guild.id]['prefix'])):].strip().lower())
    except KeyError:
        await buyMessage.delete()
        await sellMessage.delete()
        await message.add_reaction("❌")
        return
    market = await items.getPrice(itemName)
    if market['hasRank']:
        market_caches[buyMessage.id] = \
            MarketRankContainer(market, 'sell', buyMessage, items, data_collector[message.guild.id]['icon'])
        market_caches[sellMessage.id] = \
            MarketRankContainer(market, 'buy', sellMessage, items, data_collector[message.guild.id]['icon'])
    else:
        market_caches[buyMessage.id] = MarketContainer(market, 'sell', buyMessage, items,
        data_collector[message.guild.id]['icon'], data_collector[message.guild.id]['footer'])
        market_caches[sellMessage.id] = MarketContainer(market, 'buy', sellMessage, items, 
        data_collector[message.guild.id]['icon'], data_collector[message.guild.id]['footer'])             
    await market_caches[buyMessage.id].setMessage()
    await market_caches[sellMessage.id].setMessage()    
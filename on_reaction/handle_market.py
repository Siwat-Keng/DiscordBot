from services.Container import MarketContainer, MarketRankContainer

async def handle_market(reaction, user, market_caches):
    if reaction.emoji == u"\u25C0":
        if isinstance(market_caches[reaction.message.id], MarketRankContainer):
            await market_caches[reaction.message.id].prevPage()
        elif isinstance(market_caches[reaction.message.id], MarketContainer):
            await market_caches[reaction.message.id].prevPage()                                   
            
    elif reaction.emoji == u"\u25B6":
        if isinstance(market_caches[reaction.message.id], MarketRankContainer):
            await market_caches[reaction.message.id].nextPage()
        elif isinstance(market_caches[reaction.message.id], MarketContainer):
            await market_caches[reaction.message.id].nextPage()                      

    elif reaction.emoji == "🚩":
        if isinstance(market_caches[reaction.message.id], MarketContainer) \
            or isinstance(market_caches[reaction.message.id], MarketRankContainer):
            await market_caches[reaction.message.id].refresh()
    
    elif reaction.emoji == "➕":
        if isinstance(market_caches[reaction.message.id], MarketRankContainer):
            await market_caches[reaction.message.id].increaseRank()

    elif reaction.emoji == "➖":          
        if isinstance(market_caches[reaction.message.id], MarketRankContainer):                                                                   
            await market_caches[reaction.message.id].decreaseRank()
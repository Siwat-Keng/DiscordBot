from discord.errors import NotFound
from services.Container import PartyContainer, MarketRankContainer, MarketContainer, \
    FissureContainer, AllianceCollector
from services.LiveSearch import LiveSearch

def set_on_reaction_add(bot):
    
    @bot.client.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        try:
            if reaction.message.id in bot.data['message_caches']:
                if reaction.emoji == u"\u25C0":
                    if isinstance(bot.data['message_caches'][reaction.message.id], MarketRankContainer):
                        await bot.data['message_caches'][reaction.message.id].prevPage()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], MarketContainer):
                        await bot.data['message_caches'][reaction.message.id].prevPage()                        
                    elif isinstance(bot.data['message_caches'][reaction.message.id], AllianceCollector):
                        await bot.data['message_caches'][reaction.message.id].prevPage()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], LiveSearch):
                        await bot.data['message_caches'][reaction.message.id].container.prev()                        
                        
                elif reaction.emoji == u"\u25B6":
                    if isinstance(bot.data['message_caches'][reaction.message.id], MarketRankContainer):
                        await bot.data['message_caches'][reaction.message.id].nextPage()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], MarketContainer):
                        await bot.data['message_caches'][reaction.message.id].nextPage()                        
                    elif isinstance(bot.data['message_caches'][reaction.message.id], AllianceCollector):
                        await bot.data['message_caches'][reaction.message.id].nextPage()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], LiveSearch):
                        await bot.data['message_caches'][reaction.message.id].container.next()                        

                elif reaction.emoji == "👍":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].add_member(user)

                elif reaction.emoji == "👎":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        if not await bot.data['message_caches'][reaction.message.id].remove_member(user):
                            del bot.data['message_caches'][reaction.message.id]                          

                elif reaction.emoji == "📃":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].getMemberProfile(bot.data['members'])                      

                elif reaction.emoji == "🚩":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer) and user == bot.data['message_caches'][reaction.message.id].leader:
                        bot.data['message_caches'][await bot.data['message_caches'][reaction.message.id].refresh()] = bot.data['message_caches'][reaction.message.id]
                    elif isinstance(bot.data['message_caches'][reaction.message.id], MarketContainer) or isinstance(bot.data['message_caches'][reaction.message.id], MarketRankContainer):
                        await bot.data['message_caches'][reaction.message.id].refresh()
                
                elif reaction.emoji == "🇱":
                    if isinstance(bot.data['message_caches'][reaction.message.id], FissureContainer):
                        await bot.data['message_caches'][reaction.message.id].setLith()
                elif reaction.emoji == "🇲":
                    if isinstance(bot.data['message_caches'][reaction.message.id], FissureContainer):
                        await bot.data['message_caches'][reaction.message.id].setMeso()

                elif reaction.emoji == "🇳":
                    if isinstance(bot.data['message_caches'][reaction.message.id], FissureContainer):
                        await bot.data['message_caches'][reaction.message.id].setNeo()

                elif reaction.emoji == "🇦":
                    if isinstance(bot.data['message_caches'][reaction.message.id], FissureContainer):
                        await bot.data['message_caches'][reaction.message.id].setAxi()

                elif reaction.emoji == "🇷":    
                    if isinstance(bot.data['message_caches'][reaction.message.id], FissureContainer):
                        await bot.data['message_caches'][reaction.message.id].setReq()  

                elif reaction.emoji == "❌":    
                    if isinstance(bot.data['message_caches'][reaction.message.id], LiveSearch) and user == bot.data['message_caches'][reaction.message.id].owner:
                        bot.data['message_caches'][reaction.message.id].searching = False
                        await reaction.message.delete()     

                elif reaction.emoji == "➕":
                    if isinstance(bot.data['message_caches'][reaction.message.id], MarketRankContainer):
                        await bot.data['message_caches'][reaction.message.id].increaseRank()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].increaseSize()

                elif reaction.emoji == "➖":          
                    if isinstance(bot.data['message_caches'][reaction.message.id], MarketRankContainer):                                                                   
                        await bot.data['message_caches'][reaction.message.id].decreaseRank()
                    elif isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].decreaseSize() 
                        
        except Exception as err:
            print('Error on reaction : {}'.format(err))

        finally:
            try:
                if reaction.message.id in bot.data['message_caches']:
                    await reaction.remove(user)
            except NotFound:
                pass
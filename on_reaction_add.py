import discord
from externalModules.Container import PartyContainer

def set_on_reaction_add(bot):
    
    @bot.client.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        try:
            if reaction.message.id in bot.data['message_caches']:
                if reaction.emoji == u"\u25C0":
                    channel = bot.client.get_channel(int(bot.data['channels']['botcommands']))
                    message = await channel.fetch_message(reaction.message.id)                
                    if bot.data['message_caches'][reaction.message.id]["currentRank"] > 0:
                        bot.data['message_caches'][reaction.message.id]["currentRank"] -= 1
                        if bot.data['message_caches'][reaction.message.id]["type"] == "buy": 
                            embed = discord.Embed(title=bot.data['message_caches'][reaction.message.id]["market"]['itemName']+" Buyers", url = bot.data['message_caches'][reaction.message.id]["market"]['url'], color=0x00ff00)
                            for i in range(len(bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]])):
                                if i >= 5:
                                    break
                                embed.add_field(name= str(bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i]), value=bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i].getBuyMessage(), inline=False)
                            embed.set_footer(text='Item Rank : '+str(bot.data['message_caches'][reaction.message.id]["currentRank"]), icon_url=bot.data['icon']) 
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=bot.data['message_caches'][reaction.message.id]["market"]['itemName']+" Sellers", url = bot.data['message_caches'][reaction.message.id]["market"]['url'], color=0x00ff00)
                            for i in range(len(bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]])):
                                if i >= 5:
                                    break
                                embed.add_field(name= str(bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i]), value=bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i].getSellMessage(), inline=False)
                            embed.set_footer(text='Item Rank : '+str(bot.data['message_caches'][reaction.message.id]["currentRank"]), icon_url=bot.data['icon']) 
                            await message.edit(embed=embed)    
                        
                elif reaction.emoji == u"\u25B6":
                    channel = bot.client.get_channel(int(bot.data['channels']['botcommands']))
                    message = await channel.fetch_message(reaction.message.id)                 
                    if bot.data['message_caches'][reaction.message.id]["currentRank"] < bot.data['message_caches'][reaction.message.id]["market"]['maxRank']:
                        bot.data['message_caches'][reaction.message.id]["currentRank"] += 1
                        if bot.data['message_caches'][reaction.message.id]["type"] == "buy": 
                            embed = discord.Embed(title=bot.data['message_caches'][reaction.message.id]["market"]['itemName']+" Buyers", url = bot.data['message_caches'][reaction.message.id]["market"]['url'], color=0x00ff00)
                            for i in range(len(bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]])):
                                if i >= 5:
                                    break
                                embed.add_field(name= str(bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i]), value=bot.data['message_caches'][reaction.message.id]["market"]['buy'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i].getBuyMessage(), inline=False)
                            embed.set_footer(text='Item Rank : '+str(bot.data['message_caches'][reaction.message.id]["currentRank"]), icon_url=bot.data['icon']) 
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=bot.data['message_caches'][reaction.message.id]["market"]['itemName']+" Sellers", url = bot.data['message_caches'][reaction.message.id]["market"]['url'], color=0x00ff00)
                            for i in range(len(bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]])):
                                if i >= 5:
                                    break
                                embed.add_field(name= str(bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i]), value=bot.data['message_caches'][reaction.message.id]["market"]['sell'][bot.data['message_caches'][reaction.message.id]["currentRank"]][i].getSellMessage(), inline=False)
                            embed.set_footer(text='Item Rank : '+str(bot.data['message_caches'][reaction.message.id]["currentRank"]), icon_url=bot.data['icon']) 
                            await message.edit(embed=embed)  

                elif reaction.emoji == "👍":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].add_member(user)

                elif reaction.emoji == "👎":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        if not await bot.data['message_caches'][reaction.message.id].remove_member(user):
                            del bot.data['message_caches'][reaction.message.id]

                elif reaction.emoji == "1️⃣":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].getMemberProfile(bot.data['members'], 1)

                elif reaction.emoji == "2️⃣":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].getMemberProfile(bot.data['members'], 2)                    

                elif reaction.emoji == "3️⃣":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].getMemberProfile(bot.data['members'], 3)                 

                elif reaction.emoji == "4️⃣":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer):
                        await bot.data['message_caches'][reaction.message.id].getMemberProfile(bot.data['members'], 4)                  


                elif reaction.emoji == "🚩":
                    if isinstance(bot.data['message_caches'][reaction.message.id], PartyContainer) and user == bot.data['message_caches'][reaction.message.id].leader:
                        bot.data['message_caches'][await bot.data['message_caches'][reaction.message.id].refresh()] = bot.data['message_caches'][reaction.message.id]
                        del bot.data['message_caches'][reaction.message.id]

        except Exception as err:
            print('Error on reaction : {}'.format(err))

        finally:
            try:
                if reaction.message.id in bot.data['message_caches']:
                    await reaction.remove(user)
            except discord.errors.NotFound:
                pass
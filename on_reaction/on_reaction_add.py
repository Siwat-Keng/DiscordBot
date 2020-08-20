from discord import NotFound
from on_reaction.handle_market import handle_market
from on_reaction.handle_fissure import handle_fissure
from on_reaction.handle_party import handle_party
from on_reaction.handle_riven import handle_riven

def set_on_reaction_add(client, conn, data_collector, market_caches, 
fissure_caches, party_caches, riven_caches, guilds, TABLE_NAME):

    @client.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        try:
            if reaction.message.id in market_caches:
                await handle_market(reaction, user, market_caches)
            elif reaction.message.id in fissure_caches:
                await handle_fissure(reaction, user, fissure_caches)
            elif reaction.message.id in party_caches:
                await handle_party(reaction, user, guilds, party_caches)
            elif reaction.message.id in riven_caches:
                await handle_riven(reaction, user, guilds, riven_caches)                

        except Exception as err:
            print('Error on reaction : {}'.format(err))

        finally:
            try:
                if reaction.message.id in market_caches or reaction.message.id in fissure_caches or\
                    reaction.message.id in party_caches or reaction.message.id in riven_caches:
                    await reaction.remove(user)
            except NotFound:
                pass
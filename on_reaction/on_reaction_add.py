from discord import NotFound
from on_reaction.handle_market import handle_market

def set_on_reaction_add(client, conn, data_collector, market_caches, TABLE_NAME):

    @client.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return
        try:
            if reaction.message.id in market_caches:
                await handle_market(reaction, user, market_caches)
                        
        except Exception as err:
            print('Error on reaction : {}'.format(err))

        finally:
            try:
                if reaction.message.id in market_caches:
                    await reaction.remove(user)
            except NotFound:
                pass
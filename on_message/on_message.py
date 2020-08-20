from on_message.set_channel import set_channel
from on_message.set_prefix import set_prefix
from on_message.market_price import market_price

# from discord import File
from discord.channel import DMChannel
# from io import StringIO

def set_on_message(client, conn, data_collector, items, market_caches, TABLE_NAME):

    @client.event
    async def on_message(message):
        if message.author.bot or isinstance(message.channel, DMChannel):
            return

        elif message.content == '{}printfile'.format(data_collector[message.guild.id]['prefix']):
            async with conn.cursor() as cursor:
                sql = 'SELECT * FROM {} WHERE serverID = %s'.format(TABLE_NAME)
                val = (message.guild.id,)
                await cursor.execute(sql, val)
                print(await cursor.fetchone())
                
        # elif message.content == '{}savefile'.format(data_collector[message.guild.id]['prefix']):
        #     async with conn.cursor() as cursor:
        #         sql = 'SELECT * FROM {} WHERE serverID = %s'.format(TABLE_NAME)
        #         val = (message.guild.id,)
        #         await cursor.execute(sql, val)
        #         fetched = await cursor.fetchone()
        #         await cursor.close()
        #         if fetched:
        #             fetched = StringIO(fetched[1])
        #             file = File(fp=fetched, filename='backup.json')
        #             await message.channel.send(content=None, file=file)                
        
        elif message.content.startswith('{}set_prefix'.format(data_collector[message.guild.id]['prefix'])):
            await set_prefix(conn, data_collector, message, TABLE_NAME)
        
        elif message.content.startswith('{}set_ch'.format(data_collector[message.guild.id]['prefix'])):
            await set_channel(conn, data_collector, message, TABLE_NAME)

        elif message.channel.id != data_collector[message.guild.id]['channels']['botcommands']:
            return

        elif message.content.startswith('{}price'.format(data_collector[message.guild.id]['prefix'])):
            await market_price(data_collector, items, market_caches, message)

        await message.add_reaction("✅")
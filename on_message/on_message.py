from on_message.set_channel import set_channel
from on_message.set_prefix import set_prefix
from on_message.set_footer import set_footer
from on_message.set_icon import set_icon
from on_message.market_price import market_price
from on_message.set_clan import add_clan, remove_clan
from on_message.set_role import set_vip, add_admin, remove_admin
from on_message.share_ch import handle_share


# from discord import File
from discord import Forbidden
from discord.channel import DMChannel
# from io import StringIO

def set_on_message(client, conn, data_collector, guilds, items, market_caches, TABLE_NAME):

    @client.event
    async def on_message(message):
        if message.author.bot or isinstance(message.channel, DMChannel):
            return

        # elif message.content == '{}printfile'.format(data_collector[message.guild.id]['prefix']):
        #     async with conn.cursor() as cursor:
        #         sql = 'SELECT * FROM {} WHERE serverID = %s'.format(TABLE_NAME)
        #         val = (message.guild.id,)
        #         await cursor.execute(sql, val)
        #         print(await cursor.fetchone())

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
            await set_channel(client, conn, data_collector, guilds, message, TABLE_NAME)

        elif message.content.startswith('{}set_footer'.format(data_collector[message.guild.id]['prefix'])):
            await set_footer(conn, data_collector, message, TABLE_NAME)

        elif message.content.startswith('{}set_icon'.format(data_collector[message.guild.id]['prefix'])):
            await set_icon(conn, data_collector, message, TABLE_NAME)          

        elif message.content.startswith('{}add_clan'.format(data_collector[message.guild.id]['prefix'])):
            await add_clan(conn, data_collector, message, TABLE_NAME)

        elif message.content.startswith('{}remove_clan'.format(data_collector[message.guild.id]['prefix'])):
            await remove_clan(conn, data_collector, message, TABLE_NAME)

        elif message.content.startswith('{}set_vip'.format(data_collector[message.guild.id]['prefix'])):
            await set_vip(conn, data_collector, message, TABLE_NAME)

        elif message.content.startswith('{}add_admin'.format(data_collector[message.guild.id]['prefix'])):
            await add_admin(conn, data_collector, message, TABLE_NAME)

        elif message.content.startswith('{}remove_admin'.format(data_collector[message.guild.id]['prefix'])):
            await remove_admin(conn, data_collector, message, TABLE_NAME)

        elif message.channel in guilds[message.guild.id].share:
            await handle_share(client, conn, message, data_collector, guilds, TABLE_NAME)
            return

        elif message.channel.id != data_collector[message.guild.id]['channels']['botcommands']:
            return

        elif message.content.startswith('{}price'.format(data_collector[message.guild.id]['prefix'])):
            await market_price(data_collector, items, market_caches, message)

        await message.add_reaction("✅")
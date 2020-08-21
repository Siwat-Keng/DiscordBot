from discord import Forbidden
from discord.channel import DMChannel
from on_message.set_channel import set_channel
from on_message.set_prefix import set_prefix
from on_message.set_footer import set_footer
from on_message.set_icon import set_icon
from on_message.set_clan import add_clan, remove_clan
from on_message.set_role import set_vip, add_admin, remove_admin
from on_message.handle_share import handle_share
from on_message.handle_intro import handle_intro
from on_message.handle_price import handle_price
from on_message.handle_announce import handle_announce
from on_message.handle_build import handle_build
from on_message.handle_drop import handle_drop
from on_message.handle_fissure import handle_fissure
from on_message.handle_party import handle_party
from on_message.handle_riven import handle_riven

def set_on_message(client, conn, data_collector, guilds, items, market_caches, 
builds, world_stat, fissure_caches, party_caches, riven_caches, TABLE_NAME):

    @client.event
    async def on_message(message):
        try:
            if message.author.bot or isinstance(message.channel, DMChannel):
                return

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

            elif message.channel.id == data_collector[message.guild.id]['channels']['intro']:
                await handle_intro(message, client, data_collector, guilds)

            elif message.channel in guilds[message.guild.id].share:
                await handle_share(client, conn, message, data_collector, guilds, TABLE_NAME)
                return

            elif message.channel.id == data_collector[message.guild.id]['channels']['clan']:
                await handle_announce(message, data_collector, guilds)

            elif message.channel.id != data_collector[message.guild.id]['channels']['botcommands']:
                return

            elif message.content.startswith('{}price'.format(data_collector[message.guild.id]['prefix'])):
                await handle_price(data_collector, items, market_caches, message)

            elif message.content.startswith('{}build'.format(data_collector[message.guild.id]['prefix'])):
                await handle_build(message, data_collector, builds)

            elif message.content.startswith('{}drop'.format(data_collector[message.guild.id]['prefix'])):
                await handle_drop(message, data_collector, items)

            elif message.content.startswith('{}fissure'.format(data_collector[message.guild.id]['prefix'])):
                await handle_fissure(message, data_collector, world_stat, fissure_caches)

            elif message.content.startswith('{}party'.format(data_collector[message.guild.id]['prefix'])):
                await handle_party(client, message, data_collector, party_caches)

            elif message.content.startswith('{}riven'.format(data_collector[message.guild.id]['prefix'])):
                await handle_riven(client, message, data_collector, items, riven_caches)
        except Exception as err:
            print(err)
            await message.add_reaction('❌')
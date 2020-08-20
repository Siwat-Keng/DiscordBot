from aiomysql import connect
from discord import Client
from asyncio import get_event_loop
from dotenv import load_dotenv
from os import getenv
from services.WorldStat import WorldStat
from services.Items import Items
from on_message.on_message import set_on_message
from on_guild.on_guild_join import set_on_guild_join
from on_guild.on_guild_remove import set_on_guild_remove
from on_ready.on_ready import set_on_ready
from on_reaction.on_reaction_add import set_on_reaction_add


load_dotenv()

DATABASE_NAME = getenv('DB_DATABASE')
TABLE_NAME = getenv('DB_TABLE')
HOST = getenv('DB_HOST')
USER = getenv('DB_USERNAME')
PASSWORD = getenv('DB_PASSWORD')
PORT = int(getenv('DB_PORT'))

TOKEN = getenv('TOKEN')

async def init(loop):
    conn = await connect(host=HOST, port=PORT,
    user=USER, password=PASSWORD,
    db=DATABASE_NAME, loop=loop
    )
    client = Client()
    data_collector = {}
    guilds = {}
    world_stat = WorldStat(client)
    items = Items(client)
    market_caches = {}
            
    set_on_guild_join(client, conn, data_collector, TABLE_NAME)
    set_on_guild_remove(client, conn, data_collector, TABLE_NAME)
    set_on_message(client, conn, data_collector, items, market_caches, TABLE_NAME)
    set_on_ready(client, conn, guilds, data_collector, world_stat, TABLE_NAME)
    set_on_reaction_add(client, conn, data_collector, market_caches, TABLE_NAME)

    return client

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(init(loop)).run(TOKEN)
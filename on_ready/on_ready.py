from json import loads
from services.Guild import Guild

def set_on_ready(client, conn, guilds, data_collector, world_stat, TABLE_NAME):

    @client.event
    async def on_ready():
        async with conn.cursor() as cursor:
            sql = 'SELECT * FROM discord'
            await cursor.execute(sql)
            fetched = await cursor.fetchall()
            for data in fetched:
                data_collector[int(data[0])] = loads(data[1])
                guilds[int(data[0])] = Guild(client, client.get_guild(int(data[0])), 
                data_collector, world_stat, conn, TABLE_NAME)
            print('ready!')
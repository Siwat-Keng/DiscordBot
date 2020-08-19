from json import loads

def set_on_ready(client, conn, data_collector, TABLE_NAME):

    @client.event
    async def on_ready():
        async with conn.cursor() as cursor:
            sql = 'SELECT * FROM discord'
            await cursor.execute(sql)
            fetched = await cursor.fetchall()
            for data in fetched:
                data_collector[int(data[0])] = loads(data[1])
            print('ready!')
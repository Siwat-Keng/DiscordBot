from json import dumps

def set_on_guild_remove(client, conn, data_collector, TABLE_NAME):
    
    @client.event
    async def on_guild_remove(guild):
        del data_collector[guild.id]
        async with conn.cursor() as cursor:
            sql = 'DELETE FROM {} WHERE serverID = %s'.format(TABLE_NAME)
            val = (guild.id,)
            await cursor.execute(sql, val)                   
            await conn.commit()
            await cursor.close()
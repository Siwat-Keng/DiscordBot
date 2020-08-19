from json import dumps

async def set_prefix(conn, data_collector, message, TABLE_NAME):
    new_prefix = message.content[len('{}set_prefix'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['prefix'] = new_prefix
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)                   
        await conn.commit()
        await cursor.close()
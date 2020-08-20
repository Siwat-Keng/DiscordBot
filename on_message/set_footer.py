from json import dumps
from discord import Forbidden

async def set_footer(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    new_footer = message.content[len('{}set_footer'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['footer'] = new_footer
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)
        await conn.commit()
        await cursor.close()
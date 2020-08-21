from json import dumps
from discord import Forbidden

async def set_icon(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    new_icon = message.content[len('{}set_icon'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['icon'] = new_icon
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')
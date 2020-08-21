from json import dumps
from discord import Forbidden

async def add_clan(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden
    target = [m.strip() for m in message.content[len('{}add_clan'\
        .format(data_collector[message.guild.id]['prefix'])):].split('|')]
    data_collector[message.guild.id]['clan'][int(target[0])] = target[1]
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')

async def remove_clan(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden
    target = message.content[len('{}remove_clan'\
        .format(data_collector[message.guild.id]['prefix'])):]
    data_collector[message.guild.id]['clan'].pop(int(target))
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')
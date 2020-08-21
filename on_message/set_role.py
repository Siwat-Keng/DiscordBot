from json import dumps
from discord import Forbidden

async def set_vip(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    new_vip = message.content[len('{}set_vip'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['roles']['vip'] = int(new_vip)
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')

async def add_admin(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    new_admin = message.content[len('{}add_admin'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['roles']['admins'].append(int(new_admin))
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)                   
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')

async def remove_admin(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    rm_admin = message.content[len('{}remove_admin'.format(data_collector[message.guild.id]['prefix'])):].strip()
    data_collector[message.guild.id]['roles']['admins'].remove(int(rm_admin))
    async with conn.cursor() as cursor:
        sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
        val = (dumps(data_collector[message.guild.id]), message.guild.id)
        await cursor.execute(sql, val)                   
        await conn.commit()
        await cursor.close()
    await message.add_reaction('✅')
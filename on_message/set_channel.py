from json import dumps
from discord import Forbidden

async def set_channel(conn, data_collector, message, TABLE_NAME):
    if message.author != message.guild.owner:
        raise Forbidden

    elif message.content[len('{}set_ch'.format(data_collector[message.guild.id]['prefix'])):].strip()\
            in data_collector[message.guild.id]['channels'] and  message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip() != 'share':
        data_collector[message.guild.id]['channels'][message.content[len('{}set_ch'\
            .format(data_collector[message.guild.id]['prefix'])):].strip()] = message.channel.id
        async with conn.cursor() as cursor:
            sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
            val = (dumps(data_collector[message.guild.id]), message.guild.id)
            await cursor.execute(sql, val)                   
            await conn.commit()
            await cursor.close()
    elif message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip().startswith('share'):
                ch_id = message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip()[len('share'):]
                share = [message.channel.id, ch_id]
                data_collector[message.guild.id]['channels']['share'].append(share)
                async with conn.cursor() as cursor:
                    sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
                    val = (dumps(data_collector[message.guild.id]), message.guild.id)
                    await cursor.execute(sql, val)                   
                    await conn.commit()
                    await cursor.close()                
    else:
        #TODO show set channel commands
        pass
    
from json import dumps

async def set_channel(conn, data_collector, message, TABLE_NAME):
    if message.content[len('{}set_ch'.format(data_collector[message.guild.id]['prefix'])):].strip()\
            in data_collector[message.guild.id]['channels'] and  message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip() != 'share':
        data_collector[message.guild.id]['channels'][message.content[len('!set'):].strip()] = message.channel.id
        async with conn.cursor() as cursor:
            sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
            val = (dumps(data_collector[message.guild.id]), message.guild.id)
            await cursor.execute(sql, val)                   
            await conn.commit()
            await cursor.close()
    elif message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip() == 'share':
                #TODO set share channel
                pass
    else:
        #TODO send all channels
        pass
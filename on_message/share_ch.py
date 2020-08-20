from json import dumps

async def handle_share(client, conn, message, data_collector, guilds, TABLE_NAME):
    files = []
    for att in message.attachments:
        files.append(await att.to_file())
    for channel in guilds[message.guild.id].share.get_share_room(message.channel):
        try:
            await channel.send(message.content, files=files)
        except:
            guilds[message.guild.id].share.update(client)
            data_collector[message.guild.id]['channels']['share'] = \
                [ rs for rs in data_collector[message.guild.id]['channels']['share'] \
                    if client.get_channel(rs[0]) and client.get_channel(rs[1])]
            async with conn.cursor() as cursor:
                sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
                val = (dumps(data_collector[message.guild.id]), message.guild.id)
                await cursor.execute(sql, val)                   
                await conn.commit()
                await cursor.close()
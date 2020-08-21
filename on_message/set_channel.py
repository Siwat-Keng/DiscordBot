from json import dumps
from discord import Embed, Forbidden

async def set_channel(client, conn, data_collector, guilds, message, TABLE_NAME):
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
        await message.add_reaction('✅')
    elif message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip().startswith('share'):
                ch_id = message.content[len('{}set_ch'\
                .format(data_collector[message.guild.id]['prefix'])):].strip()[len('share'):]
                target_ch = client.get_channel(int(ch_id))
                target_guild = target_ch.guild
                share = [message.channel.id, int(ch_id)]
                data_collector[target_guild.id]['channels']['share'].append(share)
                guilds[target_guild.id].share.refresh(client, 
                data_collector[target_guild.id]['channels']['share'])
                async with conn.cursor() as cursor:
                    sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
                    val = (dumps(data_collector[target_guild.id]), target_guild.id)
                    await cursor.execute(sql, val)                   
                    await conn.commit()
                    await cursor.close()         
                await message.add_reaction('✅')       
    else:
        embed = Embed(title='Channel Setting Commands', color=0x00ff00)
        embed.add_field(name= '{}set_ch alert'.format(data_collector[message.guild.id]['prefix']), 
        value='ทำให้ห้องที่ใช้คำสั่ง กลายเป็นห้องแสดงเวลาต่าง ๆ ในเกม(ข้อความก่อนหน้าจะถูกลบออก!!!)', inline=False)
        embed.add_field(name= '{}set_ch botcommands'.format(data_collector[message.guild.id]['prefix']), 
        value='ทำให้ห้องที่ใช้คำสั่ง ใช้ commands ทั่วไปของบอทได้', inline=False)
        embed.add_field(name= '{}set_ch intro'.format(data_collector[message.guild.id]['prefix']), 
        value='ทำให้ห้องที่ใช้คำสั่ง เป็นห้องสำหรับแนะนำตัว โดยบอทจะสร้าง role ใหม่ขึ้นมา 2 roles', inline=False)
        embed.add_field(name= '{}set_ch share <id>'.format(data_collector[message.guild.id]['prefix']), 
        value='ทำให้ห้องที่ใช้คำสั่ง รับข้อความจากห้องที่มี id ที่ระบุมา(บอทจะต้องอยู่ใน server ที่มีห้อง id นั้น ๆ)', inline=False)
        embed.set_footer(text=data_collector[message.guild.id]['footer'], icon_url=data_collector[message.guild.id]['icon'])
        await message.channel.send(embed=embed)
        await message.add_reaction('✅')
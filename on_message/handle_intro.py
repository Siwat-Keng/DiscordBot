from services.MemberManager import MemberManager
from datetime import datetime, timedelta
from discord import Embed

async def handle_intro(message, client, data_collector, guilds):
    if guilds[message.guild.id].members.isIntro(message):
        guilds[message.guild.id].members.collectData(message)
        embed = guilds[message.guild.id].members.getEmbedded(client, message.author)
        if data_collector[message.guild.id]['roles']['waitingIntro'] and\
            data_collector[message.guild.id]['roles']['checkedIntro']:
            waitingIntro = message.guild.get_role(\
                data_collector[message.guild.id]['roles']['waitingIntro'])
            checkedIntro = message.guild.get_role(\
                data_collector[message.guild.id]['roles']['checkedIntro'])
            await message.author.add_roles(checkedIntro)
            await message.author.remove_roles(waitingIntro)
        await message.add_reaction('✅')
        await message.author.send(embed=embed)
    else:
        await message.add_reaction("❌")
        embed = Embed(title="Hello {}".format(message.author.name), 
        description = 'แนะนำตัวใหม่ในห้อง welcome_room ภายใน {} นาที ตามรูปแบบที่กำหนดนะครับ'\
            .format((message.author.joined_at-datetime.now()+timedelta(minutes=30)).seconds//60), 
        url = data_collector[message.guild.id]['url'], color=0x00ff00)
        embed.add_field(name='ถ้าไม่ต้องการใส่อายุ หรือ Clan สามารถใส่เป็น - ได้', 
        value="""```ชื่อ :\nอายุ :\nIGN(ชื่อในเกม) :\nCLAN :```""", inline=False)
        embed.set_image(url='https://cdn.discordapp.com/attachments/468032916270743564/672090545555898388/Capture.JPG')
        embed.set_footer(text='ปล. ในDiscord[PC] สามารถขึ้นบรรทัดใหม่ด้วยการกดปุ่ม Shift ค้าง + ปุ่ม Enter(จำเป็นต้องขึ้นบรรทัดใหม่)', 
        icon_url=data_collector[message.guild.id]['icon']) 
        await message.author.send(embed=embed)
        await message.delete(delay=60)
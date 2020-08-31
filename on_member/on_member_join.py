from discord import Embed

def set_on_member_join(client, data_collector):

    @client.event
    async def on_member_join(member):
        if data_collector[member.guild.id]['channels']['intro'] and\
            data_collector[member.guild.id]['roles']['waitingIntro'] and\
                data_collector[member.guild.id]['roles']['checkedIntro'] and\
                    data_collector[member.guild.id]['roles']['VIP']:
                intro_channel = client.get_channel(data_collector\
                    [member.guild.id]['channels']['intro'])
                role = intro_channel.guild.get_role(data_collector\
                    [member.guild.id]['roles']['waitingIntro'])
                await member.add_roles(role)
                embed = Embed(title='Welcome {}'.format(member.display_name), 
                description = 'อย่าลืมแนะนำตัวในห้อง {} ภายใน 30 นาที ตามตัวอย่างในรูปนะครับ \
                    แล้วห้องต่าง ๆ จะปรากฏขึ้น'
                .format(intro_channel.name), 
                url =data_collector[member.guild.id]['url'], color=0x00ff00)
                embed.add_field(name='สามารถ Copy ไปเติมได้', 
                value='```ชื่อ :\nอายุ :\nIGN(ชื่อในเกม) :\nCLAN :```', inline=False)
                embed.set_footer(text='ปล. ในDiscord[PC] สามารถขึ้นบรรทัดใหม่ด้วยการกดปุ่ม\
                     Shift ค้าง + ปุ่ม Enter(จำเป็นต้องขึ้นบรรทัดใหม่)', 
                icon_url=data_collector[member.guild.id]['icon']) 
                await member.send(embed=embed)
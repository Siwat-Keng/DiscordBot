import discord, asyncio, json


def set_on_member_join(bot):
    
    @bot.client.event
    async def on_member_join(member):

        if member.guild.id != bot.data['guild'].id:
            return
        
        try:
            if member.bot:
                await member.kick()
                return
            
            embed = discord.Embed(title="Welcome " + member.display_name, description = 'อย่าลืมแนะนำตัวในห้อง welcome_room ภายใน 30 นาที ตามตัวอย่างในรูปนะครับ แล้วห้องต่าง ๆ จะปรากฏขึ้น', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
            embed.add_field(name='สามารถ Copy ไปเติมได้', value="""```ชื่อ :
อายุ :
IGN(ชื่อในเกม) :
CLAN :```""", inline=False)
            embed.set_image(url='https://cdn.discordapp.com/attachments/468032916270743564/672090545555898388/Capture.JPG')
            embed.set_footer(text='ปล. ในDiscord[PC] สามารถขึ้นบรรทัดใหม่ด้วยการกดปุ่ม Shift ค้าง + ปุ่ม Enter(จำเป็นต้องขึ้นบรรทัดใหม่)', icon_url=bot.data['icon']) 
            await member.send(embed=embed)

        except Exception as err:
            print("Member Join Error : {}".format(err))

        bot.data['member_join'].append(member)

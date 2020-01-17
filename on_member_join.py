import discord, asyncio, json


def set_on_member_join(bot):
    
    @bot.client.event
    async def on_member_join(member):
        
        try:
            if member.bot:
                await member.kick()
                return
            
            
            await member.send("ยินดีต้อนรับ! อย่าลืมไปแนะนำตัวในห้อง welcome_room ภายใน 30 นาทีด้วยหล่ะ"+ '\nรูปแบบการแนะนำตัว\n' + """```ชื่อ : 
อายุ : 
IGN(ชื่อในเกม) : 
CLAN : ```""" + '\n' + '''```ปล.1 สามารถกดปุ่ม Shift ค้าง + Enter เพื่อขึ้นบรรทัดใหม่ขณะพิมพ์ได้
ปล.2 ถ้าไม่ต้องการระบุ อายุ หรือ Clan สามารถใส่เป็น - ได้
ปล.3 เมื่อแนะนำตัวตามรูปแบบดังกล่าวแล้ว ห้องต่าง ๆ จะปรากฏขึ้น
```''')

        except:
            pass

        bot.data['member_join'].append(member)

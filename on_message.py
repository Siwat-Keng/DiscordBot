import discord, asyncio, json, re
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from externalModules import itemInfo

def set_on_message(bot):

    @bot.client.event
    async def on_message(message):

        try:
            
            if message.author.bot:
                if message.author.id == 602322701146914829:
                    return
                if message.channel.id != int(bot.data['channels']['botcommands']):
                    await message.channel.send(message.content, delete_after = 1800.0)
                    await message.delete()
                return

            if message.channel.id == int(bot.data['channels']['intro']):
                introCheck = False
                stringList = re.split('\n',message.content.strip().replace(':',' '))
                profile = {}
                for string in stringList:
                    temp = re.search(r'^[^\s]+', string.strip()).group()
                    key = ''
                    maximum = 0
                    for pred in ['ชื่อ','อายุ','IGN(ชื่อในเกม)','Clan','Age','Name','Ign']:
                        ratio = SequenceMatcher(None,pred.lower(),temp.lower()).ratio()
                        if ratio > maximum:
                            key = pred
                            maximum = ratio

                    if key == 'ชื่อ':
                        key = 'Name'
                    elif key == 'อายุ':
                        key = 'Age'
                    elif key == 'IGN(ชื่อในเกม)':
                        key = 'Ign'

                    value = string.strip().replace(temp,'').strip()

                    if value == "" and key != "Clan" and key != "Age":
                        break

                    if maximum > 0.6:
                        profile[key] = value

                if ['Age', 'Clan', 'Ign', 'Name'] == sorted(list(profile.keys())):
                    introCheck = True
                    
                if introCheck:
                    checkedIntro = discord.utils.get(message.guild.roles, id=int(bot.data['checkedIntro']))
                    waitingIntro = discord.utils.get(message.guild.roles, id=int(bot.data['waitingIntro']))
                    await message.author.add_roles(checkedIntro)
                    await message.author.remove_roles(waitingIntro)
                    await message.add_reaction("✅")
                    embed = discord.Embed(title="Welcome " + message.author.name, description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง bot_command', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
                    embed.add_field(name= "!sentient", value="บอทจะ tag เมื่อมี sentient anomaly (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                    embed.add_field(name= "!arbitration {mode}", value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                    embed.add_field(name= "!price {item name}", value="บอทจะทำการ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                    embed.add_field(name= "!info {item name}", value="บอทจะทำการ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                    embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon'])
                    await message.author.send(embed=embed)
                    maximum = 0
                    for pred in bot.data['ally']:
                        ratio = SequenceMatcher(None,pred,profile['Clan']).ratio()
                        if ratio > maximum:
                            maximum = ratio
                    if maximum > 0.8:
                        allyRole = discord.utils.get(message.guild.roles, id=int(bot.data['checkedAlly']))
                        await message.author.add_roles(allyRole)
                    return
                else:
                    await message.add_reaction("❌")
                    embed = discord.Embed(title="Hello " + message.author.name, description = 'แนะนำตัวใหม่ในห้อง welcome_room ตามรูปแบบที่กำหนดนะครับ', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
                    embed.add_field(name='ถ้าไม่ต้องการใส่อายุ หรือ Clan สามารถใส่เป็น - ได้', value="""ชื่อ :
อายุ :
IGN(ชื่อในเกม) :
CLAN :""", inline=False)
                    embed.set_image(url='https://cdn.discordapp.com/attachments/468032916270743564/672090545555898388/Capture.JPG')
                    embed.set_footer(text='ปล. ในDiscord[PC] สามารถขึ้นบรรทัดใหม่ด้วยการกดปุ่ม Shift ค้าง + ปุ่ม Enter(จำเป็นต้องขึ้นบรรทัดใหม่)', icon_url=bot.data['icon']) 
                    await message.author.send(embed=embed)                    

                    return

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------                    

            if message.channel.id == 274051068164308994 and str(message.author.id) in bot.data['admins']:
                currentTime = (datetime.now() + timedelta(hours=7)).ctime()
                if message.mention_everyone:   
                    mes = [""""""]*2
                    spec = {}
                    index = 0
                    for string in message.clean_content.split('\n'):
                        if '|' in string:
                            temp = string.split('|')
                            spec[temp[0].strip()] = temp[1].strip()
                            index = 1
                        else:
                            mes[index] += string+'\n'
                    for member in message.channel.members:
                        try:
                            embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = mes[0]+'\n'+spec[bot.data['clan'][str(member.id)]]+'\n'+mes[1], color=0x00ff00)
                            embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])
                            await member.send(embed=embed)
                        except KeyError:
                            try:
                                predName = ''
                                maximum = 0
                                invalidName = bot.data['clan'][str(member.id)]
                                for name in spec:
                                    ratio = SequenceMatcher(None,name.lower(),invalidName.lower()).ratio()
                                    if ratio > maximum:
                                        predName = name
                                        maximum = ratio
                                if maximum > 0.8:
                                    try:
                                        embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = mes[0]+'\n'+spec[predName]+'\n'+mes[1], color=0x00ff00)
                                        embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])
                                        await member.send(embed=embed)
                                    except discord.Forbidden:
                                        await message.channel.send('Can not send message to '+member.name)                                        
                                    except:
                                        pass
                                else:
                                    embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = mes[0], color=0x00ff00)
                                    embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])
                                    await member.send(embed=embed)
                            except discord.Forbidden:
                                await message.channel.send('Can not send message to '+member.name)
                            except:
                                pass
                        except discord.Forbidden:
                            await message.channel.send('Can not send message to '+member.name)
                        except:
                            pass
                    await message.add_reaction("✅")
                elif len(message.mentions) != 0:
                    mes = [""""""]*2
                    spec = {}
                    index = 0
                    for string in message.clean_content.split('\n'):
                        if '|' in string:
                            temp = string.split('|')
                            spec[temp[0].strip()] = temp[1].strip()
                            index = 1
                        else:
                            mes[index] += string+'\n'
                    for member in message.mentions:
                        try:
                            embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = (mes[0]+'\n'+spec[bot.data['clan'][str(member.id)]]+'\n'+mes[1]), 
                            color=0x00ff00)
                            embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])
                            await member.send(embed=embed)
                        except KeyError:
                            try:
                                predName = ''
                                maximum = 0
                                invalidName = bot.data['clan'][str(member.id)]
                                for name in spec:
                                    ratio = SequenceMatcher(None,name.lower(),invalidName.lower()).ratio()
                                    if ratio > maximum:
                                        predName = name
                                        maximum = ratio
                                if maximum > 0.8:
                                    try:
                                        embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = (mes[0]+'\n'+spec[predName]+'\n'+mes[1]), 
                                        color=0x00ff00)
                                        embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])                                        
                                        await member.send(embed=embed)
                                    except discord.Forbidden:
                                        await message.channel.send('Can not send message to '+member.name)                                        
                                    except:
                                        pass
                                else:
                                    embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = mes[0], color=0x00ff00)
                                    embed.set_footer(text="From "+message.author.name+' ('+currentTime+')', icon_url=bot.data['icon'])                                    
                                    await member.send(embed=embed)
                            except discord.Forbidden:
                                await message.channel.send('Can not send message to '+member.name)
                            except:
                                pass
                        except discord.Forbidden:
                            await message.channel.send('Can not send message to '+member.name)
                        except:
                            pass
                    await message.add_reaction("✅")                

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------     

            if message.channel.id != int(bot.data['channels']['botcommands']):
                return

            if message.content.startswith('!price'):
                itemName = bot.data['itemCollector'].toName(message.content.replace('!price','').strip().lower())
                market = bot.data['itemCollector'].getPrice(itemName)
                embed = discord.Embed(title=itemName+" Sellers", url = market['url'], color=0x00ff00)
                for i in range(len(market['sell'][0])):
                    if i >= 5:
                        break
                    embed.add_field(name= str(market['sell'][0][i]), value=market['sell'][0][i].getSellMessage(), inline=False)
                if market['hasRank']:
                    embed.set_footer(text='Item Rank : 0', icon_url=bot.data['icon']) 
                else:
                    embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon'])                     
                buyMessage = await message.channel.send(embed=embed, delete_after=300)
                embed = discord.Embed(title=itemName+" Buyers", url = market['url'], color=0x00ff00)
                for i in range(len(market['buy'][0])):
                    if i >= 5:
                        break
                    embed.add_field(name= str(market['buy'][0][i]), value=market['buy'][0][i].getBuyMessage(), inline=False)
                if market['hasRank']:
                    embed.set_footer(text='Item Rank : 0', icon_url=bot.data['icon']) 
                else:
                    embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon']) 
                sellMessage = await message.channel.send(embed=embed, delete_after=300)
                if market['hasRank']:
                    await buyMessage.add_reaction(u"\u25C0")
                    await buyMessage.add_reaction(u"\u25B6")
                    await sellMessage.add_reaction(u"\u25C0")
                    await sellMessage.add_reaction(u"\u25B6")                
                    bot.data['message_caches'][buyMessage.id] = {"currentRank":0,"market":market,"type":"sell"}
                    bot.data['message_caches'][sellMessage.id] = {"currentRank":0,"market":market,"type":"buy"}
                await message.add_reaction("✅")

            elif message.content.startswith('!arbitration'):
                target = message.content.replace('!arbitration','')
                maximum = 0
                roleName = ''
                for name in bot.data['arbitration']:
                    ratio = SequenceMatcher(None,name,target).ratio()
                    if ratio > maximum:
                        roleName = name
                        maximum = ratio
                role = discord.utils.get(message.guild.roles, name=roleName)
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                else:
                    await message.author.add_roles(role)
                await message.add_reaction("✅")

            elif message.content.startswith('!info'):
                itemName = bot.data['itemCollector'].toName(message.content.replace('!info','').strip().lower())
                info = bot.data['itemCollector'].getInfo(itemName)
                embed = discord.Embed(title=itemName, url = info['wiki_link'], 
                description = info['description'].replace('<p>', '').replace('</p>',''), color=0x00ff00)
                for drop in info['drop']:
                    embed.add_field(name= '[ Drop ]', value = drop['name'])
                embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon'])                    
                await message.channel.send(embed=embed)
                await message.add_reaction("✅")

            elif message.content == "!sentient":
                role = discord.utils.get(message.guild.roles, name="Sentient")
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                else:
                    await message.author.add_roles(role)
                await message.add_reaction("✅")

            elif message.content == "!help":
                embed = discord.Embed(title="Greeting " + message.author.name, 
                description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง bot_command', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
                embed.add_field(name= "!sentient", value="บอทจะ tag เมื่อมี sentient anomaly (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                embed.add_field(name= "!arbitration {mode}", 
                value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                embed.add_field(name= "!price {item name}", value="บอทจะทำการ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                embed.add_field(name= "!info {item name}", value="บอทจะทำการ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon']) 
                await message.author.send(embed=embed)                
                await message.add_reaction("✅")

            elif message.content.startswith('!'):
                command = message.content.replace('!','').split()[0]
                predicted = []
                for com in ['sentient','info','arbitration','price','help']:
                    if SequenceMatcher(None,com.lower(),command).ratio() >= 0.8:
                        predicted.append('!'+com)
                if len(predicted) > 0:
                    embed = discord.Embed(title='The most similar commands', 
                    description = 'คำสั่ง !'+command+' ไม่มีในระบบ คำสั่งที่คล้าย ได้แก่', color=0x00ff00)
                    for pred in predicted:
                        embed.add_field(name='[Suggested Command]',value=pred,inline=False)

                    embed.set_footer(text='Uncle Cat (ลุงแมว) Discord', icon_url=bot.data['icon']) 
                    await message.channel.send(embed=embed)

#--------------------------------------------------------------------------------------------------------------------------------------------------------- external ------------------------
            if message.content.strip().lower().startswith('#joinrubedo') and message.author.id in {239926031111159808, 
            361494633659760653, 258502300274917376, 354958571789615104}:
                try:
                    role = discord.utils.get(message.guild.roles, name="เ ด็ ก แ ร่ แ ด ง")
                    rub_mems = message.mentions
                    for mem in rub_mems:
                        try:
                            await mem.add_roles(role)
                        except:
                            pass
                    await message.channel.send("`Done. :)`")
                    await message.delete()
                    return
                except:
                    await message.add_reaction("❌")
                    await message.channel.send("`Some error occurred.`")
                    await message.delete()
                    return

            if message.content.strip().lower().startswith('#leaverubedo') and message.author.id in {239926031111159808, 
            361494633659760653, 258502300274917376, 354958571789615104}:
                try:
                    role = discord.utils.get(message.guild.roles, name="เ ด็ ก แ ร่ แ ด ง")
                    rub_mems = message.mentions
                    for mem in rub_mems:
                        try:
                            await mem.remove_roles(role)
                        except:
                            pass
                    await message.channel.send("`Done. :)`")                    
                    await message.delete()
                    return
                except:
                    await message.add_reaction("❌")
                    await message.channel.send("`Some error occurred.`")
                    await message.delete()
                    return

#--------------------------------------------------------------------------------------------------------------------------------------------------------- external ------------------------
        except:
            try:
                await message.add_reaction("❌")
            except:
                pass

def set_on_message_delete(bot):
        
    @bot.client.event
    async def on_message_delete(message):
        if message.id in bot.data['message_caches']:
            del bot.data['message_caches'][message.id]
import discord, re
from difflib import get_close_matches
from datetime import datetime, timedelta
from externalModules.Container import *
from externalModules.LiveSearch import LiveSearch, InvalidSearch

COMMANDS = {'info','arbitration','price','help','riven','party', 'fissure', 'build','alliance'}

def set_on_message(bot):

    @bot.client.event
    async def on_message(message):

        try:
            
            if message.author.bot:
                if message.author == bot.client.user or message.mention_everyone or message.channel.guild != bot.data['guild']:
                    return
                if message.channel != bot.data['channels']['botcommands']:
                    embed = message.embeds
                    files = []
                    for att in message.attachments:
                        files.append(await att.to_file())
                    try:
                        await message.channel.send(content=message.content, embed=embed[0], files=files, delete_after = 1800.0)
                    except IndexError:
                        await message.channel.send(content=message.content, files=files, delete_after = 1800.0)
                    await message.delete()
                return

            if message.channel == bot.data['channels']['intro']:
                regex = re.compile('[: ]+')
                profile = {}
                for line in message.content.split('\n'):
                    splitedList = regex.split(line)
                    key = get_close_matches(splitedList[0].title(), 
                    {'ชื่อ','อายุ','Ign','Clan','Age','Name','Ign(ชื่อในเกม)'}, 1)
                    if not key:
                        continue
                    profile[key[0].replace('(ชื่อในเกม)', 
                    '').replace('ชื่อ', 'Name').replace('อายุ', 
                    'Age')] = ' '.join(splitedList[1:]).strip()
                if len(profile) == 4 and profile['Name'] and profile['Ign']:
                    await message.author.add_roles(bot.data['roles']['checkedIntro'])
                    await message.author.remove_roles(bot.data['roles']['waitingIntro'])
                    bot.data['members'][message.author.id] = profile  
                    await message.add_reaction("✅")
                    try:
                        await message.author.edit(nick="{}[{}][{}]".format(profile['Ign'],profile['Name'],profile['Age']))
                    except:
                        pass

                    embed = discord.Embed(title="Welcome {}".format(profile['Name']), 
                    description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง {}'.format(bot.data['channels']['botcommands'].name), 
                    url = bot.data['url'], color=0x00ff00)
                    embed.add_field(name= "{}arbitration <mode>".format(bot.data['prefix']), 
                    value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                    embed.add_field(name= "{}price <item name>".format(bot.data['prefix']), value="บอทจะ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                    embed.add_field(name= "{}info <item name>".format(bot.data['prefix']), value="บอทจะ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                    embed.add_field(name= "{}party <message>".format(bot.data['prefix']), value="บอทจะสร้างข้อความเพื่อหา Squad Member", inline=False)
                    embed.add_field(name= "{}fissure".format(bot.data['prefix']), value="บอทจะแสดง mission void fissure ปัจจุบัน", inline=False)
                    embed.add_field(name= "{}build".format(bot.data['prefix']), value="บอทจะ search build จาก overframe.gg", inline=False)
                    embed.add_field(name= "{}riven <weapon name> <+stat +stat +stat -stat> <price>".format(bot.data['prefix']), value="บอทจะ live search riven", inline=False)                     
                    embed.add_field(name= "{}alliance <clan name>".format(bot.data['prefix']), value="บอทจะแสดงข้อมูลแคลนนั้น ๆ (ใน alliance)", inline=False)                     
                    embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                    await message.author.send(embed=embed)
                    try:
                        get_close_matches(profile['Clan'],bot.data['ally'].keys(),n=1,cutoff=0.8)[0]
                        await message.author.add_roles(bot.data['roles']['checkedAlly'])
                    except IndexError:
                        pass
                else:
                    await message.add_reaction("❌")
                    embed = discord.Embed(title="Hello {}".format(message.author.name), 
                    description = 'แนะนำตัวใหม่ในห้อง welcome_room ภายใน {} นาที ตามรูปแบบที่กำหนดนะครับ'.format((message.author.joined_at-datetime.now()+timedelta(minutes=30)).seconds//60), 
                    url = bot.data['url'], color=0x00ff00)
                    embed.add_field(name='ถ้าไม่ต้องการใส่อายุ หรือ Clan สามารถใส่เป็น - ได้', value="""```ชื่อ :
อายุ :
IGN(ชื่อในเกม) :
CLAN :```""", inline=False)
                    embed.set_image(url='https://cdn.discordapp.com/attachments/468032916270743564/672090545555898388/Capture.JPG')
                    embed.set_footer(text='ปล. ในDiscord[PC] สามารถขึ้นบรรทัดใหม่ด้วยการกดปุ่ม Shift ค้าง + ปุ่ม Enter(จำเป็นต้องขึ้นบรรทัดใหม่)', icon_url=bot.data['icon']) 
                    await message.author.send(embed=embed)
                    await message.delete(delay=60)
                return

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------                    

            if message.channel == bot.data['channels']['clan'] and (set(message.author.roles).intersection(bot.data['roles']['admins'])):
                currentTime = (datetime.now() + timedelta(hours=7)).ctime()
                if message.mention_everyone:   
                    mes = ['']*2
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
                        if member.bot:
                            continue
                        try:
                            spec_message = spec[get_close_matches(bot.data['clan'][str(member.id)], spec.keys(), 1)[0]]+'\n'
                        except:
                            spec_message = ''
                        try:
                            embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = mes[0]+'\n'+spec_message+mes[1], color=0x00ff00)
                            embed.set_footer(text="From {} ({})".format(message.author.name, currentTime), icon_url=bot.data['icon'])
                            await member.send(embed=embed)
                        except discord.Forbidden:
                            await message.channel.send('Can not send message to '+member.name)
                    await message.add_reaction("✅")
                elif len(message.mentions) != 0:
                    mes = ['']*2
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
                            spec_message = spec[get_close_matches(bot.data['clan'][str(member.id)], spec.keys(), 1)[0]]+'\n'
                        except:
                            spec_message = ''                       
                        try:
                            embed = discord.Embed(title="Notice (Uncle Cat Discord)",description = (mes[0]+'\n'+spec_message+mes[1]), 
                            color=0x00ff00)
                            embed.set_footer(text="From {} ({})".format(message.author.name, currentTime), icon_url=bot.data['icon'])
                            await member.send(embed=embed)
                        except discord.Forbidden:
                            await message.channel.send('Can not send message to {}'.format(member.name))
                    await message.add_reaction("✅")  
                return

            if message.channel == bot.data['channels']['ally']:
                regex = re.compile('\s+:*\s*|\s*:+\s*')  
                profile = {}
                for line in message.content.split('\n'):
                    splitedList = regex.split(line)
                    key = get_close_matches(splitedList[0].title(), 
                    {'Clan','Leader'}, 1)
                    if not key:
                        continue
                    profile[key[0]] = ' '.join(splitedList[1:])
                if message.attachments:
                    profile['url'] = message.attachments[0].url
                else:
                    profile['url'] = ''
                bot.data['ally'][profile['Clan']] = profile
                del bot.data['ally'][profile['Clan']]['Clan']   
                return                    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------     
            if message.channel.id == 295477991356497920:
                embed = message.embeds
                channel = bot.client.get_channel(698812557363773471)
                files = []
                for att in message.attachments:
                    files.append(await att.to_file())
                await channel.send(content=message.content, files=files)
                return

            if message.channel.id == 698812557363773471:
                embed = message.embeds
                channel = bot.client.get_channel(295477991356497920)
                files = []
                for att in message.attachments:
                    files.append(await att.to_file())
                await channel.send(content=message.content, files=files)
                return        
            
#--------------------------------------------------------------------------------------------------------
            if message.channel != bot.data['channels']['botcommands']:
                return

            if message.content.startswith('{}price'.format(bot.data['prefix'])):
                buyMessage = await message.channel.send('```Loading...```', delete_after=300)
                sellMessage = await message.channel.send('```Loading...```', delete_after=300)
                try:
                    itemName = bot.data['itemCollector'].toName(message.content[len('{}price'.format(bot.data['prefix'])):].strip().lower())
                except KeyError:
                    await buyMessage.delete()
                    await sellMessage.delete()
                    await message.add_reaction("❌")
                    return
                market = await bot.data['itemCollector'].getPrice(itemName)
                if market['hasRank']:
                    bot.data['message_caches'][buyMessage.id] = MarketRankContainer(market, 'sell', buyMessage, bot.data['itemCollector'], bot.data['icon'])
                    bot.data['message_caches'][sellMessage.id] = MarketRankContainer(market, 'buy', sellMessage, bot.data['itemCollector'], bot.data['icon'])
                else:
                    bot.data['message_caches'][buyMessage.id] = MarketContainer(market, 'sell', buyMessage, bot.data['itemCollector'], bot.data['icon'], bot.data['footer'])
                    bot.data['message_caches'][sellMessage.id] = MarketContainer(market, 'buy', sellMessage, bot.data['itemCollector'], bot.data['icon'], bot.data['footer'])             
                await bot.data['message_caches'][buyMessage.id].setMessage()
                await bot.data['message_caches'][sellMessage.id].setMessage()                    
                await message.add_reaction("✅")

            elif message.content.startswith('{}arbitration'.format(bot.data['prefix'])):
                target = message.content[len('{}arbitration'.format(bot.data['prefix'])):].strip().lower()
                roleName = get_close_matches(target.lower(), bot.data['roles']['arbitration'].keys(), 1)[0]
                role = bot.data['roles']['arbitration'][roleName]
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                else:
                    await message.author.add_roles(role)
                await message.add_reaction("✅")

            elif message.content.startswith('{}info'.format(bot.data['prefix'])):
                embed = await bot.data['itemCollector'].getInfo(message.content[len('{}info'.format(bot.data['prefix'])):].strip().lower())
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])                    
                await message.channel.send(embed=embed)
                await message.add_reaction("✅")

            elif message.content == "{}fissure".format(bot.data['prefix']):
                fissureMessage = await message.channel.send('```Loading...```', delete_after=300)
                bot.data['message_caches'][fissureMessage.id] = FissureContainer(fissureMessage, 
                bot.data['icon'], bot.data['footer'], bot.data['world_data'].fissures)
                await bot.data['message_caches'][fissureMessage.id].setMessage()
                await message.add_reaction("✅")
            
            elif message.content.startswith("{}party".format(bot.data['prefix'])):
                target = message.content[len('{}party'.format(bot.data['prefix'])):].strip()
                embed = discord.Embed(title='{} Squad'.format(target), color=0x00ff00)
                embed.add_field(name="Squad Members", 
                value='1. {}\n2.\n3.\n4.\n👍 => Join Squad\n👎 => Leave Squad\n🚩 => Refresh [Host]\n1️⃣2️⃣3️⃣4️⃣ => Search Profile'.format('{} [Leader]'.format(message.author.display_name)), 
                inline=False)
                embed.set_image(url="https://cdn.discordapp.com/attachments/633256433512611871/692296672818233394/c05a0897365521040712bde69e3bc819.jpg")
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                partyMessage = await bot.data['channels']['general'].send(embed=embed, delete_after=1800)
                await partyMessage.add_reaction("👍")
                await partyMessage.add_reaction("👎")
                await partyMessage.add_reaction("1️⃣")
                await partyMessage.add_reaction("2️⃣")
                await partyMessage.add_reaction("3️⃣")
                await partyMessage.add_reaction("4️⃣")   
                await partyMessage.add_reaction("🚩")   
                bot.data['message_caches'][partyMessage.id] = PartyContainer(partyMessage, embed, target, message.author)      
                bot.data['message_caches'][partyMessage.id].setFooterText(bot.data['footer'])      
                bot.data['message_caches'][partyMessage.id].setIcon(bot.data['icon'])
                bot.data['message_caches'][partyMessage.id].setIntroChannel(bot.data['channels']['intro'])
                bot.data['message_caches'][partyMessage.id].setUrl("https://cdn.discordapp.com/attachments/633256433512611871/692296672818233394/c05a0897365521040712bde69e3bc819.jpg")
                await message.add_reaction("✅")

            elif message.content.startswith('{}alliance'.format(bot.data['prefix'])):
                allyMessage = await message.channel.send('```Loading...```', delete_after=300)
                target = message.content[len('{}alliance'.format(bot.data['prefix'])):]
                target = get_close_matches(target, bot.data['ally'].keys())
                if target:
                    embed = discord.Embed(title='{} Clan'.format(target[0]),
                    description ='Leader : {}'.format(bot.data['ally'][target[0]]['Leader']),
                    color=0x00ff00)
                    embed.set_image(url=bot.data['ally'][target[0]]['url'])
                    embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                    await allyMessage.edit(content=None, embed=embed)
                else:
                    bot.data['message_caches'][allyMessage.id] = AllianceCollector(allyMessage, bot.data['icon'], bot.data['footer'], bot.data['ally'])
                    await bot.data['message_caches'][allyMessage.id].setMessage()
                await message.add_reaction("✅")   

            elif message.content.startswith('{}build'.format(bot.data['prefix'])):    
                target = message.content[len('{}build'.format(bot.data['prefix'])):].strip()       
                for embed in bot.data['build'].getBuild(target):
                    await message.channel.send(embed=embed, delete_after=300)
                await message.add_reaction("✅")  

            elif message.content.startswith("{}riven".format(bot.data['prefix'])):  
                target = message.content[len('{}riven'.format(bot.data['prefix'])):].strip() 
                searchMessage = await message.channel.send('```Loading...```')   
                try:
                    bot.data['message_caches'][searchMessage.id] = LiveSearch(bot.client, searchMessage, target, bot.data['footer'], bot.data['icon'], 
                    list(bot.data['itemCollector'].weapons.keys()), message.author)        
                except InvalidSearch:
                    try:
                        regex = re.compile('^[^+-]+')
                        target = regex.search(target).group().strip()
                        embed = await bot.data['itemCollector'].getRivenPrice(target.lower())   
                        embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon']) 
                        await searchMessage.clear_reactions()
                        await searchMessage.edit(content=None, embed=embed, delete_after=300) 
                    except:
                        await searchMessage.delete()
                        await message.add_reaction("❌")
                        return     
                except:
                    await searchMessage.delete()
                    await message.add_reaction("❌")
                    return      
                await message.add_reaction("✅")               

            elif message.content == "{}help".format(bot.data['prefix']):
                embed = discord.Embed(title="Hello {}".format(message.author.name), 
                description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง {}'.format(bot.data['channels']['botcommands'].name), 
                url = bot.data['url'], color=0x00ff00)
                embed.add_field(name= "{}arbitration <mode>".format(bot.data['prefix']), 
                value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                embed.add_field(name= "{}price <item name>".format(bot.data['prefix']), value="บอทจะ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                embed.add_field(name= "{}info <item name>".format(bot.data['prefix']), value="บอทจะ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                embed.add_field(name= "{}party <message>".format(bot.data['prefix']), value="บอทจะสร้างข้อความเพื่อหา Squad Member", inline=False)
                embed.add_field(name= "{}fissure".format(bot.data['prefix']), value="บอทจะแสดง mission void fissure ปัจจุบัน", inline=False)
                embed.add_field(name= "{}build".format(bot.data['prefix']), value="บอทจะ search build จาก overframe.gg", inline=False)
                embed.add_field(name= "{}riven <weapon name> <+stat +stat +stat -stat> <price>".format(bot.data['prefix']), value="บอทจะ live search riven", inline=False)                     
                embed.add_field(name= "{}alliance <clan name>".format(bot.data['prefix']), value="บอทจะแสดงข้อมูลแคลนนั้น ๆ (ใน alliance)", inline=False)                     
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                await message.author.send(embed=embed)                
                await message.add_reaction("✅")    

            elif message.content.startswith('{}'.format(bot.data['prefix'])):
                command = message.content[1:].split()[0]
                predicted = get_close_matches(command, COMMANDS, len(COMMANDS))
                if len(predicted) > 0:
                    embed = discord.Embed(title='The most similar commands', 
                    description = 'คำสั่ง {}{} ไม่มีในระบบ คำสั่งที่คล้าย ได้แก่'.format(bot.data['prefix'],command), color=0x00ff00)
                    for pred in predicted:
                        embed.add_field(name='[Suggested Command]',value="{}{}".format(bot.data['prefix'],pred),inline=False)
                    embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon']) 
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
        except Exception as err:
            print("An error occurs[on_message] : {}".format(err))
            try:
                await message.add_reaction("❌")
            except:
                pass

def set_on_message_delete(bot):
        
    @bot.client.event
    async def on_message_delete(message):
        if message.id in bot.data['message_caches']:
            del bot.data['message_caches'][message.id]
import discord, asyncio, json, re
from difflib import get_close_matches
from datetime import datetime, timedelta
from externalModules import itemInfo
from externalModules.Container import PartyContainer, MarketRankContainer, MarketContainer

def set_on_message(bot):

    @bot.client.event
    async def on_message(message):

        try:
            
            if message.author.bot:
                if message.author.id == 602322701146914829:
                    return
                if message.channel.id not in {int(bot.data['channels']['botcommands']), 592192367663251466}:
                    embed = message.embeds
                    files = []
                    for att in message.attachments:
                        files.append(await att.to_file())
                    if message.mention_everyone:
                        try:
                            await message.channel.send(content=message.content, embed=embed[0], files=files)
                        except IndexError:
                            await message.channel.send(content=message.content, files=files)
                    else:
                        try:
                            await message.channel.send(content=message.content, embed=embed[0], files=files, delete_after = 1800.0)
                        except IndexError:
                            await message.channel.send(content=message.content, files=files, delete_after = 1800.0)
                    await message.delete()
                return

            if message.channel == bot.data['channel']['intro']:
                stringList = re.split('\n',message.content.strip().replace(':',' '))
                profile = {}
                for string in stringList:
                    try:
                        temp = re.search(r'^[^\s]+', string.strip()).group()
                    except AttributeError:
                        temp = ''
                    try:
                        key = get_close_matches(temp.capitalize(), ['ชื่อ','อายุ','IGN(ชื่อในเกม)','Clan','Age','Name','Ign'],1)[0]
                        if key == 'ชื่อ':
                            key = 'Name'
                        elif key == 'อายุ':
                            key = 'Age'
                        elif key == 'IGN(ชื่อในเกม)':
                            key = 'Ign'
                        value = string[len(temp):].strip()
                        if (value == "" or value == "-") and key != "Clan" and key != "Age":
                            break
                        profile[key] = value
                    except IndexError:
                        pass

                if ['Age', 'Clan', 'Ign', 'Name'] == sorted(list(profile.keys())):
                    checkedIntro = discord.utils.get(message.guild.roles, id=int(bot.data['checkedIntro']))
                    waitingIntro = discord.utils.get(message.guild.roles, id=int(bot.data['waitingIntro']))
                    await message.author.add_roles(checkedIntro)
                    await message.author.remove_roles(waitingIntro)
                    bot.data['members'][message.author.id] = profile  
                    await message.add_reaction("✅")

                    try:
                        await message.author.edit(nick="{}[{}][{}]".format(profile['Ign'],profile['Name'],profile['Age']))
                    except:
                        pass

                    embed = discord.Embed(title="Welcome {}".format(profile['Name']), description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง bot_command', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
                    embed.add_field(name= "{}arbitration <mode>".format(bot.data['prefix']), 
                    value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                    embed.add_field(name= "{}price <item name>".format(bot.data['prefix']), value="บอทจะทำการ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                    embed.add_field(name= "{}info <item name>".format(bot.data['prefix']), value="บอทจะทำการ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                    embed.add_field(name= "{}build <item name>".format(bot.data['prefix']), value="บอทจะทำการ search build ตามชื่อ (จาก channel build_mod)", inline=False)
                    embed.add_field(name= "{}kuva <item name> <element>".format(bot.data['prefix']), value="บอทจะทำการ search ราคา kuva weapon ตามชื่อและธาตุโบนัส (จาก WarframeTeams.com)", inline=False)
                    embed.add_field(name= "{}party <message>".format(bot.data['prefix']), value="บอทจะทำการสร้างข้อความเพื่อหา Squad Member", inline=False)
                    embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                    await message.author.send(embed=embed)
                    try:
                        get_close_matches(profile['Clan'],bot.data['ally'],n=1,cutoff=0.8)[0]
                        allyRole = discord.utils.get(message.guild.roles, id=int(bot.data['checkedAlly']))
                        await message.author.add_roles(allyRole)
                    except IndexError:
                        pass
                    finally:
                        return
                else:
                    await message.add_reaction("❌")
                    embed = discord.Embed(title="Hello {}".format(message.author.name), description = 'แนะนำตัวใหม่ในห้อง welcome_room ตามรูปแบบที่กำหนดนะครับ', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
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

            if str(message.channel.id) == bot.data['channels']['clan'] and len(set(message.author.roles) & bot.data['admins']) != 0:
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

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------     
            if message.channel == bot.data['channel']['build']:
                stringList = re.split('\n',message.content.strip().replace(':',' '))
                profile = {}
                for string in stringList:
                    try:
                        temp = re.search(r'^[^\s]+', string.strip()).group()
                        key = get_close_matches(temp, ['Name', 'IGN', 'Description'], 1)[0]
                        value = string.strip().replace(temp,'').strip()
                        profile[key] = value
                    except (IndexError, AttributeError):
                        pass

                if ['Description', 'IGN', 'Name'] == sorted(list(profile.keys())):
                    attachments = message.attachments[0].url            
                    if profile['Name'] in bot.data['build']:
                        bot.data['build'][profile['Name']].append({'Name':profile['Name'],
                        'IGN':profile['IGN'],
                        'Description':profile['Description'],
                        'Image':attachments })                  
                    else:
                        bot.data['build'][profile['Name']] = []
                        bot.data['build'][profile['Name']].append({'Name':profile['Name'],
                        'IGN':profile['IGN'],
                        'Description':profile['Description'],
                        'Image':attachments }) 
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
            if message.channel.id != int(bot.data['channels']['botcommands']):
                return

            if message.content.startswith('{}price'.format(bot.data['prefix'])):
                itemName = bot.data['itemCollector'].toName(message.content.replace('!price','').strip().lower())
                market = bot.data['itemCollector'].getPrice(itemName)
                buyMessage = await message.channel.send('```Loading...```', delete_after=300)
                sellMessage = await message.channel.send('```Loading...```', delete_after=300)                
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
                target = message.content.replace('{}arbitration'.format(bot.data['prefix']),'')
                roleName = get_close_matches(target.lower(), bot.data['arbitration'].keys(), 1)[0]
                role = discord.utils.get(message.guild.roles, name=roleName)
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                else:
                    await message.author.add_roles(role)
                await message.add_reaction("✅")

            elif message.content.startswith("{}build".format(bot.data['prefix'])):
                target = message.content.replace('{}build'.format(bot.data['prefix']), '').lower().replace('prime', '').replace('kuva', '').replace('vandal', '').replace('wraith', '').replace('mara', '').replace('prisma', '').strip()
                embedList = []
                for name in get_close_matches(target, bot.data['build'].keys(), len(bot.data['build'])):
                        for item in bot.data['build'][name]:
                            embedList.append(item)
                for emb in embedList:
                    embed = discord.Embed(title=(emb['Name']+' Build').strip(), 
                    url = emb['Image'], 
                    description = 'Description : {}'.format(emb['Description']),
                    color=0x00ff00)
                    embed.set_image(url=emb['Image'])
                    embed.set_footer(text='From : {}'.format(emb['IGN']), icon_url=bot.data['icon']) 
                    await message.author.send(embed = embed)
                await message.delete()

            elif message.content.startswith('{}info'.format(bot.data['prefix'])):
                embed = bot.data['itemCollector'].getInfo(message.content.replace('{}info'.format(bot.data['prefix']),'').strip())
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])                    
                await message.channel.send(embed=embed)
                await message.add_reaction("✅")

            elif message.content.startswith('{}kuva'.format(bot.data['prefix'])):
                temp = message.content[5:].lower().replace('kuva', '').split()
                if len(temp) < 2:
                    await message.add_reaction("❌")
                    return
                weaponName = ' '.join(temp[:len(temp)-1])
                elemental = temp[len(temp)-1]            
                weaponName, weaponList = bot.data['itemCollector'].getKuvaWeaponPrice(weaponName, elemental)
                embed = discord.Embed(title='Kuva {} Sellers'.format(weaponName), 
                url = 'https://www.warframeteams.com/index.php', color=0x00ff00)
                for item in weaponList:
                    embed.add_field(name= str(item), value=item.getMessage(), inline=False)
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])                     
                await message.channel.send(embed=embed, delete_after=300)
                await message.add_reaction("✅")

            elif message.content == "{}sentient".format(bot.data['prefix']):
                role = discord.utils.get(message.guild.roles, name="Sentient")
                if role in message.author.roles:
                    await message.author.remove_roles(role)
                else:
                    await message.author.add_roles(role)
                await message.add_reaction("✅")
            
            elif message.content.startswith("{}party".format(bot.data['prefix'])):
                target = message.content.replace('{}party'.format(bot.data['prefix']),'').strip()
                embed = discord.Embed(title='{} Squad'.format(target.title()), color=0x00ff00)
                embed.add_field(name="Squad Members", 
                value='1. {}\n2.\n3.\n4.\n👍 => Join Squad\n👎 => Leave Squad\n🚩 => Refresh [Host]\n1️⃣2️⃣3️⃣4️⃣ => Search Profile'.format('{} [Leader]'.format(message.author.display_name)), 
                inline=False)
                embed.set_image(url="https://cdn.discordapp.com/attachments/633256433512611871/692296672818233394/c05a0897365521040712bde69e3bc819.jpg")
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])
                partyMessage = await bot.data['channel']['general'].send(embed=embed, delete_after=1800)
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
                bot.data['message_caches'][partyMessage.id].setIntroChannel(bot.data['channel']['intro'])
                bot.data['message_caches'][partyMessage.id].setUrl("https://cdn.discordapp.com/attachments/633256433512611871/692296672818233394/c05a0897365521040712bde69e3bc819.jpg")
                await message.add_reaction("✅")

            elif message.content == "{}help".format(bot.data['prefix']):
                embed = discord.Embed(title="Greeting {}".format(message.author.name), 
                description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง bot_command', url = 'https://www.facebook.com/UncleCatTH', color=0x00ff00)
                embed.add_field(name= "{}arbitration <mode>".format(bot.data['prefix']), 
                value="บอทจะ tag เมื่อ arbitration เป็น mode ที่กำหนด (สามารถใช้คำสั่งนี้ซ้ำอีกครั้ง เพื่อยกเลิก)", inline=False)
                embed.add_field(name= "{}price <item name>".format(bot.data['prefix']), value="บอทจะทำการ search ราคา item ตามชื่อ (จาก Warframe Market)", inline=False)
                embed.add_field(name= "{}info <item name>".format(bot.data['prefix']), value="บอทจะทำการ search ข้อมูล item ตามชื่อ (จาก Warframe Wiki)", inline=False)
                embed.add_field(name= "{}build <item name>".format(bot.data['prefix']), value="บอทจะทำการ search build ตามชื่อ (จาก channel build_mod)", inline=False)
                embed.add_field(name= "{}kuva <item name> <element>".format(bot.data['prefix']), value="บอทจะทำการ search ราคา kuva weapon ตามชื่อและธาตุโบนัส (จาก WarframeTeams.com)", inline=False)
                embed.add_field(name= "{}party <message>".format(bot.data['prefix']), value="บอทจะทำการสร้างข้อความเพื่อหา Squad Member", inline=False)
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon']) 
                await message.author.send(embed=embed)                
                await message.add_reaction("✅")    

            elif message.content.startswith('{}'.format(bot.data['prefix'])):
                command = message.content[1:].split()[0]
                predicted = get_close_matches(command, ['info','arbitration','price','help','build','kuva','party'],len(['sentient','info','arbitration','price','help','build','kuva','party']))
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
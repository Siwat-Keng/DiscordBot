import discord, sys, re
from discord.ext import tasks
from datetime import datetime, timedelta
from externalModules import worldStat, itemInfo
from difflib import get_close_matches

def set_background_process(bot):

    @tasks.loop(seconds=3.0)
    async def cycleMessage():

        currentTime = (datetime.now() + timedelta(hours=7)).replace(microsecond=0)

        if bot.data['world_data'].arbitration.needMention:
            try:
                await bot.data['message']['arbyMention'].delete()
            except (UnboundLocalError, discord.NotFound):
                pass
            try:
                bot.data['message']['arbyMention'] = await bot.data['channel']['alert'].send(bot.data['arbitration'][bot.data['world_data'].arbitration.getMention()])
            except KeyError:
                pass
            
        if bot.data["world_data"].sentientOutposts.needMention:
            bot.data["mentioned_sentient"] = await bot.data['channel']['alert'].send(bot.data['Sentient'])
            bot.data["world_data"].sentientOutposts.needMention = False
        
        if bot.data["world_data"].sentientOutposts.currentMission == None:
            try:
                await bot.data["mentioned_sentient"].delete()
            except (KeyError, discord.NotFound):
                pass
    
        try:

            await bot.data['message']['updateMessage'].edit(content = """```css
"""+str(bot.data['world_data'].arbitration)+'\n\n'+str(bot.data['world_data'].timeCycle)+'\n\n'+str(bot.data["world_data"].sentientOutposts)+'```')

            if bot.data["world_data"].news.needEdit:
                embed = discord.Embed.from_dict(bot.data["world_data"].news.getDict())
                embed.set_image(url=bot.data["world_data"].news.image)
                embed.set_footer(text='Current Time : ' + currentTime.strftime("%H:%M (%m/%d/%Y)"), icon_url=bot.data['icon']) 

                await bot.data['message']['embedMessage'].edit(content = None, embed = embed)
            
        except discord.NotFound:
            
            async for message in bot.data['channel']['alert'].history():
                await message.delete()
                
            bot.data['message']['updateMessage'] = await bot.data['channel']['alert'].send('```Loading...```')
            bot.data['message']['embedMessage'] = await bot.data['channel']['alert'].send('```Loading...```') 

            bot.data["world_data"].news.needEdit = True               

        except:
            print("Unexpected error:", sys.exc_info())


    @cycleMessage.before_loop
    async def before_cycleMessage():

        bot.data['channel'] = {}
        bot.data['message'] = {}

        await bot.client.wait_until_ready()

        game = discord.Game('!help')
        await bot.client.change_presence(status=discord.Status.online, activity=game)
        
        bot.data['channel']['general'] = bot.client.get_channel(int(bot.data['channels']['general']))
        bot.data['channel']['alert'] = bot.client.get_channel(int(bot.data['channels']['alert']))
        
        async for message in bot.data['channel']['alert'].history():
            await message.delete()
        
        bot.data['message']['updateMessage'] = await bot.data['channel']['alert'].send('```Loading...```')
        bot.data['message']['embedMessage'] = await bot.data['channel']['alert'].send('```Loading...```')
        bot.data['message']['arbyMention'] = await bot.data['channel']['alert'].send('```Loading...```')        


    @tasks.loop(seconds=60.0)
    async def memberCycle():
        for member in bot.data['member_join']:
            
            guild = await bot.client.fetch_guild(int(bot.data['guild']))
            role = discord.utils.get(guild.roles, id=int(bot.data['checkedIntro']))
            vip_role = discord.utils.get(guild.roles, id=int(bot.data['VIP']))

            if role in member.roles or vip_role in member.roles:
                bot.data['member_join'].remove(member)
                
            elif (datetime.now() - member.joined_at).seconds//60 >= 31 and role not in member.roles:
                embed = discord.Embed(title="สามารถคลิกที่นี่ เพื่อกลับเข้าสู่ Server อีกครั้ง", 
                description = 'คุณจะถูกนำออกจาก Server เนื่องจากไม่แนะนำตัว ภายใน 30 นาที', 
                url = 'https://discordapp.com/invite/j3HMUmW', color=0x00ff00)
                embed.set_image(url="https://cdn.discordapp.com/attachments/633256433512611871/693076211794182226/unknown.png")
                embed.set_footer(text=bot.data['footer'], icon_url=bot.data['icon'])   
                try:
                    await member.send(embed=embed)
                except:
                    pass
                try:
                    await member.kick(reason = 'ไม่รายงานตัว')
                except:
                    pass
                try:
                    bot.data['member_join'].remove(member) 
                except ValueError:
                    pass 

    @memberCycle.before_loop
    async def before_memberCycle():
        bot.data['members'] = {}
        await bot.client.wait_until_ready()        
        bot.data['channel']['intro'] = bot.client.get_channel(int(bot.data['channels']['intro']))
        async for message in bot.data['channel']['intro'].history(limit=None):
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
                bot.data['members'][message.author.id] = profile

    @tasks.loop(seconds=3.0)
    async def updateData():
        bot.data['world_data'].update()
        bot.data['itemCollector'].update()
        
    @updateData.before_loop
    async def before_updateData():
        await bot.client.wait_until_ready()
        bot.data['member_join'] = []
        bot.data['message_caches'] = {}        
        bot.data['itemCollector'] = itemInfo.ItemInfo()
        bot.data['world_data'] = worldStat.WorldStat() 

    @tasks.loop(seconds=60.0)
    async def updateDiscordData():
        temp = set()
        async for message in bot.data['channel']['ally'].history(limit=None):
            mes = message.content.split('\n')
            for m in mes:
                try:
                    key = re.search(r'^Clan :',m).group()
                except AttributeError:
                    key = ''
                value = m[len(key):].strip()
                if key == 'Clan :':
                    temp.add(value.strip())
                    
        del bot.data['ally']
        bot.data['ally'] = temp

    @updateDiscordData.before_loop
    async def before_updateDiscordData():
        await bot.client.wait_until_ready()
        bot.data['channel']['ally'] = bot.client.get_channel(int(bot.data['channels']['ally']))
        bot.data['channel']['build'] = bot.client.get_channel(int(bot.data['channels']['build']))
        bot.data['ally'] = set()
        bot.data['build'] = {}
        async for message in bot.data['channel']['build'].history(limit=None):
            stringList = re.split('\n',message.content.strip().replace(':',' '))
            profile = {}
            for string in stringList:
                try:
                    temp = re.search(r'^[^\s]+', string.strip()).group()
                    key = get_close_matches(temp, ['Name', 'IGN', 'Description'],1)[0]
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
                    'Image':attachments
                    })                    
                else:
                    bot.data['build'][profile['Name']] = []
                    bot.data['build'][profile['Name']].append({'Name':profile['Name'],
                    'IGN':profile['IGN'],
                    'Description':profile['Description'],
                    'Image':attachments
                    })  

    
    updateData.start()
    memberCycle.start()
    cycleMessage.start()
    updateDiscordData.start()
    
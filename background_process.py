import discord, asyncio, sys, re
from discord.ext import tasks
from datetime import datetime, timedelta
from externalModules import worldStat, itemInfo
from difflib import SequenceMatcher

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

        await bot.client.wait_until_ready()

        game = discord.Game('!help')
        await bot.client.change_presence(status=discord.Status.online, activity=game)

        bot.data['channel'] = {}
        bot.data['message'] = {}
        
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
                try:
                    await member.send("""```css
[ คุณจะถูกเตะเนื่องจากไม่แนะนำตัว ภายใน 30 นาที ]```""")
                except:
                    pass
                try:
                    await member.kick(reason = 'ไม่รายงานตัว')
                except:
                    pass
                bot.data['member_join'].remove(member)  

    @memberCycle.before_loop
    async def before_memberCycle():
        await bot.client.wait_until_ready()

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
        async for message in bot.data['channel']['ally'].history():
            mes = message.content.split('\n')
            for m in mes:
                try:
                    key = re.search(r'^Clan :',m).group()
                except AttributeError:
                    key = ''
                value = m.replace(key,'')
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
        async for message in bot.data['channel']['build'].history():
            stringList = re.split('\n',message.content.strip().replace(':',' '))
            profile = {}
            for string in stringList:
                try:
                    temp = re.search(r'^[^\s]+', string.strip()).group()
                    key = ''
                    maximum = 0
                    for pred in ['Name', 'IGN', 'Description']:
                        ratio = SequenceMatcher(None,pred.lower(),temp.lower()).ratio()
                        if ratio > maximum:
                            key = pred
                            maximum = ratio
                    value = string.strip().replace(temp,'').strip()

                    if maximum > 0.8:
                        profile[key] = value

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
                except AttributeError:
                    pass
    
    updateData.start()
    memberCycle.start()
    cycleMessage.start()
    updateDiscordData.start()
    
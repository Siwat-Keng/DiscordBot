import discord, asyncio, json, re, sys
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from externalModules import worldStat, itemInfo
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

def set_background_process(bot):

    @tasks.loop(seconds=1.0)
    async def cycleMessage():

        currentTime = (datetime.now() + timedelta(hours=7)).replace(microsecond=0)

        if bot.data['world_data'].arbitration.needMention:
            try:
                await bot.data['message']['arbyMention'].delete()
            except (discord.NotFound, KeyError, UnboundLocalError):
                pass
            bot.data['message']['arbyMention'] = await bot.data['channel']['alert'].send(bot.data['arbitration'][bot.data['world_data'].arbitration.getMention()])

        if bot.data["world_data"].sentientOutposts.needMention:
            bot.data["mentioned_sentient"] = await bot.data['channel']['alert'].send(bot.data['Sentient'])
            bot.data["world_data"].sentientOutposts.needMention = False
        
        if bot.data["world_data"].sentientOutposts.currentMission == None:
            try:
                await bot.data["mentioned_sentient"].delete()
            except KeyError:
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

    @tasks.loop(seconds=1.0)
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
    async def updateAlliance():
        temp = set()
        async for message in bot.data['channel']['ally'].history():
            mes = message.content.split('\n')
            for m in mes:
                try:
                    key = re.search(r'^Clan :',m).group()
                except:
                    key = ''
                value = m.replace(key,'')
                if key == 'Clan :':
                    temp.add(value.strip())
        bot.data['ally'] = temp

    @updateAlliance.before_loop
    async def before_updateAlliance():
        await bot.client.wait_until_ready()
        bot.data['channel']['ally'] = bot.client.get_channel(int(bot.data['channels']['ally']))
        bot.data['ally'] = set()
    
    updateData.start()
    memberCycle.start()
    cycleMessage.start()
    updateAlliance.start()
    
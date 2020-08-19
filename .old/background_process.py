import discord, sys, re
from discord.ext import tasks
from datetime import datetime, timedelta
from services.WorldStat import WorldStat
from services.ItemInfo import ItemInfo
from services.Build import BuildCollector
from services.Notification import Notification
from services.Share import Share
from services.Announcement import Announcement
from difflib import get_close_matches

def set_background_process(bot):

    @tasks.loop(seconds=3.0)
    async def cycleMessage():
        currentTime = (datetime.now() + timedelta(hours=7)).replace(microsecond=0)
        try:
            async for message in bot.data['channels']['alert'].history():
                if message.id not in bot.data['message']['collector']:
                    await message.delete()    
        except:
            pass

        try:
            for noti in bot.data['notification']:
                if noti.notify(currentTime):
                    await bot.data['channels']['general'].send(noti.get_message())
        except Exception as err:
            print('Notification Error :', err)
        
        try:
            status = discord.Game('{}help | {} Members'.format(bot.data['prefix'], len(bot.data['members'])))
            await bot.client.change_presence(status=discord.Status.online, activity=status)
        except:
            pass

        if bot.data['world_data'].arbitration.needMention:
            try:
                bot.data['message']['collector'].remove(bot.data['message']['arbyMention'].id)
            except:
                pass
            try:
                bot.data['message']['arbyMention'] = await bot.data['channels']['alert'].send(bot.data['roles']['arbitration'][bot.data['world_data'].arbitration.getMention()].mention)
                bot.data['message']['collector'].add(bot.data['message']['arbyMention'].id) 
            except:
                pass
        try:
            await bot.data['message']['updateMessage'].edit(content = "```css\n{}\n\n{}\n\n{}```".format(bot.data['world_data'].arbitration, 
            bot.data['world_data'].timeCycle, bot.data["world_data"].sentientOutposts))

            if bot.data["world_data"].news.needEdit:
                embed = discord.Embed.from_dict(bot.data["world_data"].news.getDict())
                embed.set_image(url=bot.data["world_data"].news.image)
                embed.set_footer(text='Current Time : ' + currentTime.strftime("%H:%M (%m/%d/%Y)"), icon_url=bot.data['icon']) 
                await bot.data['message']['embedMessage'].edit(content = None, embed = embed)
        except discord.NotFound:
            async for message in bot.data['channels']['alert'].history():
                await message.delete()
            bot.data['message']['collector'] = set()
            bot.data['message']['updateMessage'] = await bot.data['channels']['alert'].send('```Loading...```')
            bot.data['message']['embedMessage'] = await bot.data['channels']['alert'].send('```Loading...```') 
            bot.data["world_data"].news.needEdit = True     
            bot.data['message']['collector'].add(bot.data['message']['updateMessage'].id)      
            bot.data['message']['collector'].add(bot.data['message']['embedMessage'].id)                  
        except:
            print("Unexpected error:", sys.exc_info())

    @cycleMessage.before_loop
    async def before_cycleMessage():
        bot.data['message'] = {}
        bot.data['message']['collector'] = set() 
        await bot.client.wait_until_ready()
        async for message in bot.data['channels']['alert'].history():
            await message.delete()
        bot.data['message']['updateMessage'] = await bot.data['channels']['alert'].send('```Loading...```')
        bot.data['message']['embedMessage'] = await bot.data['channels']['alert'].send('```Loading...```')
        bot.data['message']['arbyMention'] = await bot.data['channels']['alert'].send('```Loading...```')  
        bot.data['message']['collector'].add(bot.data['message']['updateMessage'].id)      
        bot.data['message']['collector'].add(bot.data['message']['embedMessage'].id) 
        bot.data['message']['collector'].add(bot.data['message']['arbyMention'].id)              

    @tasks.loop(seconds=60.0)
    async def memberCycle():
        for member in bot.data['member_join']:
            if bot.data['roles']['checkedIntro'] in member.roles or bot.data['roles']['VIP'] in member.roles:
                bot.data['member_join'].remove(member)
            elif (datetime.now() - member.joined_at).seconds//60 >= 31 and bot.data['roles']['checkedIntro'] not in member.roles:
                embed = discord.Embed(title="สามารถคลิกที่นี่ เพื่อกลับเข้าสู่ Server อีกครั้ง", 
                description = 'คุณจะถูกนำออกจาก Server เนื่องจากไม่แนะนำตัว ภายใน 30 นาที', 
                url = bot.data['invite'], color=0x00ff00)
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

    @memberCycle.before_loop
    async def before_memberCycle():
        bot.data['members'] = {}
        bot.data['member_join'] = []
        bot.data['ally'] = {}
        bot.data['message_caches'] = {}
        bot.data['logging'] = {}
        bot.data['notification'] = []
        bot.data['announcement'] = Announcement('Notice (Uncle Cat Discord)',
        bot.data['icon'], bot.data['clan'])

        await bot.client.wait_until_ready() 

        bot.data['guild'] = bot.client.get_guild(bot.data['guild'])
        for channel in bot.data['channels']:
            if channel == 'share':
                bot.data['channels'][channel] = Share(bot.client, bot.data['channels'][channel])
            else:
                bot.data['channels'][channel] = bot.client.get_channel(bot.data['channels'][channel])
        for role in bot.data['roles']:
            if role == 'arbitration':
                for arbi in bot.data['roles']['arbitration']:
                    bot.data['roles']['arbitration'][arbi] = discord.utils.get(bot.data['guild'].roles, 
                    id=bot.data['roles']['arbitration'][arbi])
            elif role == 'admins':
                for index, admin in enumerate(bot.data['roles']['admins']):
                    bot.data['roles']['admins'][index] = discord.utils.get(bot.data['guild'].roles, id=admin)  
            elif role == 'notifications':
                for noti in bot.data['roles']['notifications']:
                    noti['role'] = discord.utils.get(bot.data['guild'].roles, 
                id=noti['role'])
                bot.data['notification'].append(Notification(**noti))
            else:
                bot.data['roles'][role] = discord.utils.get(bot.data['guild'].roles, 
                id=bot.data['roles'][role])   

        async for message in bot.data['channels']['ally'].history(limit=None):
            regex = re.compile('[: ]+')
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

        async for message in bot.data['channels']['intro'].history(limit=None):
            regex = re.compile('[: ]+')
            profile = {}
            for line in message.content.split('\n'):
                splitedList = regex.split(line)
                key = get_close_matches(splitedList[0].title(), 
                {'ชื่อ','อายุ','Ign','Clan','Age','Name','Ign(ชื่อในเกม)'})
                if not key:
                    continue
                profile[key[0].replace('(ชื่อในเกม)', 
                '').replace('ชื่อ', 'Name').replace('อายุ', 
                'Age')] = ' '.join(splitedList[1:]).strip() 
            if {'Name', 'Age', 'Ign', 'Clan'}.issubset(profile) and profile['Name'] and profile['Ign']:
                bot.data['members'][message.author.id] = profile

    @tasks.loop(seconds=3600.0)
    async def updateItem():
        try:
            await bot.data['itemCollector'].update()
        except:
            print("Update Failed:", sys.exc_info())        
        
    @updateItem.before_loop
    async def before_updateItem():
        bot.data['itemCollector'] = ItemInfo()
        await bot.client.wait_until_ready()  
        
    @tasks.loop(seconds=3.0)
    async def updateData():
        try:
            await bot.data['world_data'].update()
        except:
            print("Update Failed:", sys.exc_info())
        try:
            await bot.data['build'].update()
        except:
            print("Update Failed:", sys.exc_info())
        
    @updateData.before_loop
    async def before_updateData():       
        bot.data['world_data'] = WorldStat()        
        bot.data['build'] = BuildCollector(bot.data['icon'], bot.data['footer'])
        await bot.client.wait_until_ready()
                     
    updateData.start()
    memberCycle.start()
    updateItem.start()
    cycleMessage.start()
    
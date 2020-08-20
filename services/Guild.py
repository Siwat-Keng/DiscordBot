from asyncio import sleep
from datetime import datetime, timedelta
from discord import Embed, NotFound
from discord.utils import get
from sys import exc_info
from json import dumps
from services.Announcement import Announcement
from services.Share import Share

class Guild:

    def __init__(self, client, guild, data_collector, world_stat, conn, TABLE_NAME):
        self.announcement = Announcement(data_collector[guild.id]['footer'],
        data_collector[guild.id]['icon'], data_collector[guild.id]['clan'])
        self.share = Share(client, data_collector[guild.id]['channels']['share'])
        client.loop.create_task(self.member_cycle(client, data_collector[guild.id], guild, conn, TABLE_NAME))
        client.loop.create_task(self.message_cycle(client, data_collector[guild.id], world_stat))

    async def member_cycle(self, client, dictionary, guild, conn, TABLE_NAME):
        while not (dictionary['channels']['intro'] and dictionary['roles']['waitingIntro']\
            and dictionary['roles']['checkedIntro']):
            if dictionary['channels']['intro']:
                checked = await guild.create_role(name='checked')
                waiting = await guild.create_role(name='waiting')
                dictionary['roles']['checkedIntro'] = checked.id
                dictionary['roles']['waitingIntro'] = waiting.id
                async with conn.cursor() as cursor:
                    sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
                    val = (dumps(dictionary), guild.id)
                    await cursor.execute(sql, val)                   
                    await conn.commit()
                    await cursor.close()  
                    break              
            await sleep(5)
        #TODO
        return

    async def message_cycle(self, client, dictionary, world_stat):
        while not dictionary['channels']['alert']:
            await sleep(5)
        alert_channel = client.get_channel(dictionary['channels']['alert'])
        async for message in alert_channel.history():
            await message.delete()        
        updateMessage = await alert_channel.send('```Loading...```')
        embedMessage = await alert_channel.send('```Loading...```')
        arbyMention = await alert_channel.send('```Loading...```') 
        while dictionary['channels']['alert']:
            alert_channel = client.get_channel(dictionary['channels']['alert'])
            if alert_channel != updateMessage.channel or \
                alert_channel != embedMessage.channel:
                updateMessage = await alert_channel.send('```Loading...```')
                embedMessage = await alert_channel.send('```Loading...```')
                world_stat.news.needEdit = True
            currentTime = (datetime.now() + timedelta(hours=7)).replace(microsecond=0)
            if world_stat.arbitration.needMention:
                try:
                    await arbyMention.delete()
                except:
                    pass
                try:
                    role = get(alert_channel.guild.roles, 
                    id=dictionary['roles']['arbitration'][world_stat.arbitration.getMention()])
                    arbyMention = await alert_channel.send(role.mention)
                except:
                    pass
            try:
                await updateMessage.edit(content = "```css\n{}\n\n{}\n\n{}```".format(world_stat.arbitration, 
                world_stat.timeCycle, world_stat.sentientOutposts))

                if world_stat.news.needEdit:
                    embed = Embed.from_dict(world_stat.news.getDict())
                    embed.set_image(url=world_stat.news.image)
                    embed.set_footer(text='Current Time : ' + currentTime.strftime("%H:%M (%m/%d/%Y)"), icon_url=dictionary['icon']) 
                    await embedMessage.edit(content = None, embed = embed)
            except NotFound:
                async for message in alert_channel.history():
                    await message.delete()
                updateMessage = await alert_channel.send('```Loading...```')
                embedMessage = await alert_channel.send('```Loading...```') 
                world_stat.news.needEdit = True                
            except:
                print('Unexpected error:', exc_info())
            await sleep(5)
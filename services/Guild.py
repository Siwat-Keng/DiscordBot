from asyncio import sleep
from datetime import datetime, timedelta
from discord import Embed, NotFound
from discord.utils import get
from sys import exc_info
from json import dumps
from services.Announcement import Announcement
from services.Share import Share
from services.MemberManager import MemberManager

class Guild:

    def __init__(self, client, guild, data_collector, world_stat, conn, TABLE_NAME):
        self.announcement = Announcement(data_collector[guild.id]['footer'],
        data_collector[guild.id]['icon'], data_collector[guild.id]['clan'])
        self.share = Share(client, data_collector[guild.id]['channels']['share'])
        self.members = MemberManager(data_collector[guild.id])
        self.voice_state = {}
        client.loop.create_task(self.member_cycle(client, data_collector[guild.id], 
        guild, conn, TABLE_NAME))
        client.loop.create_task(self.message_cycle(client, data_collector[guild.id], 
        world_stat, conn, TABLE_NAME))
        client.loop.create_task(self.load_member(client, data_collector[guild.id]))

    async def member_cycle(self, client, dictionary, guild, conn, TABLE_NAME):
        while not (dictionary['channels']['intro'] and dictionary['roles']['waitingIntro'] \
            and dictionary['roles']['checkedIntro'] and dictionary['invite']):
            if dictionary['channels']['intro'] and (not dictionary['roles']['checkedIntro'] \
                or not dictionary['roles']['waitingIntro']):
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
        while dictionary['channels']['intro'] and dictionary['roles']['waitingIntro']\
            and dictionary['roles']['checkedIntro'] and dictionary['invite']:
            waiting_intro = get(guild.roles,
                    id=dictionary['roles']['waitingIntro'])
            checked_intro = get(guild.roles,
                    id=dictionary['roles']['checkedIntro'])
            for member in waiting_intro.members:
                if checked_intro not in member.roles and \
                    (datetime.now() - member.joined_at).seconds//60 >= 31:
                    if dictionary['roles']['VIP'] and \
                        get(guild.roles,
                    id=dictionary['roles']['VIP']) not in \
                        member.roles:
                        embed = Embed(title='สามารถคลิกที่นี่ เพื่อกลับเข้าสู่ Server อีกครั้ง',
                        description = 'คุณจะถูกนำออกจาก Server เนื่องจากไม่แนะนำตัว ภายใน 30 นาที', 
                        url = dictionary['invite'], color=0x00ff00)
                        embed.set_footer(text=dictionary['footer'], icon_url=dictionary['icon'])   
                        try:
                            await member.send(embed=embed)
                        except:
                            pass
                        try:
                            await member.kick(reason = 'ไม่แนะนำตัว')
                        except:
                            pass
            await sleep(60)

    async def message_cycle(self, client, dictionary, world_stat, conn, TABLE_NAME):
        while not dictionary['channels']['alert']:
            await sleep(5)
        alert_channel = client.get_channel(dictionary['channels']['alert'])
        async for message in alert_channel.history():
            await message.delete()
        updateMessage = await alert_channel.send('```Loading...```')
        embedMessage = await alert_channel.send('```Loading...```')
        arbyMention = await alert_channel.send('```Loading...```')
        needMention = True
        prev_mention = None
        while dictionary['channels']['alert']:
            alert_channel = client.get_channel(dictionary['channels']['alert'])
            if alert_channel != updateMessage.channel or \
                alert_channel != embedMessage.channel:
                updateMessage = await alert_channel.send('```Loading...```')
                embedMessage = await alert_channel.send('```Loading...```')
                needMention = True
                prev_mention = None               
            currentTime = (datetime.now() + timedelta(hours=7)).replace(microsecond=0)

            try:
                if prev_mention != world_stat.arbitration.getMention():
                    prev_mention = world_stat.arbitration.getMention()
                    needMention = True
            except:
                needMention = True

            if needMention:
                try:
                    await arbyMention.delete()
                except:
                    pass
                try:
                    role = get(alert_channel.guild.roles,
                    id=dictionary['roles']['arbitration'][world_stat.arbitration.getMention()])
                    if not role:
                        role = await alert_channel.guild.create_role(name=world_stat.arbitration.getMention())
                        dictionary['roles']['arbitration'][world_stat.arbitration.getMention()] = role.id
                        async with conn.cursor() as cursor:
                            sql = 'UPDATE {} SET data = %s WHERE serverID = %s'.format(TABLE_NAME)
                            val = (dumps(dictionary), alert_channel.guild.id)
                            await cursor.execute(sql, val)
                            await conn.commit()
                            await cursor.close()
                    arbyMention = await alert_channel.send(role.mention)
                except:
                    pass
                needMention = False
            try:
                await updateMessage.edit(content = "```css\n{}\n\n{}\n\n{}```".format(world_stat.arbitration, 
                world_stat.timeCycle, world_stat.sentientOutposts))

                embed = Embed.from_dict(world_stat.news.getDict())
                embed.set_image(url=world_stat.news.image)
                embed.set_footer(text='Current Time : ' + currentTime.strftime("%H:%M (%m/%d/%Y)"), icon_url=dictionary['icon'])
                await embedMessage.edit(content = None, embed = embed)

            except NotFound:
                async for message in alert_channel.history():
                    await message.delete()
                needMention = True
                prev_mention = None                   
                updateMessage = await alert_channel.send('```Loading...```')
                embedMessage = await alert_channel.send('```Loading...```')
            except:
                print('Unexpected error:', exc_info())
            await sleep(10)

    async def load_member(self, client, dictionary):
        if dictionary['channels']['intro']:
            intro_channel = client.get_channel(dictionary['channels']['intro'])
            async for message in intro_channel.history(limit=None):
                self.members.collectData(message)
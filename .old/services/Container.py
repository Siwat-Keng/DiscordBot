import discord, re, math, asyncio

class PartyContainer:

    def __init__(self, message, title, leader, footerText, icon):
        self.message = message
        self.channel = message.channel
        self.title = title.strip()
        self.leader = leader
        self.members = {leader.id:leader}
        self.size = 4
        self.footerText = footerText
        self.icon = icon
        if not self.title:
            self.title = 'Unidentified Squad'
        
    async def add_member(self, member):
        if member == self.leader or len(self.members) == self.size:
            return
        self.members[member.id] = member
        embed = discord.Embed(title=self.title, color=0x00ff00)
        value = ''
        for idx, member in enumerate(self.getMembersList()):
            value += '{}. {}\n'.format(idx+1, member)
        embed.add_field(name="Squad Members", 
        value=value.strip(), inline=False)
        embed.add_field(name="Commands", 
        value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
        inline=False)        
        embed.set_footer(text=self.footerText, icon_url=self.icon)        
        await self.message.edit(content=None, embed=embed)
        if len(self.members) == self.size:
            await self.channel.send(self.leader.mention, delete_after = 60)

    async def remove_member(self, member):
        if member != self.leader:
            del self.members[member.id]
            embed = discord.Embed(title=self.title, color=0x00ff00)
            value = ''
            for idx, member in enumerate(self.getMembersList()):
                value += '{}. {}\n'.format(idx+1, member)
            embed.add_field(name="Squad Members", 
            value=value.strip(), inline=False)
            embed.add_field(name="Commands", 
            value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
            inline=False)        
            embed.set_footer(text=self.footerText, icon_url=self.icon)        
            await self.message.edit(content=None, embed=embed)
            return True
        await self.message.delete()
        return False

    async def setMessage(self):
        embed = discord.Embed(title=self.title, color=0x00ff00)
        value = ''
        for idx, member in enumerate(self.getMembersList()):
            value += '{}. {}\n'.format(idx+1, member)
        embed.add_field(name="Squad Members", 
        value=value.strip(), inline=False)
        embed.add_field(name="Commands", 
        value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
        inline=False)       
        embed.set_footer(text=self.footerText, icon_url=self.icon)        
        await self.message.edit(content=None, embed=embed)
        await self.message.add_reaction("👍")
        await self.message.add_reaction("👎")
        await self.message.add_reaction("➕")
        await self.message.add_reaction("➖")
        await self.message.add_reaction("📃")  
        await self.message.add_reaction("🚩")        

    async def refresh(self):
        await self.message.delete()
        embed = discord.Embed(title=self.title, color=0x00ff00)
        value = ''
        for idx, member in enumerate(self.getMembersList()):
            value += '{}. {}\n'.format(idx+1, member)
        embed.add_field(name="Squad Members", 
        value=value.strip(), inline=False)
        embed.add_field(name="Commands", 
        value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
        inline=False)       
        embed.set_footer(text=self.footerText, icon_url=self.icon)        
        self.message = await self.channel.send(embed=embed, delete_after=1800)
        await self.message.add_reaction("👍")
        await self.message.add_reaction("👎")
        await self.message.add_reaction("➕")
        await self.message.add_reaction("➖")
        await self.message.add_reaction("📃")  
        await self.message.add_reaction("🚩")
        return self.message.id

    def getMembersList(self):
        members = ['']*self.size
        for index, member in enumerate(self.members):
            members[index] = self.members[member].display_name
            if index == 0:
                members[index] += ' [Leader]'
        return members

    async def getMemberProfile(self, data):
        embed = discord.Embed(title=self.title, color=0x00ff00)
        for idx, member in enumerate(self.getMembersList()):
            try:
                profile = data[list(self.members.keys())[idx]]
                value = '```Name : {}\nIGN : {}\nAge : {}```'.format(profile['Name'], profile['Ign'], profile['Age'])
            except KeyError:
                await self.channel.send('อย่าลืมไปแนะนำตัวใหม่นะ {}'.format(list(self.members.values())[idx].mention), delete_after=60)
                value = '```Name : -\nIGN : -\nAge : -```'
            except IndexError:
                value = '```Name :\nIGN :\nAge :```'
            embed.add_field(name='{}. {}'.format(idx+1, member), value=value, inline=False)
        embed.set_footer(text=self.footerText, icon_url=self.icon)  
        await self.message.clear_reactions()
        await self.message.edit(content=None, embed=embed)
        await asyncio.sleep(10)
        await self.setMessage()

    async def increaseSize(self):
        if self.size < 8:
            self.size += 1
            embed = discord.Embed(title=self.title, color=0x00ff00)
            value = ''
            for idx, member in enumerate(self.getMembersList()):
                value += '{}. {}\n'.format(idx+1, member)
            embed.add_field(name="Squad Members", 
            value=value.strip(), inline=False)
            embed.add_field(name="Commands", 
            value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
            inline=False)        
            embed.set_footer(text=self.footerText, icon_url=self.icon)        
            await self.message.edit(content=None, embed=embed)

    async def decreaseSize(self):
        if self.size > 2:
            self.size -= 1
            embed = discord.Embed(title=self.title, color=0x00ff00)
            value = ''
            for idx, member in enumerate(self.getMembersList()):
                value += '{}. {}\n'.format(idx+1, member)
            embed.add_field(name="Squad Members", 
            value=value.strip(), inline=False)
            embed.add_field(name="Commands", 
            value='👍 Join Squad\n👎 Leave Squad\n➕ Increase Limit\n➖ Decrease Limit\n📃 Members Detail\n🚩 Refresh Message', 
            inline=False)        
            embed.set_footer(text=self.footerText, icon_url=self.icon)        
            await self.message.edit(content=None, embed=embed)            

class MarketRankContainer:
    
    def __init__(self, market, itemType, message, itemInfo, icon):
        self.market = market
        self.itemName = market['itemName']
        self.currentRank = 0
        self.type = itemType
        self.message = message
        self.itemInfo = itemInfo
        self.icon = icon
        self.currentPage = 1

    async def increaseRank(self):
        if self.market['maxRank'] <= self.currentRank:
            self.currentRank = self.market['maxRank']
            return
        self.currentRank += 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon)  
        await self.message.edit(embed=embed)
                            
    async def decreaseRank(self):
        if self.currentRank <= 0:
            self.currentRank = 0
            return
        self.currentRank -= 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)

    async def nextPage(self):
        if self.currentPage + 1 > math.ceil(len(self.market[self.type][self.currentRank])/5):
            return
        self.currentPage += 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)

    async def prevPage(self):
        if self.currentPage == 1:
            return
        self.currentPage -= 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)

    async def refresh(self):
        self.market = await self.itemInfo.getPrice(self.itemName)       
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)        
    
    async def setMessage(self):
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][self.currentRank])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][self.currentRank][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(content = None, embed=embed)
        await self.message.add_reaction("➕")
        await self.message.add_reaction("➖")      
        await self.message.add_reaction(u"\u25C0")
        await self.message.add_reaction(u"\u25B6")      
        await self.message.add_reaction("🚩")

class MarketContainer:

    def __init__(self, market, itemType, message, itemInfo, icon, footer):
        self.market = market
        self.itemName = market['itemName']
        self.type = itemType        
        self.message = message
        self.itemInfo = itemInfo
        self.icon = icon    
        self.footer = footer
        self.currentPage = 1

    async def nextPage(self):
        if self.currentPage + 1 > math.ceil(len(self.market[self.type][0])/5):
            return
        self.currentPage += 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][0])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][0][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(embed=embed) 

    async def prevPage(self):
        if self.currentPage == 1:
            return
        self.currentPage -= 1
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][0])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][0][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(embed=embed)      

    async def refresh(self):
        self.market = await self.itemInfo.getPrice(self.itemName)        
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][0])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][0][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(embed=embed)        
    
    async def setMessage(self):
        embed = discord.Embed(title="{} {}ers (Page {}/{})".format(self.market['itemName'], self.type.capitalize(), 
        self.currentPage, math.ceil(len(self.market[self.type][0])/5)), url = self.market['url'], color=0x00ff00)
        for item in self.market[self.type][0][5*(self.currentPage-1):5*self.currentPage]:
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(content = None, embed=embed)     
        await self.message.add_reaction(u"\u25C0")
        await self.message.add_reaction(u"\u25B6")        
        await self.message.add_reaction("🚩")

class FissureContainer:

    def __init__(self, message, icon, footer, fissures):      
        self.message = message
        self.fissures = fissures
        self.icon = icon    
        self.footer = footer    
        self.regex = re.compile('\s*\d+[s]')
    
    async def setMessage(self):
        embed = discord.Embed(title="Lith Missions", color=0x00ff00)
        for mission in self.fissures.lith:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)     
        await self.message.add_reaction("🇱")     
        await self.message.add_reaction("🇲")
        await self.message.add_reaction("🇳")
        await self.message.add_reaction("🇦")
        await self.message.add_reaction("🇷")

    async def setLith(self):
        embed = discord.Embed(title="Lith Missions", color=0x00ff00)
        for mission in self.fissures.lith:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)  

    async def setMeso(self):
        embed = discord.Embed(title="Meso Missions", color=0x00ff00)
        for mission in self.fissures.meso:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)        

    async def setNeo(self):
        embed = discord.Embed(title="Neo Missions", color=0x00ff00)
        for mission in self.fissures.neo:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)

    async def setAxi(self):
        embed = discord.Embed(title="Axi Missions", color=0x00ff00)
        for mission in self.fissures.axi:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)

    async def setReq(self):
        embed = discord.Embed(title="Requiem Missions", color=0x00ff00)
        for mission in self.fissures.req:
            embed.add_field(name='Available : {}'.format(self.regex.sub('', mission['eta']))
            , value='[{}] {}'.format(mission['missionType'], 
            mission['node']), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content=None, embed=embed)                        

class AllianceCollector:

    def __init__(self, message, icon, footer, alliance):  
        self.message = message
        self.currentPage = 0
        self.icon = icon
        self.footer = footer
        self.alliance = alliance

    async def nextPage(self):
        if len(self.alliance) <= 25*(self.currentPage+1):
            return
        self.currentPage += 1
        embed = discord.Embed(title='Cat Union Alliance [Page {}]'.format(self.currentPage+1),
        url='https://www.facebook.com/UncleCatTH/photos/a.852290578490513/852290618490509/?type=3&theater',
        color=0x00ff00)
        keys = list(self.alliance)[25*self.currentPage:25*(self.currentPage+1)]
        for clan in keys:
            embed.add_field(name= 'Clan : {}'.format(clan), 
            value='Leader : {}'.format(self.alliance[clan]['Leader']), inline=True)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(embed=embed)

    async def prevPage(self):
        if self.currentPage == 0:
            return
        self.currentPage -= 1
        embed = discord.Embed(title='Cat Union Alliance [Page {}]'.format(self.currentPage+1),
        url='https://www.facebook.com/UncleCatTH/photos/a.852290578490513/852290618490509/?type=3&theater',
        color=0x00ff00)
        keys = list(self.alliance)[25*self.currentPage:25*(self.currentPage+1)]
        for clan in keys:
            embed.add_field(name= 'Clan : {}'.format(clan), 
            value='Leader : {}'.format(self.alliance[clan]['Leader']), inline=True)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.edit(embed=embed)

    async def setMessage(self):
        embed = discord.Embed(title='Cat Union Alliance [Page {}]'.format(self.currentPage+1),
        url='https://www.facebook.com/UncleCatTH/photos/a.852290578490513/852290618490509/?type=3&theater',
        color=0x00ff00)
        keys = list(self.alliance)[25*self.currentPage:25*(self.currentPage+1)]
        for clan in keys:
            embed.add_field(name= 'Clan : {}'.format(clan), 
            value='Leader : {}'.format(self.alliance[clan]['Leader']), inline=True)
        embed.set_footer(text=self.footer, icon_url=self.icon)
        await self.message.add_reaction(u"\u25C0")
        await self.message.add_reaction(u"\u25B6")        
        await self.message.edit(content=None, embed=embed) 
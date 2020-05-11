import discord, concurrent.futures, re

class PartyContainer:

    def __init__(self, message, embed, title, leader):
        self.message = message
        self.embed = embed
        self.channel = message.channel
        self.title = title.title()
        self.leader = leader
        self.members = {leader.id:leader}
        self.intro = None
        self.url = ''
        self.image = ''
        self.footerText = ''
        self.icon = ''
        
    async def add_member(self, member):
        if member == self.leader or len(self.members) == 4:
            return
        self.members[member.id] = member
        members = self.getMembersList()
        embed = discord.Embed(title='{} Squad'.format(self.title), color=0x00ff00)
        embed.add_field(name="Squad Members", 
        value="1. {}\n2. {}\n3. {}\n4. {}\n👍 => Join Squad\n👎 => Leave Squad\n🚩 => Refresh [Host]\n1️⃣2️⃣3️⃣4️⃣ => Search Profile".format(members[0],
        members[1],members[2],members[3]), inline=False)
        embed.set_image(url=self.url)
        embed.set_footer(text=self.footerText, icon_url=self.icon)
        self.embed = embed
        await self.message.edit(embed=embed)
        if len(self.members) == 4:
            await self.channel.send(self.leader.mention, delete_after = 60)

    async def remove_member(self, member):
        if member != self.leader:
            del self.members[member.id]
            members = self.getMembersList()
            embed = discord.Embed(title='{} Squad'.format(self.title), color=0x00ff00)
            embed.add_field(name="Squad Members", 
            value="1. {}\n2. {}\n3. {}\n4. {}\n👍 => Join Squad\n👎 => Leave Squad\n🚩 => Refresh [Host]\n1️⃣2️⃣3️⃣4️⃣ => Search Profile".format(members[0],
            members[1],members[2],members[3]), inline=False)
            embed.set_image(url=self.url)
            embed.set_footer(text=self.footerText, icon_url=self.icon)
            self.embed = embed
            await self.message.edit(embed=embed)
            return True
        await self.message.delete()
        del self
        return False

    async def refresh(self):
        await self.message.delete()
        self.message = await self.channel.send(embed=self.embed, delete_after=1800)
        await self.message.add_reaction("👍")
        await self.message.add_reaction("👎")
        await self.message.add_reaction("1️⃣")
        await self.message.add_reaction("2️⃣")
        await self.message.add_reaction("3️⃣")
        await self.message.add_reaction("4️⃣")   
        await self.message.add_reaction("🚩") 
        return self.message.id

    def setFooterText(self, text):
        self.footerText = text

    def setIcon(self, icon_url):
        self.icon = icon_url

    def setUrl(self, url):
        self.url = url

    def setIntroChannel(self, intro):
        self.intro = intro.mention

    def getMembersList(self):
        members = ['', '', '', '']
        for index, member in enumerate(self.members):
            members[index] = self.members[member].display_name
            if index == 0:
                members[index] += ' [Leader]'
        return members

    async def getMemberProfile(self, data, number):
        try:
            profile = data[list(self.members.keys())[number-1]]
            embed = discord.Embed(title='Member {} [Profile]'.format(number),
            description = 'Name : {}\nAge : {}\nIGN : {}\nClan : {}'.format(profile['Name'],profile['Age'],profile['Ign'],profile['Clan']),
            color=0x00ff00)
            embed.set_footer(text='{} Members in Database'.format(len(data)), icon_url=self.icon)
            await self.channel.send(embed=embed, delete_after=30)
        except KeyError:
            await self.channel.send('อย่าลืมไปแนะนำตัวที่ห้อง {} นะ {}'.format(self.intro ,list(self.members.values())[number-1].mention), delete_after=60)
        except IndexError:
            pass

class MarketRankContainer:
    
    def __init__(self, market, itemType, message, itemInfo, icon):
        self.market = market
        self.itemName = market['itemName']
        self.currentRank = 0
        self.type = itemType
        self.message = message
        self.itemInfo = itemInfo
        self.icon = icon

    async def increaseRank(self):
        if self.market['maxRank'] <= self.currentRank:
            self.currentRank = self.market['maxRank']
            return
        self.currentRank += 1
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][self.currentRank]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)
                            
    async def decreaseRank(self):
        if self.currentRank <= 0:
            self.currentRank = 0
            return
        self.currentRank -= 1
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][self.currentRank]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)

    async def refresh(self):
        self.market = await self.itemInfo.getPrice(self.itemName)       
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][self.currentRank]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(embed=embed)        
    
    async def setMessage(self):
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][self.currentRank]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text="Item Rank : {}".format(self.currentRank), icon_url=self.icon) 
        await self.message.edit(content = None, embed=embed)
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

    async def refresh(self):
        self.market = await self.itemInfo.getPrice(self.itemName)        
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][0]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(embed=embed)        
    
    async def setMessage(self):
        embed = discord.Embed(title="{} {}ers".format(self.market['itemName'], self.type.capitalize()), url = self.market['url'], color=0x00ff00)
        for index, item in enumerate(self.market[self.type][0]):
            if index >= 5:
                break
            embed.add_field(name=item, value=item.getMessage(self.type), inline=False)
        embed.set_footer(text=self.footer, icon_url=self.icon) 
        await self.message.edit(content = None, embed=embed)     
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
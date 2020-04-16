import discord

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

class MarketContainer:
    pass
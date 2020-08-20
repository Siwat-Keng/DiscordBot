from re import compile
from difflib import get_close_matches
from discord import Embed

KEYWORDS = {'ชื่อ','อายุ','Ign','Clan','Age','Name','Ign(ชื่อในเกม)'}
FORMATS = (('(ชื่อในเกม)', ''), ('ชื่อ', 'Name'), ('อายุ', 'Age'))

class MemberManager:

    def __init__(self, containers):
        self.containers = containers
        self.members = {}

    def collectData(self, message):
        content = message.clean_content
        regex = compile('[: ]+')
        profile = {}
        for line in content.split('\n'):
            splitedList = regex.split(line)
            key = get_close_matches(splitedList[0].title(), KEYWORDS
            , 1)
            if key:
                key = key[0]
                for f in FORMATS:
                    key = key.replace(*f)
                profile[key] = ' '.join(splitedList[1:]).strip()
        if len(profile) == 4 and profile['Name'] and profile['Ign']:
            self.members[message.author.id] = profile

    def isIntro(self, message):
        content = message.clean_content
        regex = compile('[: ]+')
        profile = {}
        for line in content.split('\n'):
            splitedList = regex.split(line)
            key = get_close_matches(splitedList[0].title(), KEYWORDS
            , 1)
            if key:
                key = key[0]
                for f in FORMATS:
                    key = key.replace(*f)
                profile[key] = ' '.join(splitedList[1:]).strip()
        if len(profile) == 4 and profile['Name'] and profile['Ign']:
            return True
        return False
    
    def getEmbedded(self, client, member):
        channel = client.get_channel(self.containers['channels']['botcommands'])
        embed = Embed(title='Welcome {}'.format(member.name), 
        description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง {}'.format(channel.name), 
        url = self.containers['url'], color=0x00ff00)
        embed.add_field(name= '{}price <item>'.format(self.containers['prefix']), 
        value='บอทจะ search ราคา item ตามชื่อ (จาก Warframe Market)', inline=False)
        embed.add_field(name= '{}drop <item>'.format(self.containers['prefix']), 
        value='บอทจะ search ตำแหน่งที่ดรอป ตามชื่อ (จาก Warframe Wiki)', inline=False)
        embed.add_field(name= '{}party <message>'.format(self.containers['prefix']), 
        value='บอทจะสร้างข้อความเพื่อหา Squad Member', inline=False)
        embed.add_field(name= '{}fissure'.format(self.containers['prefix']), 
        value='บอทจะแสดง mission void fissure ปัจจุบัน', inline=False)
        embed.add_field(name= '{}build <item>'.format(self.containers['prefix']), 
        value='บอทจะ search build จาก overframe.gg', inline=False)
        embed.add_field(name= '{}riven <weapon> <+stat +stat +stat -stat> <price>'\
            .format(self.containers['prefix']), value='บอทจะ live search riven', inline=False)                     
        embed.set_footer(text=self.containers['footer'], icon_url=self.containers['icon'])
        return embed
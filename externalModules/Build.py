import re, aiohttp, discord
from difflib import get_close_matches

class Build:

    def __init__(self, title, url, stats):
        self.regex = re.compile('^\w+\s*\w+')
        self.name = self.regex.search(title).group().title()
        self.title = title
        self.url = 'https://overframe.gg{}'.format(url)
        self.stats = stats
        self.image = 'https://cdn.overframe.gg/MobileExport/Lotus/Interface/Icons/Store/Primes/{}.png@256x256.webp'.format(self.name.replace(' ',''))

    def __str__(self):
        return 'Name : {}\nTitle : {}\nURL : {}\nStats : {}'.format(self.name, self.title, self.url, self.stats)

    def __repr__(self):
        return 'Name : {}\nTitle : {}\nURL : {}\nStats : {}'.format(self.name, self.title, self.url, self.stats)

class BuildCollector:

    def __init__(self, icon, footer):
        self.collector = []
        self.available = set()
        self.regex = re.compile('^\w+\s*\w+')
        self.base_url = 'https://overframe.gg/api/v1/builds/?author_id=10027&limit=3000&category={}&sort_by=Score'
        self.targets = ['Suits', 'LongGuns', 'Pistols', 'Melee', 'SpaceSuits', 'Sentinels']
        self.icon = icon
        self.footer = footer

    async def update(self):
        async with aiohttp.ClientSession() as session:      
            newCollector = []
            for target in self.targets:
                async with session.get(self.base_url.format(target)) as request:
                    if request.status == 200:
                        js = await request.json()
                        for result in js['results']:
                            newCollector.append(Build(result['title'], result['url'], result['stats']))
                            self.available.add(self.regex.search(result['title']).group().title())
                        self.collector = newCollector
                    else:
                        raise ConnectionError
    
    def getBuild(self, name):
        target = get_close_matches(name, self.available, 1)
        if not target:
            embed = discord.Embed(title='ไม่พบ build [{}]'.format(name), 
            description='กดที่หัวข้อเพื่อติดต่อ Uncle Cat',
            url='https://www.facebook.com/UncleCatTH/', color=0x00ff00)
            embed.set_footer(text=self.footer, icon_url=self.icon)
            return [embed]
        target = target[0]
        target = list(filter(lambda build: build.name == target, self.collector))
        output = []
        for build in target:
            embed = discord.Embed(title=build.title, 
            description='กดที่หัวข้อเพื่อไปยัง Overframe.gg',
            url=build.url, color=0x00ff00)
            embed.set_image(url=build.image)
            embed.set_footer(text=self.footer, icon_url=self.icon)
            output.append(embed)
        return output
from discord import Embed
from difflib import get_close_matches
from aiohttp import ClientSession
from re import compile
from asyncio import sleep

class Build:

    def __init__(self, title, url, stats):
        self.regex = compile('^\w+\s*\w+')
        self.name = self.regex.search(title).group().title()
        self.title = title
        self.url = 'https://overframe.gg{}'.format(url)
        self.stats = stats
        self.image = 'https://cdn.overframe.gg/MobileExport/Lotus/Interface/Icons/Store/Primes/{}.png@256x256.webp'.format(self.name.replace(' ',''))

    def __str__(self):
        return 'Name : {}\nTitle : {}\nURL : {}\nStats : {}'.format(self.name, self.title, self.url, self.stats)

    def __repr__(self):
        return 'Name : {}\nTitle : {}\nURL : {}\nStats : {}'.format(self.name, self.title, self.url, self.stats)

class Builds:

    def __init__(self, client):
        self.collector = []
        self.available = set()
        self.regex = compile('^\w+\s*\w+')
        self.base_url = 'https://overframe.gg/api/v1/builds/?author_id=10027&limit=3000&category={}&sort_by=Score'
        self.targets = ['Suits', 'LongGuns', 'Pistols', 'Melee', 'SpaceSuits', 'Sentinels']
        client.loop.create_task(self.update(client))

    async def update(self, client):
        await client.wait_until_ready() 
        while not client.is_closed():
            async with ClientSession() as session:      
                newCollector = []
                for target in self.targets:
                    async with session.get(self.base_url.format(target)) as request:
                        if request.status == 200:
                            js = await request.json()
                            for result in js['results']:
                                newCollector.append(Build(result['title'], result['url'], result['stats']))
                                self.available.add(self.regex.search(result['title']).group().title())
                            self.collector = newCollector
            await sleep(1800)
    
    def getBuild(self, name, icon, footer):
        target = get_close_matches(name, self.available, 1)
        if not target:
            if not name.endswith(' Prime'):
                return self.getBuild('{} Prime'.format(name), icon, footer)
            else:
                embed = Embed(title='ไม่พบ build ดังกล่าว', 
                description='กดที่หัวข้อเพื่อติดต่อ Uncle Cat',
                url='https://www.facebook.com/UncleCatTH/', color=0x00ff00)
                embed.set_footer(text=footer, icon_url=icon)
                return [embed]
        target = target[0]
        target = list(filter(lambda build: build.name == target, self.collector))
        output = []
        for build in target:
            embed = Embed(title=build.title, 
            description='กดที่หัวข้อเพื่อไปยัง Overframe.gg',
            url=build.url, color=0x00ff00)
            embed.set_image(url=build.image)
            embed.set_footer(text=footer, icon_url=icon)
            output.append(embed)
        return output
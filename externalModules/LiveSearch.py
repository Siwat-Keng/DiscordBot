import discord, asyncio, re, aiohttp

class InvalidSearch(Exception):
    pass

class Stats():

    def __init__(self, target):
        self.regex_name = re.compile('^[^+-]+')
        self.regex_positive = re.compile('[+][^+-0123456789]+')
        self.regex_negative = re.compile('[-][^+-0123456789]+')
        self.regex_price = re.compile('\d+')        
        self.name = self.regex_name.search(target).group().strip()
        self.positive = [pos.strip()[1:] for pos in self.regex_positive.findall(target)]
        self.negative = [neg.strip()[1:] for neg in self.regex_negative.findall(target)]
        self.price = sorted([int(price) for price in self.regex_price.findall(target)])

        if len(self.positive) > 3 or len(self.negative) > 1 or len(self.price) > 2:
            raise InvalidSearch

    def getURL(self):
        url = {}
        url['rv.market'] = 'https://riven.market/list/PC/{}/{}'
        url['wf.market'] = 'https://warframe.market/auctions/search?type=riven&weapon_url_name={}&positive_stats={}'
        #TODO return searchable url
        return url

class Container(): #TODO update embed

    def __init__(self, message):
        pass

    async def next(self):
        pass

    async def prev(self):
        pass

    async def update(self, data):
        pass

class LiveSearch():

    def __init__(self, client, message, target):
        self.client = client
        self.container = Container(message)
        self.target = Stats(target)
        self.client.loop.create_task(self.searchTask())
    
    async def searchTask(self):
        await self.message.add_reaction('❌')
        targetURL = self.target.getURL()
        while not self.client.is_closed():
            fetched = []
            async with aiohttp.ClientSession() as session:
                async with session.get(targetURL['wf.market']) as request:
                    #TODO add data to fetched         
                async with session.get(targetURL['rv.market']) as request:
                    #TODO add data to fetched                         
            try:
                await self.container.update(fetched)
            except discord.NotFound:
                break
            await asyncio.sleep(1)
from difflib import get_close_matches
import aiohttp, discord, asyncio

async def fetch(url, session):
    async with session.get(url) as response:
        content = await response.json()
        return content

class MarketItem():

    def __init__(self, user, name, quantity, price, rank=-1):
        self.user = user
        self.name = name
        self.quantity = quantity
        self.price = int(price)
        self.rank = int(rank)

    def __str__(self):
        if self.rank == -1:
            return 'Quantity : {} | Price : {} platinum.'.format(self.quantity, self.price)
        else:
            return 'Quantity : {} | Price : {} platinum. [ Item Rank : {} ]'.format(self.quantity, self.price, self.rank)

    def __repr__(self):
        if self.rank == -1:
            return 'Quantity : {} | Price : {} platinum.'.format(self.quantity, self.price)
        else:
            return 'Quantity : {} | Price : {} platinum. [ Item Rank : {} ]'.format(self.quantity, self.price, self.rank)

    def __lt__(self, other):
        if self.rank == other.rank:
            return self.price < other.price
        else:
            return self.rank < other.rank

    def __le__(self, other):
        if self.rank == other.rank:
            return self.price <= other.price
        else:
            return self.rank <= other.rank

    def __gt__(self, other):
        if self.rank == other.rank:
            return self.price > other.price
        else:
            return self.rank > other.rank      

    def __eq__(self, other):
        return self.name == other.name and self.price == other.price and self.rank == other.rank and self.user == other.user

    def getMessage(self, type):
        if type == 'sell':
            return "/w {} Hi! I want to buy: {} for {} platinum. (warframe.market)".format(self.user, self.name, self.price)
        return "/w {} Hi! I want to sell: {} for {} platinum. (warframe.market)".format(self.user, self.name, self.price)
        
class ItemInfo():

    def __init__(self):
        self.url = {}
        self.name = {}
        # self.weapons = {}
        # self.warframe = {}
        self.drops = {}

    async def update(self):
        try:
            tasks = []
            async with aiohttp.ClientSession() as session:
                tasks.append(asyncio.create_task(fetch('https://api.warframe.market/v1/items', session)))
                tasks.append(asyncio.create_task(fetch('https://api.warframestat.us/drops', session)))
                # tasks.append(asyncio.create_task(fetch('https://api.warframestat.us/weapons', session)))
                # tasks.append(asyncio.create_task(fetch('https://api.warframestat.us/warframes', session)))
                tasks = await asyncio.gather(*tasks)
                for item in tasks[0]['payload']['items']:
                    self.name[item['url_name']] = item['item_name']
                    self.url[item['item_name']] = item['url_name']
                for item in { item['item'] for item in tasks[1] }:
                    self.drops[item] = list(filter(lambda i: i['item'] == item, tasks[1]))            
                # for weapon in tasks[2]:
                #     self.weapons[weapon['name']] = weapon 
                # for warframe in tasks[3]:
                #     self.warframe[warframe['name']] = warframe
            return True
        except:
            return False        
    
    def toUrl(self, name):
        try:
            return self.url[get_close_matches(name,self.url.keys(),1,0.5)[0]]
        except IndexError:
            raise KeyError

    def toName(self, url):
        try:
            return self.name[get_close_matches(url,self.name.keys(),1,0.5)[0]]
        except IndexError:
            raise KeyError

    def getDropInfo(self, name): 
        try:
            target = get_close_matches(name,self.drops.keys(),1)[0]
            results = self.drops[target]
            embed = discord.Embed(title=target, 
                description='[ Drop Location ]', url='https://api.warframestat.us/drops', color=0x00ff00)
            for location in results:
                embed.add_field(name='Chance : {}%'.format(location['chance']), 
                value='Location : {}'.format(location['place']))
            return embed
        except IndexError:
            raise KeyError

    async def getPrice(self, name):
        output = {}
        output['buy'] = [[] for i in range(11)]
        output['sell'] = [[] for i in range(11)]          
        output['url'] = 'https://warframe.market/items/{}'.format(self.url[name])
        output['itemName'] = name
        maximum = -1
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.warframe.market/v1/items/{}/orders?include=item'.format(self.url[name])) as request:
                if request.status == 200:
                    json = await request.json()
                    json = list(filter(lambda item: item['user']['status'] != 'offline', json['payload']['orders']))
                    for order in json:
                        if(order['order_type'] == 'buy'):
                            if 'mod_rank' in order:
                                output['buy'][order['mod_rank']].append(MarketItem(order['user']['ingame_name'], name, order['quantity'], order['platinum'], order['mod_rank']))
                                if order['mod_rank'] > maximum:
                                    maximum = order['mod_rank']
                            else:
                                output['buy'][0].append(MarketItem(order['user']['ingame_name'], name, order['quantity'], order['platinum']))
                        else:
                            if 'mod_rank' in order:             
                                output['sell'][order['mod_rank']].append(MarketItem(order['user']['ingame_name'], name, order['quantity'], order['platinum'], order['mod_rank']))
                                if order['mod_rank'] > maximum:
                                    maximum = order['mod_rank']                                             
                            else:
                                output['sell'][0].append(MarketItem(order['user']['ingame_name'], name, order['quantity'], order['platinum']))

                    if maximum > -1:
                        output['hasRank'] = True
                    else:
                        output['hasRank'] = False
                    output['maxRank'] = maximum
                    for items in output['buy']:
                        items.sort(reverse=True)
                    for items in output['sell']:
                        items.sort()          
                    return output

                else:
                    raise ConnectionError

    async def getRivenPrice(self, weapon):    
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.warframestat.us/pc/rivens') as request:
                rivens = await request.json()
                result = {}
                for riven in rivens.values():
                    result.update(riven)
                riven = get_close_matches(weapon, result.keys())[0] 
                embed = discord.Embed(title='{} Riven'.format(riven), 
                description='Weekly Riven Price(Official)', url='https://warframe.com/repos/weeklyRivensPC.json', color=0x00ff00)
                embed.add_field(name='Unroll Riven',
                    value='```Price Range : {} - {}\nAverage Price : {}```'.format(result[riven]['unrolled']['min'], 
                    result[riven]['unrolled']['max'], result[riven]['unrolled']['avg']))
                embed.add_field(name='Rolled Riven',
                    value='```Price Range : {} - {}\nAverage Price : {}```'.format(result[riven]['rerolled']['min'], 
                    result[riven]['rerolled']['max'], result[riven]['rerolled']['avg']))                                        
                embed.set_image(url='https://cdn.warframestat.us/img/{}'.format(self.weapons[riven]['imageName']))
                return embed

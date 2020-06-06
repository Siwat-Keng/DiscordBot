from difflib import get_close_matches
import aiohttp, discord

class MarketItem():

    def __init__(self, user, name, quantity, price, rank=-1):
        self.user = user
        self.name = name
        self.quantity = quantity
        self.price = int(price)
        self.rank = int(rank)

    def __str__(self):
        if self.rank == -1:
            return str(self.user) + " : " +str(self.price) + " platinum."
        else:
            return str(self.user) + " : " +str(self.price) + " platinum. [ Item rank : " + str(self.rank) + " ]"

    def __repr__(self):
        if self.rank == -1:
            return str(self.user) + " : " +str(self.price) + " platinum."
        else:
            return str(self.user) + " : " +str(self.price) + " platinum. [ Item rank : " + str(self.rank) + " ]"

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
        return self.name == other.name and self.price == other.price and self.rank == other.rank

    def getMessage(self, type):
        if type == 'sell':
            return "/w {} Hi! I want to buy: {} for {} platinum. (warframe.market)".format(self.user, self.name, self.price)
        return "/w {} Hi! I want to sell: {} for {} platinum. (warframe.market)".format(self.user, self.name, self.price)
        

class KuvaWeapon:

    def __init__(self, ign, name, elemental, bonus, ephemera, price):
        self.ign = ign
        self.name = name
        self.elemental = elemental
        self.bonus = bonus
        self.ephemera = ephemera
        self.price = price

    def __lt__(self, other):
        if self.name == other.name:
            if self.elemental == other.elemental:
                if self.bonus == other.bonus:
                    self.elemental < other.elemental
                else:
                    self.bonus < other.bonus
                return self.price < other.price
            else:
                self.elemental < other.elemental
        else:
            return self.name < other.name

    def __le__(self, other):
        if self.name == other.name:
            if self.elemental == other.elemental:
                if self.bonus == other.bonus:
                    self.elemental <= other.elemental
                else:
                    self.bonus <= other.bonus
                return self.price <= other.price
            else:
                self.elemental <= other.elemental
        else:
            return self.name <= other.name

    def __gt__(self, other):
        if self.name == other.name:
            if self.elemental == other.elemental:
                if self.bonus == other.bonus:
                    self.elemental > other.elemental
                else:
                    self.bonus > other.bonus
                return self.price > other.price
            else:
                self.elemental > other.elemental
        else:
            return self.name > other.name

    def __eq__(self, other):
        return self.name == other.name and self.price == other.price and self.elemental == other.elemental and self.bonus == other.bonus             

    def __str__(self):
        if self.ephemera == '':
            ephemera = 'No'
        else:
            ephemera = 'Yes'
        return "Weapon : " + self.name + " Elemental : " + self.elemental + "(" + self.bonus + ") Ephemera : " + ephemera
        
    def __repr__(self):
        if self.ephemera == '':
            ephemera = 'No'
        else:
            ephemera = 'Yes'        
        return "Weapon : " + self.name + " Elemental : " + self.elemental + "(" + self.bonus + ") Ephemera : " + ephemera

    def getMessage(self):
        if self.ephemera == '':
            ephemera = ' '
        else:
            ephemera = self.ephemera + ' '        
        return "/w "+self.ign+" Hi! I want to buy " + self.name + ' ' + self.elemental + " " + self.bonus + " " + ephemera + "for "+str(self.price)+" platinum.(WarframeTeams.com)"

class ItemInfo():

    def __init__(self):
        self.url = {}
        self.name = {}
        self.weapons = {}
        self.warframe = {}

    async def update(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.warframe.market/v1/items') as request1:
                    if request1.status == 200:
                        items = await request1.json()            
                        for item in items['payload']['items']:
                            self.name[item['url_name']] = item['item_name']
                            self.url[item['item_name']] = item['url_name']
                async with session.get('https://api.warframestat.us/weapons') as request2:
                        if request2.status == 200:
                            weapons = await request2.json()                            
                            for weapon in weapons:
                                self.weapons[weapon['name']] = weapon
                async with session.get('https://api.warframestat.us/warframes') as request3:
                        if request3.status == 200:
                            warframes = await request3.json()                                 
                            for warframe in warframes:
                                self.warframe[warframe['name']] = warframe
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

    async def getInfo(self, name): 
        try:
            targetName = get_close_matches(name,list(self.weapons.keys())+list(self.warframe.keys()),1)[0]
            if targetName in self.weapons:
                embed = discord.Embed(title='[Weapon] {}'.format(targetName), url = self.weapons[targetName]['wikiaUrl'], 
                        description = self.weapons[targetName]['description'], color=0x00ff00)
                for component in self.weapons[targetName]['components']:
                    if '/Lotus/Types/Items/MiscItems/' in component['uniqueName']:
                        continue
                    dropLists = set()
                    try:
                        for drop in component['drops']:
                            dropLists.add(drop['location'].replace('Radiant','Relic').replace('Intact','Relic').replace('Flawless','Relic').replace('Exceptional','Relic'))
                        embed.add_field(name='{} [Drop Location]'.format(component['name']),
                        value=', '.join(dropLists))
                    except KeyError:
                        pass
                embed.set_image(url='https://cdn.warframestat.us/img/{}'.format(self.weapons[targetName]['imageName']))
            else:
                embed = discord.Embed(title='[Warframe] {}'.format(targetName), url = self.warframe[targetName]['wikiaUrl'], 
                        description = self.warframe[targetName]['description'], color=0x00ff00)
                for component in self.warframe[targetName]['components']:
                    if '/Lotus/Types/Items/MiscItems/' in component['uniqueName']:
                        continue
                    try:
                        dropLists = set()
                        for drop in component['drops']:
                            dropLists.add(drop['location'].replace('Radiant','Relic').replace('Intact','Relic').replace('Flawless','Relic').replace('Exceptional','Relic'))
                        embed.add_field(name='{} [Drop Location]'.format(component['name']),
                        value=', '.join(dropLists))
                    except KeyError:
                        pass  
                embed.set_image(url='https://cdn.warframestat.us/img/{}'.format(self.warframe[targetName]['imageName']))
        except IndexError:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.warframe.market/v1/items/' + self.url[self.toName(name)]) as request:
                    if request.status == 200:
                        items = await request.json()    
                        info = items['payload']['item']['items_in_set'][0]['en']        
                        embed = discord.Embed(title=info['item_name'], url = info['wiki_link'], 
                                description = info['description'], color=0x00ff00)
                        for drop in info['drop']:
                            embed.add_field(name= '[ Drop ]', value = drop['name'])  
                    else:
                        raise ConnectionError   
        finally:
            return embed

    async def getPrice(self, name):
        output = {}
        output['buy'] = [[] for i in range(11)]
        output['sell'] = [[] for i in range(11)]          
        output['url'] = 'https://warframe.market/items/{}'.format(self.url[name])
        output['itemName'] = name
        maximum = -1
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://api.warframe.market/v1/items/{}/orders?include=item'.format(self.url[name]))
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
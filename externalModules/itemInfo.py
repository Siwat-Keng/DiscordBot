from bs4 import BeautifulSoup
from difflib import get_close_matches
import aiohttp, discord, json, concurrent.futures

async def loads(text):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(json.loads, text).result()

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
        output['url'] = 'https://warframe.market/items/' + self.url[name]
        output['itemName'] = name
        maximum = -1
        async with aiohttp.ClientSession() as session:
            request = await session.get(output['url'])
            if request.status == 200:
                text = await request.read()
                soup = BeautifulSoup(text, "html.parser").find('script', id='application-state').contents[0]
                json = await loads(soup)
                for order in json['payload']['orders']:
                    if(order['user']['status'] == 'ingame'):
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


    async def getKuvaWeaponPrice(self, name, bonus):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.warframeteams.com/index.php') as request:
                text = await request.read()
                if request.status == 200:
                    text = await request.read()
                    raw_data = BeautifulSoup(text, "html.parser")
                    data = raw_data.find_all('tr')
                    sector_data = raw_data.findAll("div", {"class": "wfmain"})
                    raw_weapon = sector_data[0]
                    raw_bonus = sector_data[1]
                    weapons = []
                    bonuses = []
                    for w in raw_weapon.findAll("form", {"class": "warframesmainform"}):
                        weapons.append(w.find("input")['value'])

                    for w in raw_bonus.findAll("form", {"class": "warframesmainform"}):
                        bonuses.append(w.find("input")['value'])
                    try:
                        weaponName = get_close_matches(name,weapons, 1)[0]
                        elementalName = get_close_matches(bonus,bonuses, 1)[0]
                    except IndexError:
                        weaponName = ''
                        elementalName = ''   
                    try:
                        key = data[0].get_text().strip('\n').split('\n')
                        result = {}
                        for i in data[1:]:
                            info = i.get_text().strip('\n').split('\n')
                            if len(info) != len(key):
                                continue
                            if info[2] not in result and info[1] == 'In game' and info[2] == weaponName and info[3] == elementalName:
                                result[info[2]] = [KuvaWeapon(info[0], info[2], info[3], info[4], info[5], info[6])]
                            elif info[1] == 'In game' and info[2] == weaponName and info[3] == elementalName:
                                result[info[2]].append(KuvaWeapon(info[0], info[2], info[3], info[4], info[5], info[6]))  
                        return (weaponName, sorted(result[weaponName]))
                    except KeyError:
                        return (weaponName, {})

                else:
                    raise ConnectionError
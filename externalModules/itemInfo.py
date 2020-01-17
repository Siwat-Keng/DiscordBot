from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from difflib import SequenceMatcher
import json

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

    def getBuyMessage(self):
        return "/w "+self.user+" Hi! I want to sell: "+self.name+" for "+str(self.price)+" platinum. (warframe.market)"

    def getSellMessage(self):
        return "/w "+self.user+" Hi! I want to buy: "+self.name+" for "+str(self.price)+" platinum. (warframe.market)"

class Item():

    def __init__(self, name, description, wikiaUrl, image=None, drops=None):
        self.name = name
        self.description = description
        self.wikiaUrl = wikiaUrl
        if image == None:
            self.image = image
        else:
            self.image = 'https://cdn.warframestat.us/img/'+image
        self.drops = drops

class Weapon(Item):

    def __init__(self, weaponDict):
        super().__init__(weaponDict['name'], weaponDict['description'], weaponDict['wikiaUrl'], image = weaponDict['imageName'])
        # self.



class ItemInfo():

    def __init__(self):
        self.weapons = set()
        self.items = {}
        self.url = {}
        self.name = {}

    def update(self):
        try:
            self.items = json.loads(str(BeautifulSoup(urlopen(Request('http://api.warframe.market/v1/items' ,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 'html.parser')))['payload']['items']
            for item in self.items:
                self.name[item['url_name']] = item['item_name']
                self.url[item['item_name']] = item['url_name']

            target = str(BeautifulSoup(urlopen(Request('https://www.warframe.com/repos/weeklyRivensPC.json', 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})), 
            'html.parser'))
            target =json.loads(target[:target.rfind(']')+1])
            temp = set()
            for weapon in target:
                try:
                    temp.add(weapon['compatibility'].lower().replace('<archwing>','').strip())
                except:
                    pass
            self.weapons = temp

            return True
        except:
            return False        
    
    def toUrl(self, name):
        maximum = 0
        itemName = ''
        for item in self.url:
            ratio = SequenceMatcher(None,name.lower(),item).ratio()
            if ratio > maximum:
                maximum = ratio
                itemName = item
        return self.url[itemName]

    def toName(self, url):
        itemMax = 0
        weaponMax = 0
        itemUrl = ''
        weapon = ''
        for item in self.name:
            ratio = SequenceMatcher(None,url.lower(),item).ratio()
            if ratio > itemMax:
                itemMax = ratio
                itemUrl = item 
        for item in self.weapons:
            ratio = SequenceMatcher(None,url.lower(),item).ratio()
            if ratio > weaponMax:
                weaponMax = ratio
                weapon = item
        if weaponMax > itemMax:
            return weapon       
        return self.name[itemUrl]

    def getInfo(self, name):
        s = str(BeautifulSoup(urlopen(Request('https://api.warframestat.us/items/search/' + name.lower().replace('(veiled)','').replace('set','').strip().replace(' ','%20'), 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 
        'html.parser'))
        info = json.loads(s[:s.rfind(']')+1])
        try:
            return info[0]
        except IndexError:
            info = json.loads(str(BeautifulSoup(urlopen(Request('https://api.warframe.market/v1/items/' + self.url[name], 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 
            'html.parser')))['payload']['item']['items_in_set']
            for item in info:
                if item['en']['item_name'] == name:
                    temp = item['en']
            info = {'name':temp['item_name'], 'description':temp['description'], 'wikiaUrl':temp['wiki_link'], 'drop':temp['drops']}
            return info


    def getPrice(self, name):
        output = {}
        output['buy'] = [[] for i in range(11)]
        output['sell'] = [[] for i in range(11)]          
        output['url'] = 'https://warframe.market/items/' + self.url[name]
        output['itemName'] = name
        maximum = -1

        for order in json.loads(BeautifulSoup(urlopen(Request(output['url'] ,
                                                            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 
                                                            'html.parser').find('script', id='application-state').contents[0])['payload']['orders']:
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

a = ItemInfo()
a.update()
data = a.getInfo(a.toName("kogake prime"))
for i in data:
    print(i)
print(data['imageName'])
print(data['name'])
# print(a.getInfo(a.toName("pennant"))['components'])

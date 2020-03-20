from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import requests, urllib.request, json

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
        self.collector = []
        self.url = {}
        self.name = {}

    def update(self):
        try:
            self.collector = json.loads(requests.get('https://api.warframe.market/v1/items').text)['payload']['items']
            for item in self.collector:
                self.name[item['url_name']] = item['item_name']
                self.url[item['item_name']] = item['url_name']
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
        maximum = 0
        itemUrl = ''
        for item in self.name:
            ratio = SequenceMatcher(None,url.lower(),item).ratio()
            if ratio > maximum:
                maximum = ratio
                itemUrl = item        
        return self.name[itemUrl]

    def getInfo(self, name): 
        info = json.loads(requests.get('https://api.warframe.market/v1/items/' + self.url[name]).text)['payload']['item']['items_in_set']
        for item in info:
            if item['en']['item_name'] == name:
                return item['en']

    def getPrice(self, name):
        output = {}
        output['buy'] = [[] for i in range(11)]
        output['sell'] = [[] for i in range(11)]          
        output['url'] = 'https://warframe.market/items/' + self.url[name]
        output['itemName'] = name
        maximum = -1

        for order in json.loads(BeautifulSoup(requests.get(output['url']).text, "html.parser").find('script', 
        id='application-state').contents[0])['payload']['orders']:
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

    def getKuvaWeaponPrice(self, name):
        data = BeautifulSoup(requests.get('https://www.warframeteams.com/index.php').text, "html.parser").find_all('tr')
        key = data[0].get_text().strip('\n').split('\n')
        result = {}
        for i in data[1:]:
            info = i.get_text().strip('\n').split('\n')
            if len(info) != len(key):
                continue
            if info[2] not in result and info[1] == 'In game':
                result[info[2]] = [KuvaWeapon(info[0], info[2], info[3], info[4], info[5], info[6])]
            elif info[1] == 'In game':
                result[info[2]].append(KuvaWeapon(info[0], info[2], info[3], info[4], info[5], info[6]))

        maximum = 0
        weaponName = ''
        for item in result:
            ratio = SequenceMatcher(None,name.lower(),item.lower()).ratio()
            if ratio > maximum:
                maximum = ratio
                weaponName = item    

        return (weaponName, sorted(result[weaponName]))
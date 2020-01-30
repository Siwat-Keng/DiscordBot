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

class ItemInfo():

    def __init__(self):
        self.collector = []
        self.url = {}
        self.name = {}

    def update(self):
        try:
            self.collector = json.loads(str(BeautifulSoup(urlopen(Request('http://api.warframe.market/v1/items' ,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 'html.parser')))['payload']['items']
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
        info = json.loads(str(BeautifulSoup(urlopen(Request('https://api.warframe.market/v1/items/' + self.url[name], 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})).read(), 
        'html.parser')))['payload']['item']['items_in_set']
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
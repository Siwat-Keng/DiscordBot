import discord, asyncio, re, aiohttp, json
from difflib import get_close_matches
from datetime import datetime
from bs4 import BeautifulSoup

def hasNegative(riven):
    for att in riven['item']['attributes']:
        if not att['positive']:
            return True
    return False

class InvalidSearch(Exception):
    pass

class Stats():

    def __init__(self, target, weapons):
        with open('stats.json', 'r') as statsFile:
            self.params = json.load(statsFile)
        with open('outstats.json', 'r') as translator:
            self.translator = json.load(translator)
        self.regex_name = re.compile('^[^+-]+')
        self.regex_positive = re.compile('[+][^+-0123456789]+')
        self.regex_negative = re.compile('[-][^+-0123456789]+')
        self.regex_price = re.compile('\d+')
        try:
            self.name = get_close_matches(self.regex_name.search(target).group().strip(), weapons)[0].title()
        except AttributeError:
            self.name = ''
        if self.name.replace('Prime', '').strip() in weapons:
            self.name = self.name.replace('Prime', '').strip()
        if self.name.replace('Kuva', '').strip() in weapons:
            self.name = self.name.replace('Kuva', '').strip()
        if self.name.replace('Vandal', '').strip() in weapons:
            self.name = self.name.replace('Vandal', '').strip()
        if self.name.replace('Wraith', '').strip() in weapons:
            self.name = self.name.replace('Wraith', '').strip()
        self.positive = [self.params[get_close_matches(pos.strip()[1:].lower(), self.params.keys())[0]] for pos in self.regex_positive.findall(target)]
        self.negative = [self.params[get_close_matches(neg.strip()[1:].lower(), self.params.keys())[0]] for neg in self.regex_negative.findall(target)]
        self.price = sorted([int(price) for price in self.regex_price.findall(target)])

        if len(self.negative) == 0:
            self.negative = ['all']

        self.positive = list(set(self.positive)-{'all', 'None', 'Any'})

        if len(self.positive) > 3 or len(self.negative) > 1 or len(self.price) > 2 or len(self.positive) == 0:
            raise InvalidSearch

    def getURL(self):
        url = {}
        url['rv.market'] = 'https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=500&recency=-1&veiled=false&onlinefirst=true&polarity=all&rank=all&mastery=16&weapon={}&stats={}&neg={}&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time={}'.format(self.name.replace(' ','_'), 
        ','.join(self.positive), self.negative[0], str(datetime.now().timestamp()).replace('.','')[:13])
        positive = '&positive_stats={}'.format(','.join([self.translator[pos].replace(' ','_').lower() for pos in self.positive if pos.strip() != '']))
        negative = ''
        if self.negative == ['None']:
            negative = '&negative_stats=none'
        elif self.negative != ['Any'] and self.negative != ['all']:
            negative = '&negative_stats={}'.format(self.translator[self.negative[0]]).replace(' ','_').lower()
        url['wf.market'] = 'https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name={}{}{}'.format(self.name.replace(' ','_').lower()
        , positive, negative)
        url['wf.market'] = url['wf.market'].replace('initial_combo', 'channeling_damage')
        url['wf.market'] = url['wf.market'].replace('melee_combo_efficiency', 'channeling_efficiency')
        if self.name == '':
            url['rv.market'] = url['rv.market'].replace('&weapon=', '&weapon=Any')
            url['wf.market'] = url['wf.market'].replace('&weapon_url_name=', '')
        return url

    def getPriceRange(self):
        if len(self.price) == 0:
            return None
        elif len(self.price) == 1:
            return range(self.price[0]+1)
        else:
            return range(self.price[0], self.price[1]+1)

    def get_positive(self, number):
        try:
            return self.positive[number]
        except IndexError:
            return 'all'

class Container():

    def __init__(self, message, stats, footer, icon, owner, weapon):
        with open('outstats.json', 'r') as statsFile:
            self.result = json.load(statsFile)
        self.message = message
        self.stats = stats
        self.data = []
        self.currentPage = 0
        self.footer = footer
        self.icon = icon
        self.counter = 0
        self.owner = owner
        self.weapon = weapon
      
    async def next(self):
        if not self.data or len(self.data) - 1 == self.currentPage:
            return
        self.currentPage += 1
        if self.data:
            price = str(self.data[self.currentPage].price).replace('Platinum', '')
            if 'Top Bid' in price:
                price = '????'
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.data[self.currentPage].weapon, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on {}.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].location, price),color=0x00ff00)
            embed.add_field(name= 'Price : {}'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], 
            self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            try:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)
                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False) 
            except AttributeError:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False)      

                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                embed.add_field(name= 'Commands', 
                value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                , inline=False)      
            embed.set_footer(text=self.footer, icon_url=self.icon)
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
            await self.message.edit(content=None, embed=embed)

    async def prev(self):
        if not self.data or self.currentPage == 0:
            return
        self.currentPage -= 1
        if self.data:
            price = str(self.data[self.currentPage].price).replace('Platinum', '')
            if 'Top Bid' in price:
                price = '????'
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.data[self.currentPage].weapon, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on {}.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].location, price),color=0x00ff00)
            embed.add_field(name= 'Price : {}'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], 
            self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            try:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)
                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False) 
            except AttributeError:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False)      

                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False)      
            embed.set_footer(text=self.footer, icon_url=self.icon)
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
            await self.message.edit(content=None, embed=embed) 

    async def update(self, data):
        newRiven = [riven for riven in data if riven not in self.data]
        if self.data == data and self.data:
            return
        elif newRiven:
            self.data = data
            await self.message.channel.send(self.owner.mention, delete_after=3)
        else:
            self.data = data

        if self.data:
            price = str(self.data[self.currentPage].price).replace('Platinum', '')
            if 'Top Bid' in price:
                price = '????'
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.data[self.currentPage].weapon, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on {}.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].location, price),color=0x00ff00)
            embed.add_field(name= 'Price : {}'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], 
            self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            try:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)
                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], self.stats.getPriceRange().start,
                        self.stats.getPriceRange().stop-1), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False) 
            except AttributeError:
                try:
                    embed = discord.Embed(title="{} Riven".format(self.data[self.currentPage].weapon), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False)      

                except IndexError:
                    embed = discord.Embed(title="{} Riven".format(self.weapon).strip(), 
                        description = "Keep Searching{}\n```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nPrice Range : {} - {} Platinum```"
                        .format('.'*self.counter, self.result[self.stats.positive[0]], self.result[self.stats.positive[1]], 
                        self.result[self.stats.get_positive(2)], self.result[self.stats.negative[0]], 0, "Infinity"), color=0x00ff00)    
                    embed.add_field(name= 'Commands', 
                    value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
                    , inline=False)      
            embed.set_footer(text=self.footer, icon_url=self.icon)
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
            await self.message.edit(content=None, embed=embed)

class Riven():

    def __init__(self, name, polarity, price, rank, reroll, mr, pos, neg, seller, location, weapon):
        with open('outstats.json', 'r') as statsFile:
            self.result = json.load(statsFile)       
        self.name = name
        self.polarity = polarity
        self.price = price
        self.rank = rank
        self.reroll = reroll
        self.mr = mr
        self.weapon = weapon
        if location == 'Riven':
            self.pos = ['+{} {}'.format(s[1], self.result[s[0]]) for s in pos if float(s[1]) != 0]
            try:
                self.neg = '-{} {}'.format(neg[0][1], self.result[neg[0][0]])
                if float(neg[0][1]) == 0:
                    self.neg = 'None'      
            except KeyError:
                self.neg = 'None'    
        else:
            self.pos = ['+{} {}'.format(s[1], s[0]) for s in pos if float(s[1]) != 0]
            try:
                self.neg = '-{} {}'.format(neg[0][1], neg[0][0])
            except IndexError:
                self.neg = 'None'
        self.seller = seller
        self.location = location
        self.neg = self.neg.replace('Channeling Efficiency', 'Melee Combo Efficiency')
        if 'Recoil' in self.neg:
            self.neg = self.neg.replace('-', '+')        
        for index in range(len(self.pos)):
            if 'Recoil' in self.pos[index]:
                self.pos[index] = self.pos[index].replace('+', '-')
            self.pos[index] = self.pos[index].replace('Channeling Damage', 'Initial Combo')
            self.pos[index] = self.pos[index].replace('Channeling Efficiency', 'Melee Combo Efficiency')
        while len(self.pos) < 3:
            self.pos.append('None')

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return '{} {} {} {} {} {} {} {} {} {}'.format(self.name, self.polarity, self.price, self.rank, self.reroll, self.mr,
        self.pos, self.neg, self.seller, self.location)

class LiveSearch():

    def __init__(self, client, message, target, footer, icon, weapons, author):
        self.client = client
        self.owner = author
        self.target = Stats(target, weapons)      
        self.container = Container(message, self.target, footer, icon, author, self.target.name)
        self.searching = True
        self.client.loop.create_task(self.searchTask(message))

    
    async def searchTask(self, message):
        await message.add_reaction(u"\u25C0")
        await message.add_reaction(u"\u25B6")        
        await message.add_reaction('❌')     
        targetURL = self.target.getURL()
        while self.searching:
            fetched = []
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(targetURL['wf.market']) as request:
                        if request.status == 200:
                            json = await request.json()
                            rivens = list(filter(lambda riven: riven['owner']['status'] != 'offline', json['payload']['auctions']))  
                            if self.target.negative == ['Any']:
                                rivens = list(filter(lambda riven: hasNegative(riven), rivens))
                            for riven in rivens:
                                positive = []
                                negative = []
                                for att in riven['item']['attributes']:
                                    if att['positive']:
                                        positive.append((att['url_name'].replace('_', ' ').title(), att['value']))
                                    else:
                                        negative.append((att['url_name'].replace('_', ' ').title(), str(att['value']).replace('-','')))
                                positive = positive + [('', 0)]*(3-len(positive))
                                if riven['is_direct_sell']:
                                    if self.target.getPriceRange() and int(riven['starting_price']) not in self.target.getPriceRange():
                                        continue                            
                                    fetched.append(Riven('{} {}'.format(riven['item']['weapon_url_name'].replace('_', ' ').title(), 
                                    riven['item']['name'].capitalize()), riven['item']['polarity'], '{} Platinum'.format(riven['starting_price']), 
                                    riven['item']['mod_rank'], riven['item']['re_rolls'], riven['item']['mastery_level'], 
                                    positive, negative, riven['owner']['ingame_name'], 'warframe', riven['item']['weapon_url_name'].replace('_', ' ').title()))
                                else:
                                    if riven['top_bid'] and self.target.getPriceRange() and riven['top_bid']+1 in self.target.getPriceRange():
                                        price = '\nStarting : {} Platinum\nTop Bid : {} Platinum\nBuy Out : {} Platinum'.format(riven['starting_price'],
                                        riven['top_bid'], str(riven['buyout_price']).replace('None', 'Infinity'))
                                        fetched.append(Riven('{} {}'.format(riven['item']['weapon_url_name'].replace('_', ' ').title(), 
                                        riven['item']['name'].capitalize()), riven['item']['polarity'], price, 
                                        riven['item']['mod_rank'], riven['item']['re_rolls'], riven['item']['mastery_level'], 
                                        positive, negative, riven['owner']['ingame_name'], 'warframe', riven['item']['weapon_url_name'].replace('_', ' ').title()))
                                    elif not riven['top_bid'] and self.target.getPriceRange() and riven['starting_price'] in self.target.getPriceRange():
                                        price = '\nStarting : {} Platinum\nTop Bid : {}\nBuy Out : {} Platinum'.format(riven['starting_price'],
                                        None, str(riven['buyout_price']).replace('None', 'Infinity'))
                                        fetched.append(Riven('{} {}'.format(riven['item']['weapon_url_name'].replace('_', ' ').title(), 
                                        riven['item']['name'].capitalize()), riven['item']['polarity'], price, 
                                        riven['item']['mod_rank'], riven['item']['re_rolls'], riven['item']['mastery_level'], 
                                        positive, negative, riven['owner']['ingame_name'], 'warframe', riven['item']['weapon_url_name'].replace('_', ' ').title()))
                                    elif not self.target.getPriceRange():
                                        price = '\nStarting : {} Platinum\nTop Bid : {} Platinum\nBuy Out : {} Platinum'.format(riven['starting_price'],
                                        riven['top_bid'], str(riven['buyout_price']).replace('None', 'Infinity'))
                                        fetched.append(Riven('{} {}'.format(riven['item']['weapon_url_name'].replace('_', ' ').title(), 
                                        riven['item']['name'].capitalize()), riven['item']['polarity'], price, 
                                        riven['item']['mod_rank'], riven['item']['re_rolls'], riven['item']['mastery_level'], 
                                        positive, negative, riven['owner']['ingame_name'], 'warframe', riven['item']['weapon_url_name'].replace('_', ' ').title()))   

                        elif request.status == 400:
                            await self.owner.send('```Error[log]\nURL : {}\nกรุณาส่ง URL ให้ Admin```'.format(targetURL['wf.market']))
                            await self.container.message.delete()
                            break

                        else:
                            print('warframe.market status : {}'.format(request.status))

                    async with session.get(targetURL['rv.market']) as request:   
                        if request.status == 200:
                            text = await request.read()  
                            soup = BeautifulSoup(text, "html.parser")  
                            for riven in soup.find_all("div", {"class": "riven"}):
                                if riven.find_all("div", {"class": "attribute online offline"}):
                                    break    
                                if self.target.getPriceRange() and int(riven['data-price']) not in self.target.getPriceRange():
                                    continue
                                try:
                                    fetched.append(Riven('{} {}'.format(riven['data-weapon'].replace('_', ' '), riven['data-name']),
                                    riven['data-polarity'], '{} Platinum'.format(riven['data-price']), riven['data-rank'], riven['data-rerolls'],
                                    riven['data-mr'], [
                                        (riven['data-stat1'], riven['data-stat1val']),
                                        (riven['data-stat2'], riven['data-stat2val']),
                                        (riven['data-stat3'], riven['data-stat3val'])
                                    ], [
                                        (riven['data-stat4'], riven['data-stat4val'])
                                    ], riven.find_all("div", {"class": "attribute seller"})[0].text.strip(),
                                    'Riven', riven['data-weapon'].replace('_', ' ')))
                                except IndexError:
                                    fetched.append(Riven('{} {}'.format(riven['data-weapon'].replace('_', ' '), riven['data-name']),
                                    riven['data-polarity'], '{} Platinum'.format(riven['data-price']), riven['data-rank'], riven['data-rerolls'],
                                    riven['data-mr'], [
                                        (riven['data-stat1'], riven['data-stat1val']),
                                        (riven['data-stat2'], riven['data-stat2val']),
                                        (riven['data-stat3'], riven['data-stat3val'])
                                    ], [
                                        (riven['data-stat4'], riven['data-stat4val'])
                                    ], riven.find_all("div", {"class": "attribute seller patreon-badge"})[0].text.strip(),
                                    'Riven', riven['data-weapon'].replace('_', ' ')))   
                        else:
                            print('riven.market status : {}'.format(request.status))
                await self.container.update(fetched)
                await asyncio.sleep(3)
            except discord.NotFound:
                self.searching = False
            except Exception as err:
                print('searchTask Exception : {}'.format(err))
            
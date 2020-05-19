class InvalidSearch(Exception):
    pass

class Stats():

    def __init__(self, target, weapons):
        self.params = ['Multi', 'Damage', 'CritDmg', 'Speed', 'Corpus', 'Grineer', 'Infested', 'Impact', 'Puncture', 
'Slash', 'Cold', 'Electric', 'Heat', 'Toxin', 'ChannelDmg', 'ChannelEff', 'Combo', 'CritChance', 
'Slide', 'Finisher', 'Flight', 'Ammo', 'Magazine', 'Punch', 'Reload', 'Range', 'StatusC', 'StatusD', 
'Recoil', 'Zoom', 'InitC', 'ComboEfficiency', 'ComboGainExtra', 'ComboGainLost']
        self.regex_name = re.compile('^[^+-]+')
        self.regex_positive = re.compile('[+][^+-0123456789]+')
        self.regex_negative = re.compile('[-][^+-0123456789]+')
        self.regex_price = re.compile('\d+')        
        self.name = get_close_matches(self.regex_name.search(target).group().strip(), weapons)[0].replace(' ','_').title()
        self.positive = [get_close_matches(pos.strip()[1:], self.params)[0] for pos in self.regex_positive.findall(target)]
        self.negative = [get_close_matches(neg.strip()[1:], self.params)[0] for neg in self.regex_negative.findall(target)]
        self.price = sorted([int(price) for price in self.regex_price.findall(target)])

        if len(self.negative) == 0:
            self.negative = ['all']

        if len(self.positive) > 3 or len(self.negative) > 1 or len(self.price) > 2:
            raise InvalidSearch

    def getURL(self):
        url = {}
        url['rv.market'] = 'https://riven.market/_modules/riven/showrivens.php?baseurl=Lw==&platform=PC&limit=200&recency=-1&veiled=false&onlinefirst=true&polarity=all&rank=all&mastery=16&weapon={}&stats={}&neg={}&price=99999&rerolls=-1&sort=time&direction=ASC&page=1&time={}'.format(self.name, ','.join(self.positive), self.negative[0], str(datetime.now().timestamp()).replace('.','')[:13])
        url['wf.market'] = 'https://warframe.market/auctions/search?type=riven&weapon_url_name={}&positive_stats={}'
        #TODO return searchable wf.market url
        return url

    def getPriceRange(self):
        if len(self.price) == 0:
            return None
        elif len(self.price) == 1:
            return range(self.price[0])
        else:
            return range(self.price[0], self.price[1]+1)

class Container():

    def __init__(self, message, stats, footer, icon):
        self.message = message
        self.stats = stats
        self.data = None
        self.currentPage = 0
        self.footer = footer
        self.icon = icon
        self.counter = 0

    async def next(self):
        if not self.data or len(self.data) - 1 == self.currentPage:
            return
        self.currentPage += 1
        if self.data:
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.stats.name, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on Riven.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].price),color=0x00ff00)
            embed.add_field(name= 'Price : {} Platinum'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            embed = discord.Embed(title="{} Riven".format(self.stats.name), 
            description = "Keep Searching{}".format('.'*self.counter),color=0x00ff00)
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
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.stats.name, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on Riven.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].price),color=0x00ff00)
            embed.add_field(name= 'Price : {} Platinum'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            embed = discord.Embed(title="{} Riven".format(self.stats.name), 
            description = "Keep Searching{}".format('.'*self.counter),color=0x00ff00)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)             
            embed.set_footer(text=self.footer, icon_url=self.icon)
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
            await self.message.edit(content=None, embed=embed)        

    async def update(self, data):
        self.data = data
        if self.currentPage >= len(self.data):
            self.currentPage = len(self.data) - 1
        elif self.currentPage < 0:
            self.currentPage = 0
        if self.data:
            embed = discord.Embed(title="{} Riven (Page {}/{})".format(self.stats.name, self.currentPage+1, len(self.data)), 
            description = "/w {} Hey! I'd like to buy the {} Riven that you sell on Riven.market for {} Platinum!".format(self.data[self.currentPage].seller,
            self.data[self.currentPage].name, self.data[self.currentPage].price),color=0x00ff00)
            embed.add_field(name= 'Price : {} Platinum'.format(self.data[self.currentPage].price), 
            value='```Positive 1 : {}\nPositive 2 : {}\nPositive 3 : {}\nNegative   : {}\nMod Rank : {}\tPolarity : {}\nMastery Rank : {}\tReroll : {}```'
            .format(self.data[self.currentPage].pos[0], self.data[self.currentPage].pos[1], self.data[self.currentPage].pos[2],
            self.data[self.currentPage].neg, self.data[self.currentPage].rank, self.data[self.currentPage].polarity,
            self.data[self.currentPage].mr, self.data[self.currentPage].reroll), inline=False)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)            
            embed.set_footer(text=self.footer, icon_url=self.icon)
            await self.message.edit(content=None, embed=embed)
        else:
            embed = discord.Embed(title="{} Riven".format(self.stats.name), 
            description = "Keep Searching{}".format('.'*self.counter),color=0x00ff00)
            embed.add_field(name= 'Commands', 
            value='❌ For cancel searching\n\u25C0 Go to prevous page\n\u25B6 Go to next page'
            , inline=False)             
            embed.set_footer(text=self.footer, icon_url=self.icon)
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
            await self.message.edit(content=None, embed=embed)

class Riven():

    def __init__(self, name, polarity, price, rank, reroll, mr, pos, neg, seller):
        self.name = name
        self.polarity = polarity
        self.price = price
        self.rank = rank
        self.reroll = reroll
        self.mr = mr
        self.pos = ['{} +{}'.format(s[0], s[1]) for s in pos if float(s[1]) != 0]
        self.neg = '{} -{}'.format(neg[0][0], neg[0][1])
        self.seller = seller

        if float(neg[0][1]) == 0:
            self.neg = 'None'

        while len(self.pos) < 3:
            self.pos.append('None')

class LiveSearch():

    def __init__(self, client, message, target, footer, icon, weapons):
        self.client = client
        self.target = Stats(target, weapons)      
        self.container = Container(message, self.target, footer, icon)
        self.client.loop.create_task(self.searchTask(message))
    
    async def searchTask(self, message):
        await message.add_reaction(u"\u25C0")
        await message.add_reaction(u"\u25B6")        
        await message.add_reaction('❌')     
        targetURL = self.target.getURL()
        while not self.client.is_closed():
            fetched = []
            async with aiohttp.ClientSession() as session:
                # async with session.get(targetURL['wf.market']) as request:
                    #TODO add data to fetched         
                async with session.get(targetURL['rv.market']) as request:   
                    text = await request.read()  
                    soup = BeautifulSoup(text, "html.parser")  
                    for riven in soup.find_all("div", {"id": "riven-list"})[0].find_all("div", {"class": "riven"}):
                        if riven.find_all("div", {"class": "attribute online offline"}):
                            break    
                        if self.target.getPriceRange() and int(riven['data-price']) not in self.target.getPriceRange():
                            continue
                        fetched.append(Riven('{} {}'.format(riven['data-weapon'], riven['data-name']),
                        riven['data-polarity'], riven['data-price'], riven['data-rank'], riven['data-rerolls'],
                        riven['data-mr'], [
                            (riven['data-stat1'], riven['data-stat1val']),
                            (riven['data-stat2'], riven['data-stat2val']),
                            (riven['data-stat3'], riven['data-stat3val'])
                        ], [
                            (riven['data-stat4'], riven['data-stat4val'])
                        ], riven.find_all("div", {"class": "attribute seller"})[0].text.strip()))
            try:
                await self.container.update(fetched)
            except discord.NotFound:
                break
            await asyncio.sleep(1)
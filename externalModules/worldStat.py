from datetime import datetime, timedelta
from difflib import get_close_matches
import aiohttp, re

class UpdateErrorException(Exception):
    pass

class SentientAnomaly:

    def __init__(self):
        self.currentMission = None
        self.remainingTime = None
        self.counter = None
        self.firstUpdate = True
                
    def update(self, data):
        currentTime = datetime.now().replace(microsecond=0)

        try:
            if self.firstUpdate and self.currentMission != None and self.currentMission != data['mission']['node']:
                self.firstUpdate = False
                
            if self.currentMission != data['mission']['node']:
                self.currentMission = data['mission']['node']
                self.counter = currentTime + timedelta(minutes=30)
                self.remainingTime = "{} minutes".format((self.counter - currentTime).seconds//60)
            else:
                self.remainingTime = "{} minutes".format((self.counter - currentTime).seconds//60)
                if (self.counter - currentTime).seconds//60 <= 0:
                    self.remainingTime = "<1 minute"

        except (TypeError,KeyError):
            self.currentMission = "Loading..."
            self.remainingTime = "Loading..."

        if self.firstUpdate:
            self.remainingTime = "Calculating."

    def __str__(self):
        return "[ Sentient Anomaly ] \nLocation : {}\nAvailable : {}".format(self.currentMission,
        self.remainingTime)

    def __repr__(self):
        return "[ Sentient Anomaly ] \nLocation : {}\nAvailable : {}".format(self.currentMission,
        self.remainingTime)

class Arbitration:
    
    def __init__(self):
        self.prevArbitration = None
        self.remainingTime = None
        self.currentMission = None
        self.needMention = False
        self.waitingState = True

    def update(self, mission):
        if len(mission) != 7:
            return
        currentTime = datetime.now().replace(microsecond=0)
        if self.prevArbitration != mission:
            self.needMention = True
            self.waitingState = False
        self.prevArbitration = mission
        self.currentMission = mission
        self.remainingTime = (timedelta(minutes=65)-timedelta(minutes=currentTime.minute)).seconds//60
        if self.remainingTime > 60:
            self.remainingTime -= 60
        self.remainingTime -= 5
        if self.remainingTime == 0:
            self.remainingTime = "<1 minutes"
        elif self.remainingTime < 0:
            self.waitingState = True
        else:
            self.remainingTime = "{} minutes".format(self.remainingTime)

    def getMention(self):
        self.needMention = False
        try:
            return get_close_matches(self.currentMission['type'].lower(),['survival', 'defense', 'defection', 'disruption', 
            'excavation', 'interception', 'infested salvage'],1)[0].capitalize()
        except IndexError:
            self.needMention = True
            return ""
            
    def __str__(self):
        if self.waitingState:
            return "[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"
        return "[ Arbitration ] \nLocation : {} (Available : {})\nEnemy : {}\nType : {}".format(self.currentMission['node'],
        self.remainingTime, self.currentMission['enemy'], self.currentMission['type'].replace("Dark Sector ",""))

    def __repr__(self):
        if self.waitingState:
            return "[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"
        return "[ Arbitration ] \nLocation : {} (Available : {})\nEnemy : {}\nType : {}".format(self.currentMission['node'],
        self.remainingTime, self.currentMission['enemy'], self.currentMission['type'].replace("Dark Sector ",""))

class TimeCycle:

    def __init__(self):
        self.cetusState = None
        self.cetusTime = None
        self.earthState = None
        self.earthTime = None
        self.vallisState = None
        self.vallisTime = None
        self.regex = re.compile('\s*\d+[s]')

    def update(self, cetus, earth, vallis):
        self.cetusState = cetus['state'].capitalize()
        self.cetusTime = self.regex.sub('', cetus['timeLeft'])                  
        self.earthState = earth['state'].capitalize()
        self.earthTime = self.regex.sub('', earth['timeLeft'])
        self.vallisState = vallis['state'].capitalize()
        self.vallisTime = self.regex.sub('', vallis['timeLeft'])
        if self.cetusTime == '':
            self.cetusTime = '<1m'
        if self.earthTime == '':
            self.earthTime = '<1m'   
        if self.vallisTime == '':
            self.vallisTime = '<1m'          

    def __str__(self):
        return """[ Time Cycle ]\nEarth : {} (Available : {})\nCetus : {} (Available : {})\nFortuna : {} (Available : {})""".format(self.earthState,
        self.earthTime, self.cetusState, self.cetusTime, self.vallisState, self.vallisTime)

    def __repr__(self):
        return """[ Time Cycle ]\nEarth : {} (Available : {})\nCetus : {} (Available : {})\nFortuna : {} (Available : {})""".format(self.earthState,
        self.earthTime, self.cetusState, self.cetusTime, self.vallisState, self.vallisTime)

class News:

    def __init__(self):
        self.name = None
        self.url = None
        self.eta = None
        self.image = None
        self.prevNews = None
        self.needEdit = False

    def update(self, news):
        if news == self.prevNews:
            return
        self.needEdit = True
        self.prevNews = news
        self.name = news['translations']['en']
        self.url = news['link']
        self.eta = re.sub(r'\d+[s]', '', news['eta']).strip()
        self.image = news['imageLink']
        if self.eta.strip() == 'ago':
            self.eta = '<1m ago'

    def getDict(self):
        self.needEdit = False
        return {'title':"[PC] Latest Warframe News", 'description':'{} [{}]'.format(self.name, self.eta), 'url':self.url, 'color':0x00ff00}

class Fissures:

    def __init__(self):
        self.lith = []
        self.meso = []
        self.neo = []
        self.req = []

    def update(self, fissures):
        self.lith = list(filter(lambda mission: mission['tierNum'] == 1, fissures))
        self.meso = list(filter(lambda mission: mission['tierNum'] == 2, fissures))
        self.neo = list(filter(lambda mission: mission['tierNum'] == 3, fissures))
        self.axi = list(filter(lambda mission: mission['tierNum'] == 4, fissures))
        self.req = list(filter(lambda mission: mission['tierNum'] == 5, fissures))
    
class WorldStat:

    def __init__(self):
        self.sentientOutposts = SentientAnomaly()
        self.timeCycle = TimeCycle() 
        self.arbitration = Arbitration()
        self.news = News()    
        self.fissures = Fissures()
        
    async def update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.warframestat.us/pc') as request:
                if request.status == 200:
                    worldStat = await request.json()
                    self.sentientOutposts.update(worldStat['sentientOutposts'])
                    self.timeCycle.update(worldStat['cetusCycle'], 
                    worldStat['earthCycle'], worldStat['vallisCycle'])
                    self.arbitration.update(worldStat['arbitration'])
                    self.fissures.update(worldStat['fissures'])
        
                    for index in range(len(worldStat['news'])-1,-1,-1):
                        if 'en' in worldStat['news'][index]['translations']:
                            self.news.update(worldStat['news'][index])
                            break
                else:
                    raise UpdateErrorException
from datetime import datetime, timedelta
from difflib import get_close_matches
import requests, json, re

class SentientAnomaly():

    def __init__(self):
        self.currentMission = None
        self.remainingTime = None
        self.nextArrive = None
        self.needMention = False
                
    def update(self, data):
        currentTime = datetime.now().replace(microsecond=0)

        if self.currentMission != data['mission'] and self.currentMission == None:
            self.needMention = True

        try:
            self.currentMission = data['mission']['node']
        except (TypeError,KeyError):
            self.currentMission = None

        self.nextArrive = (datetime.strptime(data['activation'],
        "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=7)).strftime("%H:%M")

        if data['active']:
            remainingTime = (datetime.strptime(data['previous']['expiry'],
            "%Y-%m-%dT%H:%M:%S.%fZ") - currentTime).seconds//60
            if remainingTime < 0: remainingTime = '<1 minute'
            self.remainingTime = "{} minutes".format(remainingTime)
        else:
            self.remainingTime = None

    def __str__(self):
        return """[ Sentient Anomaly ] \nLocation : {}\nAvailable : {}\nExpected Next : {}""".format(self.currentMission,
        self.remainingTime,self.nextArrive)

    def __repr__(self):
        return """[ Sentient Anomaly ] \nLocation : {}\nAvailable : {}\nExpected Next : {}""".format(self.currentMission,
        self.remainingTime,self.nextArrive)

class Arbitration():
    
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
            return """[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"""
        return """[ Arbitration ] \nLocation : {} (Available : {})\nEnemy : {}\nType : {}""".format(str(self.currentMission['node']),
        self.remainingTime, str(self.currentMission['enemy']), str(self.currentMission['type']).replace("Dark Sector ",""))

    def __repr__(self):
        if self.waitingState:
            return """[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"""
        return """[ Arbitration ] \nLocation : {} (Available : {})\nEnemy : {}\nType : {}""".format(str(self.currentMission['node']),
        self.remainingTime, str(self.currentMission['enemy']), str(self.currentMission['type']).replace("Dark Sector ",""))

class TimeCycle():

    def __init__(self):
        self.cetusState = None
        self.cetusTime = None
        self.earthState = None
        self.earthTime = None
        self.vallisState = None
        self.vallisTime = None

    def update(self, cetus, earth, vallis):
        self.cetusState = cetus['state'].capitalize()
        self.cetusTime = re.sub(r'\d+[s]', '', cetus['timeLeft']).strip()                   
        self.earthState = earth['state'].capitalize()
        self.earthTime = re.sub(r'\d+[s]', '', earth['timeLeft']).strip()
        self.vallisState = vallis['state'].capitalize()
        self.vallisTime = re.sub(r'\d+[s]', '', vallis['timeLeft']).strip()
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

class News():

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
    

class WorldStat():

    def __init__(self):
        self.sentientOutposts = SentientAnomaly()
        self.timeCycle = TimeCycle() 
        self.arbitration = Arbitration()
        self.news = News()    
        
    def update(self):
        try:
            temp = json.loads(requests.get('https://api.warframestat.us/pc').text)
            
            self.sentientOutposts.update(temp['sentientOutposts'])
            self.timeCycle.update(temp['cetusCycle'], temp['earthCycle'], temp['vallisCycle'])
            self.arbitration.update(temp['arbitration'])
            
            for index in range(len(temp['news'])-1,-1,-1):
                if 'en' in temp['news'][index]['translations']:
                    self.news.update(temp['news'][index])
                    break
        except:
            pass
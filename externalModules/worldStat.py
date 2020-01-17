from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime, timedelta
import microgear.client as client
import json, re

class Mission():
    
    def __init__(self, node, type, enemy, darksector):
        self.node = node
        self.type = type
        self.enemy = enemy
        self.darksector = darksector

def setMission():

    data = {}

    with open('MissionData.json', 'r') as file:
        temp = json.load(file)

    for key in temp:
        data[key] = Mission(temp[key]['value'], temp[key]['type'], temp[key]['enemy'], temp[key]['darksector'])

    return data

class SentientAnomaly():

    def __init__(self):
        self.period = None
        self.currentMission = None
        self.remainingTime = None
        self.lastArrive = None
        self.nextArrive = None
        self.needMention = False
        self.firstUpdate = True
        self.sentientOutPoseLastArrive = "/sentientOutPoseLastArrive"
        self.sentientOutPosePeriod = "/sentientOutPosePeriod"

        appid = 'Discord'
        gearkey = 'xLwW8SP58CvHYvl'
        gearsecret = 'gqDGYfA4FKieYh3bqbTId9jWF'

        client.create(gearkey,gearsecret,appid)

        def subscription(topic,message):
            if topic == '/'+appid+self.sentientOutPoseLastArrive and self.firstUpdate:
                self.lastArrive = datetime.strptime(message,"b'%a %b %d %H:%M:%S %Y'")
            elif topic == '/'+appid+self.sentientOutPosePeriod and self.firstUpdate:
                self.period = float(message[2:len(message)-1])
        
        client.setalias("uncle-bot")
        client.setname("uncle-bot")
        client.on_message = subscription
        client.subscribe(self.sentientOutPoseLastArrive)
        client.subscribe(self.sentientOutPosePeriod)
        client.connect()

    def update(self, data):
        currentTime = datetime.now().replace(microsecond=0) + timedelta(hours=7)

        if self.firstUpdate:
            predicted = self.period+3.1
            if predicted >= 210:
                predicted = 151 
            self.nextArrive = (self.lastArrive + timedelta(minutes=predicted)).strftime("%H:%M")

        if data['mission'] == self.currentMission and self.currentMission == None:
            self.firstUpdate = False
            return
        elif data['mission'] == None:
            self.currentMission = None
            self.remainingTime = None
        elif data['mission']['node'] == self.currentMission:
            remaining = (self.lastArrive + timedelta(minutes=30) - currentTime).seconds//60
            if self.lastArrive + timedelta(minutes=30) < currentTime or remaining == 0:
                remaining = '<1'
            self.remainingTime = str(remaining) + ' minutes'          
        elif data['mission'] != None and self.currentMission == None:
            self.currentMission = data['mission']['node']
            self.remainingTime = '30 minutes'
            if not self.firstUpdate:
                self.period = (currentTime - self.lastArrive).seconds/60
                predicted = self.period + 3.1
                if predicted >= 210:
                    predicted = 151
                self.nextArrive = (currentTime + timedelta(minutes=predicted)).strftime("%H:%M")
                self.lastArrive = currentTime
                client.publish(self.sentientOutPoseLastArrive, currentTime.ctime(), {'retain':True})
                client.publish(self.sentientOutPosePeriod, self.period, {'retain':True})
            self.needMention = True
        self.firstUpdate = False

    def __str__(self):
        return """[ Sentient Anomaly ] \nLocation : """ + str(self.currentMission) + "\nAvailable : " + str(self.remainingTime)+"""
Expected Next : """ + str(self.nextArrive)

    def __repr__(self):
        return """[ Sentient Anomaly ] \nLocation : """ + str(self.currentMission) + "\nAvailable : " + str(self.remainingTime)+"""
Expected Next : """ + str(self.nextArrive)

class Arbitration():
    
    def __init__(self):
        self.prevArbitration = None
        self.remainingTime = None
        self.currentMission = None
        self.needMention = False
        self.waitingState = False

    def update(self, missions, node):
        currentTime = datetime.now().replace(microsecond=0)
        if self.prevArbitration != node:
            self.needMention = True
            self.waitingState = False
        self.prevArbitration = node
        self.currentMission = missions[node]
        self.remainingTime = (timedelta(minutes=65)-timedelta(minutes=currentTime.minute)).seconds//60
        if self.remainingTime > 60:
            self.remainingTime -= 60
        self.remainingTime -= 5
        if self.remainingTime == 0:
            self.remainingTime = "<1 minutes"
        elif self.remainingTime < 0:
            self.waitingState = True
        else:
            self.remainingTime = str(self.remainingTime) + " minutes"


    def getMention(self):
        self.needMention = False
        return self.currentMission.type

    def __str__(self):
        if self.waitingState:
                    return """[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"""
        return """[ Arbitration ] \nLocation : """ + self.currentMission.node + " (Available : " + self.remainingTime + ')\nEnemy : ' + \
            self.currentMission.enemy + '\nType : ' + self.currentMission.type

    def __repr__(self):
        if self.waitingState:
                    return """[ Arbitration ] \nLocation : Waiting Data (Available : Waiting Data)\nEnemy : Waiting Data\nType : Waiting Data"""        
        return """[ Arbitration ] \nLocation : """ + self.currentMission.node + " (Available : " + self.remainingTime + ')\nEnemy : ' + \
            self.currentMission.enemy + '\nType : ' + self.currentMission.type

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
        return """[ Time Cycle ]
Earth : """ + self.earthState + " (Available : " + self.earthTime + ")\nCetus : " + self.cetusState + \
    " (Available : " + self.cetusTime + ")\nFortuna : " + self.vallisState + " (Available : " + self.vallisTime + ")"

    def __repr__(self):
        return """[ Time Cycle ]
Earth : """ + self.earthState + " (Available : " + self.earthTime + ")\nCetus : " + self.cetusState + \
    " (Available : " + self.cetusTime + ")\nFortuna : " + self.vallisState + " (Available : " + self.vallisTime + ")"

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
        return {'title':"[PC] Latest Warframe News", 'description':self.name+' ['+self.eta+']', 'url':self.url, 'color':0x00ff00}
    
class WorldStat():

    def __init__(self):
        self.missions = setMission()
        self.sentientOutposts = SentientAnomaly()
        self.timeCycle = TimeCycle() 
        self.arbitration = Arbitration()
        self.news = News()

    def update(self):
        try:
            temp = json.loads(str(BeautifulSoup(urlopen(Request('https://api.warframestat.us/pc', 
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'})), 
            'html.parser')))

            self.sentientOutposts.update(temp['sentientOutposts'])
            self.timeCycle.update(temp['cetusCycle'], temp['earthCycle'], temp['vallisCycle'])
            try:
                self.arbitration.update(self.missions, temp['arbitration']['solnode'])
            except KeyError:
                self.arbitration.update(self.missions, 'SolNode308')
            for index in range(len(temp['news'])-1,-1,-1):
                if 'en' in temp['news'][index]['translations']:
                    self.news.update(temp['news'][index])
                    break

            return True
        except:
            return False
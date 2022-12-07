from __future__ import print_function

import os.path
import random
import math

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
sheetID = "1QsAdSvagX-wuJo28hf4euMVY2eBYaKt5OeCoxu8WxnU"
monSheetID = "1UONrVgxMoUUvzRcUqhpKfF2r13Fwb04oISFgOuyj5Mc"
promptSheetID = "1ujabnrd1g25kq0srbgFQqS17_2FrR4LrKKOUTVirXNE"
global creds

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

##Initializes a connection to the google sheets API
service = build('sheets', 'v4', credentials=creds)

statNames = [["Name"], ["Strength", "Dexterity", "Agility", "Constitution", "Intelligence", "Wisdom", "Resolve", "Presence"], ["Melee", "Ranged", "Bond", "Exploration", "Endurance", "Reaction", 
"Resilience", "Crafting", "Hunting", "Foraging", "Fishing", "Cooking", "Athletics", "Perception", "Insight", "Persuasion", "Stealth"], ["Damage", "XP"], ["Speed", "Conditions"]]
statCodes = [["nam"], ["str", "dex", "agi", "con", "int", "wis", "rsl", "pre"], ["mel", "ran", "bnd", "exp", "end", "rea", 
"res", "cra", "hun", "frg", "fsh", "cok",  "ath", "prc", "ins", "prs", "ste"], ["dam", "xp"], ["lim"], ["ele"], ["rle"]]
diceSizes = [None, 1, 2, 3, 4, 6, 8, 10, 12, 20]
statsRange = [["!D2"], ["!C6", "!C7", "!C8", "!C9", "!C10", "!C11", "!C12", "!C13"], ["!G6", "!G7", "!G8", "!G9", "!G10", 
"!G11", "!G12", "!G13", "!G14", "!G15", "!G16", "!G17", "!G18", "!G19", "!G20", "!G21", "!G22"], ["!C15", "!C16"]]
statRanges = ["!D2", "!C6:C13", "!G6:G22", "!C15:C16", "!B19:B24", "!C19:C20", "!D19"]
elemTypes = ["Light", "Dark", "Fire", "Nature", "Water", "Air", "Lightning", "Sound", "Earth", "Toxic", "Metal"]
elemStr = [["Dark"], ["Light"], ["Nature", "Air", "Lightning", "Sound"], ["Water", "Air", "Lightning", "Sound"], ["Fire", "Air", "Lightning", "Sound"], ["Lightning", "Earth", "Toxic", "Metal"], 
["Sound", "Earth", "Toxic", "Metal"], ["Air", "Earth", "Toxic", "Metal"], ["Toxic", "Fire", "Nature", "Water"], ["Metal", "Fire", "Nature", "Water"], ["Earth", "Fire", "Nature", "Water"]]

class Character:
    ##Initializes new Character object with base values
    def __init__(self):
        self.nam=""
        self.str = self.dex = self.agi = self.con = 1
        self.int = self.wis = self.rsl = self.pre = 4
        self.mel = self.ran = self.bnd = self.exp = self.end = self.rea = self.res = 1
        self.cra = self.hun = self.frg = self.fsh = self.cok = 1
        self.ath = self.prc = self.ins = self.prs = self.ste = 1
        self.dam = self.xp = self.spd = 0
        self.mon = False
        self.cnd = []
    
    ##Increases a stat by a specified amount
    def increase(self, name, amount):
        stat = getattr(self, name)
        setattr(self, name, (stat+amount))
    
    ##Decreases a stat by a specified amount
    def decrease(self, name, amount):
        stat = getattr(self, name)
        setattr(self, name, (stat-amount))
    
    ##Returns a specified stat value
    def getStat(self, name):
        return getattr(self, name)
    
    ##Returns a dice size based on a specified stat value
    def getDice(self, name):
        return diceSizes[getattr(self, name)]

    ##Reset set of stats to their starting values
    def reset(self, stats):
        for name in stats:
            value = 1
            if name in ["int", "wis", "rsl", "pre"]:
                value = 4
            setattr(self, name, value)

    ##Load in Character information from google sheets database
    def load(self, name):
        ##Sets ranges of values to pull data from
        ranges = []
        for i in range(4):
            ranges.append(name+statRanges[i])

        try:
            for i in range(4):
                ##For each list of stats, load list from sheets and distribute to stats accordingly
                list = service.spreadsheets().values().get(spreadsheetId=sheetID, range=ranges[i], majorDimension="COLUMNS").execute().get('values', [])[0]
                for j in range(len(statCodes[i])):
                    if i == 0:
                        setattr(self, statCodes[i][j], list[j])
                    else:
                        setattr(self, statCodes[i][j], int(list[j]))
            
            ##Speed based on agility and athletics
            self.spd = (self.agi + (3 * self.ath))
            
        except HttpError as err:
            print(err)
    
    ##Flips status of whether currently controlling mon or not
    def inMon(self):
        self.mon = not self.mon

class Mon(Character):
    ##Initializes a new Mon with base stats 
    def __init__(self):
        super().__init__()
        self.int = self.wis = self.rsl = self.pre = 1
        self.rle = ""
        self.ele = []
        self.lim = ["Head"]
    
    ##Generates a random Mon
    def generate(self):
        self.nam = "Wild Mon"
        roll = random.randint(1, 20)

        ##Randomly assigns environmental niche and uses niche to determine bond difficulty
        match roll:
            case 1|2|3|4|5|6|7:
                self.rle = "Herd Prey"
                self.bnd = random.randint(1, 3)
            
            case 8|9|10|11:
                self.rle = "Solitary Prey"
                self.bnd = random.randint(3, 5)

            case 12|13|14:
                self.rle = "Pack Scavenger"
                self.bnd = random.randint(1, 5)
            
            case 15|16|17:
                self.rle = "Solo Scavenger"
                self.bnd = random.randint(4, 8)

            case 18|19:
                self.rle = "Pack Predator"
                self.bnd = random.randint(2, 6)
            
            case 20:
                self.rle = "Solo Predator"
                self.bnd = random.randint(4, 8)
        
        ##For each ability and skill, randomizes stat value based off of bond difficulty
        for i in range(1, 3):
            for statCode in statCodes[i]:
                if statCode == "bnd":
                    continue
                value = random.randint(1, 4) + (math.ceil(self.bnd / 2))
                if value > 9:
                    value = 9
                setattr(self, statCode, value)
        
        ##Randomly determines number of elements and randomly assigns elements
        numElem = random.choice([1, 1, 1, 1, 1, 2, 2, 2, 3, 3])
        while len(self.ele) < numElem:
            type = random.choice(["Light", "Dark", "Fire", "Fire", "Water", "Water", "Nature", "Nature", "Earth", "Earth", "Metal", "Metal", "Toxic", "Toxic", "Air", "Air", "Lightning", "Lightning", "Sound", "Sound"])
            if type in self.ele:
                continue
            else:
                self.ele.append(type)
        self.ele.sort()

        ##Determines number of limbs from bond difficulty and randomly assigns them
        totalLimbs = self.bnd
        while totalLimbs > 0:
            ##Arms, legs, tails, and fins more likely than wings or head
            limb = random.choice(["Arm", "Arm", "Leg", "Leg", "Tail", "Tail", "Fins", "Fins", "Wings", "Head"])
            if limb == "Wings":
                if (totalLimbs < 2):
                    continue
                else:
                    totalLimbs -= 1
            
            self.lim.append(limb)
            totalLimbs -= 1
        self.lim.sort()

        ##Speed based off of how many legs Mon has
        num = self.lim.count("Leg") + 1
        self.spd = (self.agi + (num * self.ath))
    
    ##Apply effects of broken limbs and removes limb from list of limbs
    def breakLimb(self, limb):
        self.lim.remove(limb)
        
        match limb:
            ##Reduces athletics
            case "Tail":
                self.ath -= 1
            
            #Reduces speed
            case "Leg":
                legs = self.lim.count("Leg")
                spdLoss = (self.spd // legs)
                self.spd -= spdLoss
            
            ##Applies Confusion condition if no more heads
            case "Head":
                if self.lim.count(limb) == 0:
                    self.cnd.append("Confused")
    
    ##Loads in Mon information from google sheets database
    def load(self, name):
        ##Sets ranges of values to pull data from
        ranges = []
        for i in range(7):
            ranges.append(name+statRanges[i])

        try:
            for i in range(7):
                ##For each list of stats, load list from sheets and distribute to stats accordingly
                list = service.spreadsheets().values().get(spreadsheetId=monSheetID, range=ranges[i], majorDimension="COLUMNS").execute().get('values', [])[0]
                if i == 0:
                    setattr(self, "nam", list[0])
                elif i < 4:
                    for j in range(len(statCodes[i])):
                        setattr(self, statCodes[i][j], int(list[j]))
                
                ##Load list of Mon limbs
                elif i == 4:
                    for value in list:
                        self.lim.append(value)
                
                #Load in list of Mon elements
                elif i == 5:
                    for value in list:
                        self.ele.append(value)
                
                ##Load in Mon's environmental niche
                elif i == 6:
                    self.rle = list[0]
            
            ##Sets Mon speed stat
            self.spd = (self.agi + (3 * self.ath))
            
        except HttpError as err:
            print(err)
    
    ##Checks Mon stats and returns value of highest stat
    def highest(self):
        highestValue = 0
        for i in range(1, 3):
            for j in range(len(statCodes[i])):
                if getattr(self, statCodes[i][j]) > highestValue:
                    highestValue = getattr(self, statCodes[i][j])
        return highestValue

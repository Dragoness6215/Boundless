import discord
import random
import math
import os

from discord.ext import commands
from dotenv import load_dotenv
from character import *
from exploration import *
from os import environ

load_dotenv()
token = environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
bot.remove_command("help")

pCalls = 0
pNeeded = 0
pCallers = []

players = []
characters = []
mons = []

inCreation = []
inCombat = []

promptList = []
line = ["Welcome to Boundless Character Creation!\nThe bot will run through the process of character creation with you.",
        "\n\nType 'continue' to proceed when you are ready.",
        "Please enter your character's name below.",
        "__Abilities:__\nYour physical abilities (Strength, Dexterity, Agility, Constitution) all begin at rank 1.",
        "\nYour mental abilities (Intelligence, Wisdom, Resolve, Presence) all begin at rank 4.",
        "\nRight now, you can distribute 5 additional ranks among your abilities however you see fit, but none can exceed rank 5.",
        "\n\nFormat your response to include the ability you wish to increase, followed by the amount of ranks you wish to add:",
        "'[Desired Stat] [# of Ranks]'\ne.g. 'Strength 3' or 'Agility 2'",
        "__Skills:__\nYour skills all begin at rank 1.",
        "\nRight now, you can distribute 10 additional ranks among your skills however you see fit, but none can exceed rank 5.",
        "\n\nFormat your response to include the skill you wish to increase, followed by the amount of ranks you wish to add:",
        "'[Desired Skill] [# of Ranks]'\ne.g. 'Bond 3' or 'Endurance 2'"]
instructions = [line[0]+line[1], line[2], line[3]+line[4]+line[5]+line[6]+line[7], line[8]+line[9]+line[10]+line[11]]
embedNames = [["Strength", "Intelligence", "Dexterity", "Wisdom", "Agility", "Resolve", "Constitution", "Presence"], ["Bond", "Exploration", "Melee", "Athletics",
"Crafting", "Ranged", "Perception", "Cooking", "Endurance", "Insight", "Hunting", "Resilience", "Persuasion", "Foraging", "Reaction", "Stealth", "Fishing"]]
embedCodes = [["str", "int", "dex", "wis", "agi", "rsl", "con", "pre"], ["bnd", "exp", "mel", "ath",
"cra", "ran", "prc", "cok", "end", "ins", "hun", "res", "prs", "frg", "rea", "ste", "fsh"]]
statusNames = [["Name", "Movement Speed", "Damage Taken", "EXP Points"], ["Elements", "Conditions"]]
statusCodes = [["nam", "spd", "dam", "xp"], ["ele", "cnd"]]
## ------------------------------------------------------------------------------------------------

##Checks if the player has registered a character already
def has_character():
    def predicate(ctx):
        return ctx.message.author.id in players
    return commands.check(predicate)

##Displays error message is player doesn't have permission to use command
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Please make a character before calling this command.")

##Loads all Characters and Mons when bot turns on
@bot.event
async def on_ready():
    global pNeeded
    global promptList
    global players
    global characters
    global mons

    print(f"Sucessfully logged in as {bot.user}") ##Message to show bot booted correctly

    try:
        ##Accesses spreadsheets from Google Sheets
        charSheets = service.spreadsheets().get(spreadsheetId=sheetID).execute()['sheets']
        monSheets = service.spreadsheets().get(spreadsheetId=monSheetID).execute()['sheets']

        ##For each sheet pair in Characters and Mons, loads the character and mon as objects
        for i in range(len(charSheets)):
            charTitle = charSheets[i]['properties']['title']
            monTitle = monSheets[i]['properties']['title']
            if charTitle != 'Template': ##Checks if sheet is the template and skips if it is
                players.append(int(charTitle))
                char = Character() ##Creates new objects
                mon = Mon()
                char.load(charTitle) ##Loads database info to objects
                mon.load(monTitle)
                characters.append(char) ##Adds finished objects to lists
                mons.append(mon)
                pNeeded = math.ceil(len(players) * (2/3))
        
        ##Loads in all available prompts from google sheet database
        promptList = service.spreadsheets().values().get(spreadsheetId=promptSheetID, range="A1:A", majorDimension="COLUMNS").execute().get('values', [])[0]

    except HttpError as err:
        print(err)

## ------------------------------------------------------------------------------------------------

##Groups commands to be called on characters
@bot.group(invoke_without_command=True)
async def char(ctx):
    return

##Displays status information of your character
@char.command()
@has_character()
async def status(ctx):
    await embedStatus(ctx, characters, "__Colonist Status:__")

##Displays information on character abilities
@char.command()
@has_character()
async def stats(ctx, *, ability=None):
    await embedStats(ctx, characters, "__Colonist Abilities:__", embedNames[0], embedCodes[0], ability)

##Displays information on character skills
@char.command()
@has_character()
async def skills(ctx, *, skill=None):
    await embedStats(ctx, characters, "__Colonist Skills:__", embedNames[1], embedCodes[1], skill)

##Ranks up a specified stat of your character
@char.command()
@has_character()
async def rankup(ctx, stat):
    if stat.capitalize() not in (embedNames[0] + embedNames[1]):
        await ctx.send("Invalid Stat: Please refer to Ability/Skill list.")
    
    else:
        await rankUp(ctx, characters, stat.capitalize(), sheetID)

##Begins character creation process
@char.command()
async def create(ctx):
    global inCreation
    global pNeeded
    global characters
    global players

    ##Check if player already made character
    if ctx.author.id in players:
        await ctx.send("You have already made a character.")
        return
    
    ##Check if player is already making character
    if ctx.author.id in inCreation:
        await ctx.send("You are already making a character.")
        return
    
    inCreation.append(ctx.author.id)
    char = Character()
    mon = Mon()

    ##Checks for valid user input
    def check(m):
        return m.content.lower() in ["continue", "restart"] and m.channel == ctx.channel and m.author == ctx.author
    def checkName(m):
        return m.channel == ctx.channel and m.author == ctx.author
    
    ##Wait for player to type 'continue'
    await ctx.send(instructions[0])
    await bot.wait_for('message', check=check)

    ##Ask for character name and wait for player input to confirm
    while True:
        await ctx.send(instructions[1])
        msg = await bot.wait_for("message", check=checkName)
        setattr(char, "nam", msg.content)

        await ctx.send("If you are happy with your character name, type 'continue' to proceed. If not, type 'restart' to try again.")
        msg = await bot.wait_for('message', check=check)
        if msg.content.lower() == "continue":
            break
    
    ##Ask player to assign abilities and confirm final decisions
    await ctx.send(instructions[2])
    await assignStats(ctx, char, statNames[1], statCodes[1], 5, "abilities")

    ##Ask player to assign skills and confirm final decisions
    await ctx.send(instructions[3])
    await assignStats(ctx, char, statNames[2], statCodes[2], 10, "skills")

    ##Assign speed stat after other stats are complete
    speed = (char.getStat("agi") + (3 * char.getStat("ath")))
    char.increase("spd", speed)

    await ctx.send("Character Creation: Complete")
    
    ##Duplicate template Character and Mon sheet and assign new values to new sheets in database
    newSheet(str(ctx.author.id), 647374573, 647374573, char)
    editSheet(monSheetID, ctx.author.id, statsRange[0][0], [char.getStat("nam")])

    ##Add character and mon to respective lists for easy reference
    players.append(ctx.author.id)
    characters.append(char)
    inCreation.remove(ctx.author.id)
    mon.load(str(ctx.author.id))
    mons.append(mon)
    
    pNeeded = math.ceil(len(players) * (2/3))

##Deletes player's character along with associated Mon
@char.command()
@has_character()
async def delete(ctx):
    deleteSheet(ctx, sheetID)
    deleteSheet(ctx, monSheetID)
    
    index = players.index(ctx.author.id)
    del players[index]
    del characters[index]
    del mons[index]
    
    await ctx.send("Character has been deleted.")

## ------------------------------------------------------------------------------------------------

##Groups commands to be called on Mons
@bot.group(invoke_without_command=True)
async def mon(ctx):
    return

##Displays status information of your Mon
@mon.command()
@has_character()
async def status(ctx):
    await embedStatus(ctx, mons, "__Mon Status:__")

##Displays information on Mon abilities
@mon.command()
@has_character()
async def stats(ctx, *, ability=None):
    await embedStats(ctx, mons, "__Mon Abilities:__", embedNames[0], embedCodes[0], ability)

##Displays information on Mon skills
@mon.command()
@has_character()
async def skills(ctx, *, skill=None):
    await embedStats(ctx, mons, "__Mon Skills:__", embedNames[1], embedCodes[1], skill)

##Ranks up a specified stat of your Mon
@mon.command()
@has_character()
async def rankup(ctx, stat):
    if stat.capitalize() not in (embedNames[0] + embedNames[1]):
        await ctx.send("Invalid Stat: Please refer to Ability/Skill list.")
    
    else:
        await rankUp(ctx, mons, stat.capitalize(), monSheetID)

##Lets player enter and leave the mind of their Mon
@mon.command()
@has_character()
async def control(ctx):
    ##Controlling or leaving Mon not allowed during combat
    if ctx.author.id in inCombat:
        await ctx.send("Please finish your encounter before calling this command.")
        return
    
    char = characters[players.index(ctx.author.id)]
    char.inMon()
    if char.getStat("mon"):
        await ctx.send("You have entered the mind of your Domonstri!")
    else:
        await ctx.send("You have left the mind of your Domonstri!")

## ------------------------------------------------------------------------------------------------

##Displays all available commands in an embedded help message
@bot.command()
async def help(ctx):
    embed=discord.Embed(title="__Available Commands:__", description="A list of all commands supported by the bot and the format to call them.\nArguments written with {} or [] are required while arguments written with <> are optional. (Do not include brackets when calling the command)", color=discord.Color.blue())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="!{char/mon} status", value="Displays status information for your character or mon.", inline=False)
    embed.add_field(name="!{char/mon} stats <ability>", value="Displays your character's or mon's abilities, or a specified ability, if provided.", inline=False)
    embed.add_field(name="!{char/mon} skills <skill>", value="Displays your character's or mon's skills, or a specified skill, if provided.", inline=False)
    embed.add_field(name="!{char/mon} rankup [stat]", value="Levels up a specified stat of your character or mon.", inline=False)
    embed.add_field(name="!char {create/delete}", value="Begins the character creation process or deletes an existing character.", inline=False)
    embed.add_field(name="!mon control", value="Enters or leaves the mind of your Domonstri.", inline=False)
    embed.add_field(name="!roll [X]d[X] <comment>", value="Rolls a specified amount and size of dice. (Replace X's with digits)", inline=False)
    embed.add_field(name="!check [ability] [skill]", value="Rolls a stat check with the specified ability and skill.", inline=False)
    embed.add_field(name="!prompt", value="Generates a prompt for all players to react to.\n(2/3rds must call this command to generate the prompt)", inline=False)
    embed.add_field(name="!encounter", value="Begins a random encounter with a wild Domonstri.", inline=False)
    embed.add_field(name="!explore [direction]", value="Explores a nex hex in a specified direction.\n(Northwest, West, Southwest, Northeast, East, or Southeast)", inline=False)
    embed.add_field(name="!biome", value="Returns the biome of your current hex.", inline=False)
    
    await ctx.send(embed=embed)

## ------------------------------------------------------------------------------------------------

##Rolls a dice of specified size and amount
@bot.command(aliases = ['r'])
async def roll(ctx, dice, *, comment=None):
    dice.casefold()
    txt = dice.split("d")
    amount, size = [int(txt[i]) for i in (range(2))] ##Separates dice input for roll command

    finalMessage = rollCommand(dice, amount, size, 0)[0]

    ##If there is a comment at the end, add it to the displayed message
    if comment != None:
        finalMessage += ("\n#" + comment)

    await ctx.send(ctx.author.mention+finalMessage)

## ------------------------------------------------------------------------------------------------

##Makes a check with specified ability and skill
@bot.command()
@has_character()
async def check(ctx, ability, skill, *, comment=None):
    char = characters[players.index(ctx.author.id)]
    ability = ability.capitalize()
    skill = skill.capitalize()

    ##Assigns dice values based on current stat values
    amount = char.getStat(embedCodes[1][embedNames[1].index(skill)])
    size = char.getDice(embedCodes[0][embedNames[0].index(ability)])
    dice = "%sd%s" % (amount, size)

    finalMessage = rollCommand(dice, amount, size, char.getStat("dam"))[0]

    ##If there is a comment at the end, add it to the displayed message
    if comment != None:
        finalMessage += ("\n#" + comment)

    await ctx.send(ctx.author.mention+finalMessage)

## ------------------------------------------------------------------------------------------------

##Allows players to collectively call a prompt together
@bot.command()
@has_character()
async def prompt(ctx):
    global pCalls
    global pCallers
    
    ##Checks if players has called command already
    if ctx.author.id not in pCallers:
        pCalls += 1
        pCallers.append(id)
    
    ##Checks if enough playes have called command
    if pCalls < pNeeded:
        await ctx.send("\nAdditional Players Required: %s more player(s) needed to get prompt." % (pNeeded - pCalls))
    
    ##If enough have called, display new prompt
    else:
        await ctx.send("\nYour New Prompt: **%s**" % promptList[random.randrange(0, len(promptList))])
        pCalls = 0
        pCallers.clear()    

## ------------------------------------------------------------------------------------------------

##Begins an encounter with a random Mon
@bot.command()
@has_character()
async def encounter(ctx):
    ##Checks if already in combat
    global inCombat
    if ctx.author.id in inCombat:
        await ctx.send("You are already in an encounter.")
        return
    
    ##Assigns active character (Uses player's mon if currently in mind of Mon)
    inCombat.append(ctx.author.id)
    char = characters[players.index(ctx.author.id)]
    if char.getStat("mon"):
        char = mons[players.index(ctx.author.id)]
    mon = await randomMon(ctx)

    await ctx.send("__Combat Round:__ Initiative (Agility Reaction)")
    
    ##Rolls initiative for player and wild mon
    charIni = initiative(char)
    await ctx.send("Player's Initiative Roll:%s" % charIni[0])
    monIni = initiative(mon)
    await ctx.send("Domonstri's Initiative Roll:%s" % monIni[0])

    ##Decides turn order based on initiative roll
    turnOrder = []
    if charIni[1] > monIni[1]:
        turnOrder.append(char)
        turnOrder.append(mon)
    
    else:
        turnOrder.append(mon)
        turnOrder.append(char)
    
    await ctx.send("__Turn Order:__\n%s\n%s" % (turnOrder[0].getStat("nam"), turnOrder[1].getStat("nam")))
    
    ##Waits for user input to begin combat
    def check(m):
        return m.content.lower() == 'continue' and m.channel == ctx.channel and m.author == ctx.author
    await ctx.send("Type 'continue' when you are ready to begin.")
    await bot.wait_for('message', check=check)
    
    result = await combat(ctx, turnOrder)

    ##If player won encounter, distribute XP points
    if result[0] == "Mon Died":
        await ctx.send("You have earned %s XP points." % result[1])
        if char in mons:
            char = characters[mons.index(char)]
        char.increase("xp", result[1])
        editSheet(sheetID, ctx.author.id, statsRange[3][1], [char.getStat("xp")])

    inCombat.remove(ctx.author.id)

## ------------------------------------------------------------------------------------------------

##Explores the next hexagon in environment grid in specified direction
@bot.command()
@has_character()
async def explore(ctx, direction):
    dir = direction.lower()
    if dir not in directions: ##Check if valid direction
        await ctx.send("Invalid Direction: Please use Northeast, East, Southeast, Northwest, West, or Southwest")
        return
    
    explore = move(dir)
    await ctx.send(explore[0])
    if explore[1] > 0: ##If new discovery, give XP
        for character in characters:
            character.increase("xp", explore[1])
            editSheet(sheetID, players[characters.index(character)], statsRange[3][1], [character.getStat("xp")])
        await ctx.send("Explorers have gained 5 XP Points!")

## ------------------------------------------------------------------------------------------------

##Displays player's current biome
@bot.command()
@has_character()
async def biome(ctx):
    await ctx.send("You are currently within a %s biome." % getBiome())

## ------------------------------------------------------------------------------------------------

##Rolls a specified amount of a specified size dice and returns a formatted message
def rollCommand(dice, amount, size, damage):
    total = 0
    rollText = ""
    damageText = ""
    
    for i in range(0, amount):
        if(i != 0): ##prevents there to be a + for the first loop
            rollText += ", "
        roll = random.randint(1, size) ##TODO: THIS IS PSUEDORANDOM? MAYBE MAKE BETTER
        total += roll
        rollText += str(roll)
    
    if damage > 0:
        total -= damage
        damageText = " - %s" % damage
    
    finalMessage = "\nResult: **%s** [%s (%s)%s]" % (total, dice, rollText, damageText)
    
    return [finalMessage, total]

##Allows player to assign values to a specified stat list until they are happy with it
async def assignStats(ctx, char, statNames, statCodes, maxRanks, txt):
    ##Checks for valid input from user
    def check(m):
        return m.content.lower() in ['continue', 'restart'] and m.channel == ctx.channel and m.author == ctx.author
    def checkStat(m):
        stat = m.content.split()
        return stat[0].capitalize() in statNames and stat[1].isdigit() and len(stat) == 2 and m.channel == ctx.channel and m.author == ctx.author
    
    ##Repeat until player is happy with stat allotment
    while True:
        ranks = maxRanks
        
        ##Repeat until player has used up available stat ranks
        while ranks > 0:
            await ctx.send("You have %s remaining rank(s) to distribute amongst your %s." % (ranks, txt))
            msg = await bot.wait_for("message", check=checkStat)
            rank = msg.content.split()

            stat = statCodes[statNames.index(rank[0].capitalize())]
            amount = int(rank[1])

            ##Sends error if exceeding maximum stat value
            if char.getStat(stat) + amount > 5:
                await ctx.send("A stat cannot exceed 5 ranks.")
                continue

            ##Sends error if using too many stat ranks
            if ranks - amount < 0:
                await ctx.send("You cannot distribute more than %s ranks total." % maxRanks)
                continue

            char.increase(stat, amount)
            ranks -= amount
        
        await ctx.send("If you are happy with your %s, type 'continue' to proceed. If not, type 'restart' to try again." % txt)
        msg = await bot.wait_for('message', check=check)
        if msg.content.lower() == "continue":
            break
        char.reset(statCodes)

#Creates a discord embed message to display stat information for character
async def embedStats(ctx, list, title, names, codes, stat):
    ##Initializes embed
    char = list[players.index(ctx.author.id)]
    embed = discord.Embed(title=title, color = discord.Color.blue())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    ##If user specified stat, only reference that stat
    if stat:
        stat = stat.capitalize()
        ##If invalid stat name, show error and abort code
        if stat not in names:
            await ctx.send("Invalid Stat: Please refer to Ability/Skill list.")
            return

        embed.add_field(name = stat, value = "Rank: %s" % char.getStat(codes[names.index(stat)]), inline = False)
    
    ##Otherwise, display information for all stats in specified list
    else:
        for i in range(len(names)):
            embed.add_field(name=names[i], value="Rank: %s" % char.getStat(codes[i]), inline=True)
            if names[0] == "Strength" and i % 2 == 1 and i != 7:
                embed.add_field(name='\u200b', value='\u200b', inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
    
    await ctx.send(embed=embed)

##Creates a discord embed message to display status information for character
async def embedStatus(ctx, list, title):
    ##Initializes embed
    char = list[players.index(ctx.author.id)]
    embed = discord.Embed(title=title, color = discord.Color.blue())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    ##For each relevant stat, add field to display information
    for i in range(len(statusNames[0])):
        embed.add_field(name=statusNames[0][i], value=char.getStat(statusCodes[0][i]), inline=True)
        if i % 2 == 1:
            embed.add_field(name='\u200b', value='\u200b', inline=True)
    
    ##If getting status of mon, adds mon-only information to embed
    if char in mons:
        elements = char.getStat(statusCodes[1][0])
        elementtxt = ""
        for i in range(len(elements)):
            if i != 0:
                elementtxt += ", "
            elementtxt += elements[i]
        embed.add_field(name = statusNames[1][0], value=elementtxt, inline=False)
    
    ##Displays any conditions character is suffering if applicable
    if char.getStat(statusCodes[1][1]):
        conditions = char.getStat(statusCodes[1][1])
        conditiontxt = ""
        for i in range(len(conditions)):
            if i != 0:
                conditiontxt += ", "
            conditiontxt += conditions[i]
        embed.add_field(name = statusNames[1][1], value=conditiontxt, inline=False)

    await ctx.send(embed=embed)

##Ranks up a specified stat of a specified character 
async def rankUp(ctx, list, stat, sheet_id):
    char = list[players.index(ctx.author.id)]
    xpSource = characters[players.index(ctx.author.id)]

    ##Find index of desired stat
    i = j = 0
    for i in range(len(statNames)):
        if stat in statNames[i]:
            j = statNames[i].index(stat)
            break
    
    value = char.getStat(statCodes[i][j])
    xpValue = xpSource.getStat("xp")

    ##If ability already at rank 9, cannot increase further
    if stat in statNames[1] and value == 9:
        await ctx.send("You cannot raise this ability above rank 9.")
    
    #Checks if player has enough XP to level up
    elif xpValue < value + 1:
        await ctx.send("You do not have enought XP points to level up this stat.")
    
    ##Increases stat and removes used XP, Updates sheets database to reflect changes
    else:
        char.increase(statCodes[i][j], 1)
        xpSource.decrease("xp", value + 1)
        editSheet(sheet_id, ctx.author.id, statsRange[i][j], [char.getStat(statCodes[i][j])])
        editSheet(sheetID, ctx.author.id, statsRange[3][1], [xpSource.getStat("xp")])
        await ctx.send("Your %s has been increased!" % stat)

##Duplicates the template sheets for Character and Mons in google sheets
def newSheet(id, sourceID, monsourceID, char):
    try:
        body = {'requests': [ {'duplicateSheet': {'sourceSheetId': sourceID, 'insertSheetIndex': 1, 'newSheetName': id} } ] }
        monbody = {'requests': [ {'duplicateSheet': {'sourceSheetId': monsourceID, 'insertSheetIndex': 1, 'newSheetName': id} } ] }
        service.spreadsheets().batchUpdate(spreadsheetId=sheetID, body=body).execute()
        service.spreadsheets().batchUpdate(spreadsheetId=monSheetID, body=monbody).execute()
        
        for i in range(4):
            statList = []
            for stat in statCodes[i]:
                statList.append(char.getStat(stat))
            editSheet(sheetID, id, statRanges[i], statList)
    
    except HttpError as err:
        print(err)

##Edits a value at a specified range in a specified google sheets document
def editSheet(sheet_id, sheet, cells, values):
    range = (str(sheet) + cells)
    try:
        body = {'values': [ values ], 'majorDimension' : 'COLUMNS'}
        service.spreadsheets().values().update(spreadsheetId=sheet_id, range=range, valueInputOption="USER_ENTERED", body=body).execute()
    
    except HttpError as err:
        print(err)

##Deletes a specified sheet from a google spreadsheet
def deleteSheet(ctx, spreadsheet_ID):
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_ID).execute()
        sheets = spreadsheet['sheets']

        for i in range(len(sheets)):
            if sheets[i]['properties']['title'] == str(ctx.author.id):
                sheet_id = sheets[i]['properties']['sheetId']
                break
        
        body = {"requests": [ {"deleteSheet": {"sheetId": sheet_id} } ] }
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_ID, body=body).execute()

    except HttpError as err:
        print(err)

##Makes an initiative roll and returns a formatted message
def initiative(char):
    amount = char.getStat("rea")
    size = char.getDice("agi")
    dice = "%sd%s" % (amount, size)

    return rollCommand(dice, amount, size, char.getStat("dam"))

##Generates and returns a random Mon along with a message describing the Mon
async def randomMon(ctx):
    mon = Mon()
    mon.generate()
    limbs = mon.getStat("lim")

    await ctx.send("__You have encountered a wild Domonstri__!")
    finalMessage = "\nNiche: %s\nThe creature before you has %s and %s. " % (mon.getStat("rle"), pluralize(limbs.count("Arm"), "arm"), pluralize(limbs.count("Leg"), "leg"))
    if limbs.count("Fins") > 0:
        finalMessage += "You can make out %s emerging from its body. " % pluralize(limbs.count("Fins"), "fin")
    if limbs.count("Tail") > 0:
        finalMessage += "A set of %s sways gently behind it. " % pluralize(limbs.count("Tail"), "tail")
    if limbs.count("Wings") > 0:
        finalMessage += "%s wings sprout from its back. " % (limbs.count("Wings") * 2)
    if limbs.count("Head") > 0:
        finalMessage += "Additionally, it also seems to have %s. " % pluralize(limbs.count("Head"), "head")

    await ctx.send(finalMessage)
    return mon

##Loops through turn order until encounter is completed
async def combat(ctx, turnOrder):
    combatEnd = False
    distance = 10
    player = ctx.author.id

    ##Repeat through turn order until someone is knocked unconscious
    while not combatEnd:
        ##For each character/mon in the combat round
        for attacker in turnOrder:
            targetList = turnOrder.copy()
            targetList.remove(attacker)
            defender = targetList[0] ##Can only attack other character in turn order for right now

            att = attacker.getStat("nam")
            dfn = defender.getStat("nam")
            await ctx.send("**It is %s's turn**! The distance between you and the opponent is %sft." % (att, distance))

            ##If attacker is Confused, chance to lose their turn each round
            if "Confused" in attacker.getStat("cnd"):
                    if random.randint(1, 4) == 1:
                        await ctx.send("%s's confusion prevents it from taking its turn!" % att)
                        continue

            ##Player Offense Actions
            if attacker in characters or attacker in mons:
                actions = ["Move", "Standard"]

                ##Repeat while player still has actions available
                while actions:
                    def checkActions(m):
                        return m.content.capitalize() in (actions + ["Skip"]) and m.channel == ctx.channel and m.author.id == player
                    
                    ##Take user input on what action to take
                    await ctx.send(choiceMessage(actions) + " You may 'Skip' if you do not want to take anymore actions. Type your choice below:")
                    msg = await bot.wait_for('message', check=checkActions)
                    action = msg.content.capitalize()

                    ##Move on to next character/mon turn in turn order
                    if action == "Skip":
                        await ctx.send("__%s decides not to take any further actions this turn__!" % att)
                        break
                    
                    ##Move closer to or further away from the opponent
                    if action == "Move":
                        ##Check for valid user input
                        def checkDistance(m):
                            return m.content.isdigit() and int(m.content) > 0 and m.channel == ctx.channel and m.author.id == player
                        def checkChoice(m):
                            return m.content.lower() in ["closer", "further", "cancel"] and m.channel == ctx.channel and m.author.id == player
                        
                        ##Get user input on how to utilize move action
                        await ctx.send("You can choose to move 'Closer' to or 'Further' from the enemy. You may use 'Cancel' to return to the previous selection. Type your choice below:")
                        distanceChoice = await bot.wait_for('message', check=checkChoice)
                        direction = distanceChoice.content.lower()

                        if direction == "cancel":
                            continue

                        ##Get user input on how far to move
                        await ctx.send("__%s attempts to move %s the opponent__!\nPlease type how many feet you would like to move:" % (att, distanceMessage(direction)))
                        distMess = await bot.wait_for('message', check=checkDistance)
                        dist = int(distMess.content)
                        
                        ##If not enough speed, try again
                        while dist > attacker.getStat("spd"):
                            await ctx.send("You cannot move more than your Movement Speed during your turn.\nPlease type how many feet you would like to move:")
                            distMess = await bot.wait_for('message', check=checkDistance)
                            dist = int(distMess.content)
                        
                        if direction == "further":
                            dist *= -1
                        distance -= dist

                        ##User cannot be closer than 0ft
                        if distance < 0:
                            await ctx.send("You move as close as you possibly can to %s" % dfn)
                            distance = 0
                        
                        await ctx.send("You are now %s feet away from the opponent." % distance)
                    
                    ##Take a standard action
                    elif action == "Standard":
                        ##Check for valid user input (If limb included, check if mon has limb)
                        def checkChoice(m):
                            txt = m.content.split()
                            limbCondition = True
                            if len(txt) > 1:
                                if txt[1].capitalize() not in defender.getStat("lim"):
                                    limbCondition = False
                            return txt[0].capitalize() in ["Attack", "Flee", "Cancel"] and limbCondition and m.channel == ctx.channel and m.author.id == player
                        
                        ##Get user input on what standard action to take
                        await ctx.send("You can choose to 'Attack' or 'Flee'. You may use 'Cancel' to return to the previous selection.\nTo attack a specific limb, include it after 'Attack'. (e.g. 'Attack Arm', 'Attack Head') Type your choice below:")
                        standardChoice = await bot.wait_for('message', check=checkChoice)
                        choice = standardChoice.content.capitalize().split()

                        ##Return to action selection
                        if choice[0] == "Cancel":
                            continue

                        ##Flee the encounter and end combat
                        if choice[0] == "Flee":
                            await ctx.send("__%s runs away and flees the encounter!__" % att)
                            return ["Player Fled"]
                        
                        ##Make attack on enemy
                        elif choice[0] == "Attack":
                            ##Check if close enough to attack
                            if distance > 5:
                                await ctx.send("You are not close enough to perform a melee attack.")
                                continue

                            ##If controlling Mon, checks for type advantages and applies bonuses
                            bonus = 0
                            if attacker in mons:
                                myElem = attacker.getStat("ele")
                                enemyElem = defender.getStat("ele")
                                strengths = []
                                for elem in myElem:
                                    strengths += elemStr[elemTypes.index(elem)]
                                
                                ##For each of opponent's elements, if strong against it, increase bonus
                                for elem in enemyElem:
                                    if elem in strengths:
                                        bonus += 1
                            
                            ##Regular attacks, deal damage as normal
                            if len(choice) == 1:
                                ##Both parties get combat roll to attack or defend
                                await ctx.send("__%s steps forward and attempts to attack %s__!" % (att, dfn))
                                attackRoll = await combatRoll(ctx, attacker, "str", "mel", bonus)

                                await ctx.send("The Domonstri tries to move away to evade your attack.")
                                defenseRoll = await combatRoll(ctx, defender, "agi", "rea", 0)

                                ##If mon fails defense roll, end combat
                                if defenseRoll < 1:
                                    await ctx.send("__%s has been knocked unconscious__!" % dfn)
                                    return ["Mon Died", defender.highest()]
                                
                                damage = attackRoll - defenseRoll
                                if damage > 0: ##If attack higher than defense, inflict damage
                                    await ctx.send("%s successfully strikes %s for %s damage." % (att, dfn, damage))
                                    defender.increase("dam", damage)
                                else:
                                    await ctx.send("%s successfully protects themself from %s's attack!" % (dfn, att))
                            
                            ##Attack specific limb, no damage dealt
                            else:
                                ##Both parties get combat roll to attack or defend
                                await ctx.send("__%s steps forward and attempts to attack %s's %s__!" % (att, dfn, choice[1]))
                                attackRoll = await combatRoll(ctx, attacker, "str", "mel", bonus)

                                await ctx.send("The Domonstri tries to move away to evade your attack.")
                                defenseRoll = await combatRoll(ctx, defender, "agi", "rea", 0)

                                ##If attack higher than defense roll, calculate damage
                                damage = attackRoll - defenseRoll
                                limbDefense = defender.getStat("con") + defender.getStat("res") 
                                if damage > limbDefense: ##If damage higher than enemy Constitution plus Resilience, limb breaks
                                    await ctx.send("__%s lands the attack and breaks %s's %s__!" % (att, dfn, choice[1]))
                                    defender.breakLimb(choice[1].capitalize())
                                
                                else:
                                    await ctx.send("%s manages to protect itself from the attack!" % dfn)
                    
                    ##Remove used up actions from action list
                    actions.remove(action)
            
            ##Player Defense Actions
            else:
                ##If Mon not close enough to attack, approach player
                if distance > 5:
                    distance -= attacker.getStat("spd")
                    if distance < 5:
                        distance = 5
                    await ctx.send("The Domonstri begins to move closer to %s! It now stands %s feet away from you." % (dfn, distance))
                    if distance > 5:
                        await ctx.send("%s isn't close enough to make an attack." % att)
                        continue
                
                ##If player controlling mon, check for element type advantage against them
                bonus = 0
                if defender in mons:
                    attElem = attacker.getStat("ele")
                    enemyElem = defender.getStat("ele")
                    strengths = []
                    for elem in attElem:
                        strengths += elemStr[elemTypes.index(elem)]
                                    
                    for elem in enemyElem:
                        if elem in strengths:
                            bonus += 1
                
                await ctx.send("__%s lunges forward and attempts to attack %s__!" % (att, dfn))
                attackRoll = await combatRoll(ctx, attacker, "str", "mel", bonus)

                ##Check for valid user input
                def check(m):
                    return m.content.lower() in ["evade", "endure", "counter"] and m.channel == ctx.channel and m.author.id == player
                
                ##Get user input on desired defense method
                await ctx.send("You can attempt to 'Evade' the attack (Agi Rea), 'Endure' it (Con End), or 'Counter' it (Str End).\nType your choice below:")
                msg = await bot.wait_for('message', check=check)
                defense = msg.content.lower()

                #detrmine ability and skill for defense roll based on defense method
                if defense == "evade":
                    stat, skill = ["agi", "rea"]     
                elif defense == "endure":
                    stat, skill = ["con", "end"]
                elif defense == "counter":
                    stat, skill = ["str", "end"]
                
                defenseRoll = await combatRoll(ctx, defender, stat, skill, 0)
                
                ##If player fails defense roll, end combat
                if defenseRoll < 1: 
                    await ctx.send("__%s has been knocked unconscious__!" % dfn)
                    return ["Player Died"]
                
                ##If attack roll higher than defense, inflict damage
                damage = attackRoll - defenseRoll
                if damage > 0:
                    await ctx.send("%s successfully strikes %s for %s damage." % (att, dfn, damage))
                    defender.increase("dam", damage)
                    if defender in characters:
                        sheet_id = sheetID
                    else:
                        sheet_id = monSheetID
                    editSheet(sheet_id, player, statsRange[3][0], [defender.getStat("dam")])
                else:
                    await ctx.send("%s successfully protects themself from %s's attack!" % (dfn, att))

##Makes an attack or defense roll based off specified attack or defense method and sends a formatted message
async def combatRoll(ctx, char, stat, skill, bonus):
    amount = char.getStat(skill) + bonus
    size = char.getDice(stat)
    dice = "%sd%s" % (amount, size)

    roll = rollCommand(dice, amount, size, char.getStat("dam"))
    await ctx.send(roll[0])

    return roll[1]

##Adds an s if a word needs to be plural, otherwise doesn't change it
def pluralize(amount, input):
    finalMessage = "%s %s" % (amount, input)
    if amount != 1:
        finalMessage += "s"

    return finalMessage

##Formats remaining actions for the player to take for displayed messages
def choiceMessage(actions):
    if len(actions) == 1:
        return ("You have a '%s' action remaining." % actions[0])
    
    if len(actions) > 1:
        return ("You have a '%s' and a '%s' action remaining." % (actions[0], actions[1]))

##Formats distance messages quickly for displayed messages
def distanceMessage(choice):
    if choice == "closer":
        return (choice + " to")
    if choice == "further":
        return (choice + " from")

## ------------------------------------------------------------------------------------------------

bot.run(token)
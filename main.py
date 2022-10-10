# RUNNING: navigate to that folder, and then call:
# py -3 main.py   

import discord
from os import environ
from dotenv import load_dotenv

from functions import *
from mysql import *

#Global Variables
prefix="!"

USE_MYSQL=True ##Easy way to enable/disable MySQL database code.

##Setting up hidden variables (we don't want people knowing the token)
load_dotenv()
token = environ["TOKEN"]

##initializing the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True
client = discord.Client(intents=intents)

## ------------------------------------------------------------------------------------------------

@client.event
async def on_ready(): 
    ##prints to the terminal once the bot's online
    print(f'We have logged in as {client.user}')
    #await guild.system_channel.send("@here Boundless is on!")
    ##Test code to add all members to the database if need be.
    for guild in client.guilds:
        for member in guild.members:
            print(member.display_name)
            ##if(member.display_name!="Boundless" and not member.bot and USE_MYSQL ):
            ##    await addPlayer(member)

## ------------------------------------------------------------------------------------------------

@client.event
async def on_member_join(member): ##Called whenever the bot sees someone join
    for guild in client.guilds:
        for channel in guild.channels:
            if(channel.name=='general'):
                await channel.send(member.mention+" Welcome! \n Call <***"+str(prefix)+"help***> for help getting started! \n Here's the link to the full documentation: <TBD>")
                if(USE_MYSQL): await addPlayer(member)

## ------------------------------------------------------------------------------------------------

@client.event
async def on_guild_join(guild):
    print("Joined: "+str(guild.name))

## ------------------------------------------------------------------------------------------------

@client.event
async def on_message(message): ##called whenever the bot regesters a message

    if message.author == client.user: ##removes responding to boundless's own messages
        return

    print("Recieved: "+ message.content)

    ## each of the commands
    if message.content.startswith(prefix+'help'):
        await message.channel.send(help(message))

    elif message.content.startswith(prefix+'prompt'):
        await message.channel.send(message.author.mention+prompt(message))
    
    elif message.content.startswith(prefix+'r') or message.content.startswith(prefix+'R') or message.content.startswith(prefix+'roll') or message.content.startswith(prefix+'Roll'):
        await message.channel.send(message.author.mention+roll(message))
        
    elif message.content.startswith(prefix):
        await message.channel.send(message.author.mention+'I did not recognize that. Perhaps call **!help** for the list of all commands?')

## ------------------------------------------------------------------------------------------------

## Starts the bot running
client.run(token)
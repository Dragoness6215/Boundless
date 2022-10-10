# RUNNING: navigate to that folder, and then call:
# py -3 main.py   

# Inform Seven

import discord
from os import environ
from dotenv import load_dotenv

from functions import *
from mysql import *

#Global Variables
prefix="!"

##Setting up hidden variables (we don't want people knowing the token)
load_dotenv()
token = environ["TOKEN"]

##initializing the bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready(): 
    ##prints to the terminal once the bot's online
    print(await getPlayerInfo(1))
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message): ##called whenever the bot regesters a message

    if message.author == client.user: ##removes responding to boundless's own messages
        return

    print("Recieved: "+ message.content)

    ## each of the commands
    if message.content.startswith(prefix+'help'):
        await message.channel.send(help(message))


        #message.author.mention=@+ID
        #message.author=playername#number

    elif message.content.startswith(prefix+'prompt'):
        await message.channel.send(message.author.mention+prompt(message))
    
    elif message.content.startswith(prefix+'r') or message.content.startswith(prefix+'R') or message.content.startswith(prefix+'roll') or message.content.startswith(prefix+'Roll'):
        await message.channel.send(message.author.mention+roll(message))
        
    elif message.content.startswith(prefix):
        await message.channel.send(message.author.mention+'I did not recognize that. Perhaps call **!help** for the list of all commands?')
## Starts the running
client.run(token)
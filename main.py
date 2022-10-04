# RUNNING: navigate to that folder, and then call:
# py -3 main.py   

import discord
from os import environ
from dotenv import load_dotenv

from functions import *


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
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message): ##called whenever the bot regesters a message

    if message.author == client.user: ##removes responding to boundless's own messages
        return

    print("Recieved: "+ message.content)

    ## each of the commands
    if message.content.startswith(prefix+'hello'):
        await message.channel.send('Hello!')

    if message.content.startswith(prefix+'help'):
        await message.channel.send(help(message))
    
    if message.content.startswith(prefix+'r') or message.content.startswith(prefix+'R') or message.content.startswith(prefix+'roll') or message.content.startswith(prefix+'Roll'):
        await message.channel.send(roll(message))

## Starts the running
client.run(token)
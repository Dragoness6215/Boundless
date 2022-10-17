import discord
import random

# message formating: (bleh psuedojson)
# < Message id=1026954804683091968 
#   channel=<TextChannel 
#   id=1020393862239354920 
#   name='botrolling' 
#   position=1 
#   nsfw=False 
#   news=False 
#   category_id=1020392488206336061> 
#   type=<MessageType.default: 0> 
#   author=< Member id=622184568740642847 
#                   name='TheCrazyDragonLady' 
#                   discriminator='7007' 
#                   bot=False 
#                   nick=None 
                #   guild=< Guild id=1020392488206336060 
                #           name='BoundlessDevServer' 
                #           shard_id=0 
                #           chunked=False 
                #           member_count=5>> 
# flags=<MessageFlags value=0>>
# .content which is message content

#Called by Main for each call; named after it.
## Returns the help message
def help():
    finalMessage=", these are the commands."
    
<<<<<<< Updated upstream
    return message.author.mention+' This will be a help message'
=======
    return 'This will be a help message'
>>>>>>> Stashed changes

## rolls xdy and returns a formatted message
def roll(message):
    ##Spliting the message into readable parts
    messageSplit=message.split(' ', 1)
    rollSplit=messageSplit[0].casefold().split('d')
   
    ##string trackers; finalMessage is returned and rollMessage is used for efficency to keep track of the rolls
    rollMessage=""
    
    ##used to track the total of the rolls
    total=0
    for i in range(0,int(rollSplit[0])):
        if(i!=0): ##prevents there to be a + for the first loop
            rollMessage+=", "
        roll=random.randrange(1,int(rollSplit[1])) ##TODO: THIS IS PSUEDORANDOM? MAYBE MAKE BETTER
        total+=int(roll)
        rollMessage+=str(roll)
    
    ##Update the final message
    finalMessage="\nResult: **"+str(total)+"** ["+messageSplit[0]+" ("+rollMessage+")]"
    
    ##If there's a note attached to the end of the message, add that.
<<<<<<< Updated upstream
    if(len(firstSplit)>=3):  
        finalMessage+="\n**"
        for i in range(2,len(firstSplit)):
            finalMessage+=firstSplit[i]+" "
        finalMessage+="**"
    return message.author.mention+finalMessage

def prompt(message):
    finalMessage="srsly"
    return message.author.mention+"This will be a prompt"
=======
    if(len(messageSplit)==2):
        finalMessage+="\n#"+messageSplit[1]
    return finalMessage

def prompt(): ##Didn't like global stuff?!?!
    promptCalls=0
    neededCalls=1
    promptList=["Flood","Hurricane","Fire"]
    promptCalls+=1
    finalMessage=""
    if(promptCalls<neededCalls):
        finalMessage="\n Need "+str(neededCalls-promptCalls)+" more people to get a prompt"
    elif(promptCalls==neededCalls):
        finalMessage="**\nNew Prompt: "+promptList[random.randrange(0,len(promptList))]+"**"
    return finalMessage
>>>>>>> Stashed changes

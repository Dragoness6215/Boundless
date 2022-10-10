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
def help(message):
    finalMessage=", these are the commands."
    
    return ' This will be a help message'

## rolls xdy and returns a formatted message
def roll(message):
    ##Spliting the message into readable parts
    firstSplit=message.content.split(' ')
    rollPartWhole=firstSplit[1].casefold().split('d')
    ##string trackers; finalMessage is returned and rollMessage is used for efficency to keep track of the rolls
    finalMessage="\nRolled a total of "
    rollMessage=""
    ##used to track the total of the rolls
    total=0
    for i in range(0,int(rollPartWhole[0])):
        if(i!=0): ##prevents there to be a + for the first loop
            rollMessage+="+"
        theRoll=random.randrange(1,int(rollPartWhole[1])) ##TODO: THIS IS PSUEDORANDOM? MAYBE MAKE BETTER
        total+=int(theRoll)
        rollMessage+=str(theRoll)
    ##Update the final message
    finalMessage+="**"+str(total)+"** \n("+rollMessage+")"
    ##If there's a note attached to the end of the message, add that.
    if(len(firstSplit)>=3):  
        finalMessage+="\n**"
        for i in range(2,len(firstSplit)):
            finalMessage+=firstSplit[i]+" "
        finalMessage+="**"
    return finalMessage

def prompt(message): ##Didn't like global stuff?!?!
    numTimesPromptCalled=0
    numPeopleToCallPrompt=1
    promptList=["Flood","Hurricane","Fire"]
    numTimesPromptCalled+=1
    finalMessage=""
    if(numTimesPromptCalled<numPeopleToCallPrompt):
        finalMessage="\n Need "+str(numPeopleToCallPrompt-numTimesPromptCalled)+" more people to get a prompt"
    elif(numTimesPromptCalled==numPeopleToCallPrompt):
        finalMessage="**\nNew Prompt: "+promptList[random.randrange(0,len(promptList))]+"**"
    return finalMessage
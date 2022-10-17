import asyncio
import aiomysql
from os import environ
from dotenv import load_dotenv


load_dotenv()
password = environ["PASSWORD"]

async def fetchAll():
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password=password, db='testserver')
    cur = await conn.cursor() 
    await cur.execute("SELECT * FROM players")
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    print("Server Connected.")
    return r

async def getPlayerInfo(id):
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password=password, db='testserver')
    cur = await conn.cursor() 

    querry="SELECT * FROM players WHERE id = '"+str(id) +"'"

    await cur.execute(querry) 
    r = await cur.fetchall() 
    await cur.close()
    conn.close()
    return r

## Player ('name', id, driveLink, fighting, newPrompt, makingChar)
async def addPlayer(member):
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password=password, db='testserver')
    cur = await conn.cursor() 
    name=str(member.display_name)
    id=str(member.id)
    driveLink="''"
    querry="INSERT INTO players VALUES("+"'"+name+"',"+id+","+driveLink+","+"false"+","+"false"+","+"false"+")"
    print(querry)
    await cur.execute(querry) 
    await conn.commit()
    await cur.close()
    conn.close()


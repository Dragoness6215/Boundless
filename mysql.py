import asyncio
import aiomysql
from os import environ
from dotenv import load_dotenv


load_dotenv()
password = environ["PASSWORD"]

async def fetchAll():
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password=password, db='testserver',)
    cur = await conn.cursor() 
    await cur.execute("SELECT * FROM players")
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return r

async def getPlayerInfo(id):
    conn = await aiomysql.connect(host='localhost', port=3306, user='root', password=password, db='testserver',)
    cur = await conn.cursor() 

    querry="SELECT * FROM players WHERE id = '"+str(id) +"'"

    await cur.execute(querry) 
    r = await cur.fetchall() 
    await cur.close()
    conn.close()
    return r




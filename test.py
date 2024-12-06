import requests
import main
import asyncio
import server
import time,sys,os
import datetime

async def main1():
    try:
        req=requests.get('http://localhost:8888')
        if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
            raise Exception("Server not response")
        sys.exit("Exited")
    except Exception as error:
        server.b()
        await main.main()
asyncio.run(main1())
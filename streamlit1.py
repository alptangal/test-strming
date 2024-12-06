import aiohttp
import asyncio
import requests

async def keepLive(BASE_URL):
    print(BASE_URL+' processing')
    location=None
    isPaused=False
    
    headers={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
    }
    headers['cookie']=''
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(BASE_URL+'api/v2/app/status',headers=headers) as res:
            if res.status<400:
                js=await res.json()
                if js['status']!=5:
                    isPaused=True
        if not isPaused:
            async with session.get(BASE_URL,headers=headers,allow_redirects=False) as res:
                if res.status<400:
                    if not location:
                        location=res.headers['location']
                        #
                        async with session.get(location,headers=headers,allow_redirects=False) as res:
                            if res.status<400:
                                location=res.headers['location']
                                async with session.get(location,headers=headers,allow_redirects=False) as res:
                                    if res.status<400:
                                        location=res.headers['location']
                                        async with session.get(location,headers=headers,allow_redirects=False) as res:
                                            if res.status<400:
                                                async with session.get(location+'api/v2/app/context',headers=headers,allow_redirects=False) as res:
                                                    if res.status<400:
                                                        cookies = session.cookie_jar.filter_cookies(location)
                                                        for key, cookie in cookies.items():
                                                            headers['cookie'] += cookie.key +'='+cookie.value+';'
                                                        async with session.get(BASE_URL+'api/v2/app/disambiguate',headers=headers) as res:
                                                            print(BASE_URL,'Ping success!')
                    else:
                        async with session.get(location,headers=headers,allow_redirects=False) as res:
                            if res.status<400:
                                cookies = session.cookie_jar.filter_cookies(location)
                                for key, cookie in cookies.items():
                                    headers['cookie'] += cookie.key +'='+cookie.value+';'
                                async with session.get(BASE_URL+'api/v2/app/context',headers=headers,allow_redirects=False) as res:
                                    if res.status<400:
                                        cookies = session.cookie_jar.filter_cookies(location)
                                        for key, cookie in cookies.items():
                                            headers['cookie'] += cookie.key +'='+cookie.value+';'
                                        async with session.get(BASE_URL+'api/v2/app/disambiguate',headers=headers) as res:
                                            print(BASE_URL,'Ping success!')
        location=BASE_URL
        async with session.get(location+'api/v2/app/context',headers=headers,allow_redirects=False) as res:
            if res.status<400:
                async with session.get(BASE_URL+'api/v2/app/disambiguate',headers=headers) as res:
                    if res.status<400:
                        headers['x-csrf-token']=res.headers['x-csrf-token']
                        url=BASE_URL+'api/v2/app/status'
                        async with session.get(url,headers=headers) as res:
                            js=await res.json()
                            if js['status']!=5:
                                print(BASE_URL,'Resuming...')
                                url=BASE_URL+'api/v2/app/resume'
                                async with session.post(url,headers=headers) as res:
                                    if res.status<400:
                                        stop=False
                                        i=0
                                        while not stop:
                                            async with session.get(BASE_URL+'api/v2/app/status',headers=headers) as res:
                                                if res.status<400:
                                                    js=await res.json()
                                                    if js['status']==5:
                                                        stop=True
                                            if i==20:
                                                stop=True
                                            await asyncio.sleep(2)
                                            i+=1
                            else:
                                url=BASE_URL+'api/v2/app/restart'
                                headers['content-type']='application/json'
                                req=requests.post(url,headers=headers)
                                stop=False
                                i=0
                                while not stop:
                                    url=BASE_URL+'api/v2/app/status'
                                    req=requests.get(url,headers=headers)
                                    if req.status_code<400:
                                        js=req.json()
                                        if js['status']!=5:
                                            await asyncio.sleep(15)
                                        else:
                                            stop=True
                                    if i==10:
                                        stop=True
                                    i+=1
                            async with session.get(location+'api/v2/app/context',headers=headers,allow_redirects=False) as res:
                                if res.status<400:
                                    cookies = session.cookie_jar.filter_cookies(location)
                                    for key, cookie in cookies.items():
                                        headers['cookie'] += cookie.key +'='+cookie.value+';'
                                    async with session.get(BASE_URL+'api/v2/app/disambiguate',headers=headers) as res:
                                        if res.status<400:
                                            headers['x-csrf-token']=res.headers['x-csrf-token']
                                            url=BASE_URL+'api/v1/app/event/open'
                                            async with session.post(url,headers=headers) as res:
                                                url=BASE_URL+'api/v2/app/status'
                                                async with session.get(url,headers=headers) as res:
                                                    print(res.status)
                                                    await asyncio.sleep(60)
            return {'status':res.status}
import requests
from bs4 import BeautifulSoup as Bs4
import time
import os,re
from datetime import datetime
import random
from urllib.parse import unquote
import aiohttp
import asyncio
import math
import msgpack
import websockets

from g4f.client import Client
gf=Client()

DEVICEIDS = ['37VWSnXJ0Vn7e1f5cP1a7w==|Vt8zDuU2JHPSWyysWvXz4kI8/5Toj6Pl+iLk5bMkIbBn5Tx/YpEe5OyinB/hGWn/tWpJ4kWbn92tYQ==|tlwDeHYdISTt4DpC|08|3',"i9dq1UYJ65i8MN0pDHJFbw==|vcxdPXwx6CEMVvkDt68wxWxXXjf/YTArpoKF7/GW0iK1NTGGoGmHheh9WYCCY9XA0vuhUu/mlhaYBZE=|Nr4B0UqPTviiAbx7|08|3",'DV60Po3KPLbbC57rzzXQGQ==|YRdagLTVUvdZ67OGDArDCmXbxNCnRhNMQC5gbZLMoVacLWkUQObm25dSZK/ty7I6Or8h9BKTaKpMhw==|mQn4DpnHDHaA9yo6|08|3']

CDS_TK='1'
async def genDeviceId():
  url='https://df.infra.sz.shopee.vn/v2/shpsec/web/report'
  headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    } 
  data='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'
  async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
      async with session.post(url, headers=headers,data=data) as res:
        if res.status<400: 
          js=await res.json()
          print('Gen new Device Id success')
          return js['data']['riskToken']
  print('Can\'t gen new Device Id')
  return False
async def login(username, password,devices,email=None):
    username='84'+username[1:] if username[:1]=='0' else username
    first=False
    for i in range(2):
        if i==1:
            first=True
        for no,device in enumerate(devices):
            #device=await genDeviceId()
            url='https://shopee.vn/api/v4/account/basic/get_account_info'
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
                'Sec-Fetch-Site': 'same-origin',
                }
            async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
                async with session.get(url, headers=headers) as res:
                    if res.status<400:
                        url = 'https://shopee.vn/api/v4/account/login_by_password'
                        data = {"phone": username,
                                "password": password,
                                "support_ivs": True,
                                "client_identifier": {
                                    "security_device_fingerprint": device
                                }
                                }
                        async with session.post(url, headers=headers, json=data) as res:
                            if res.status < 400:
                                js = await res.json()
                                headers['cookie'] = ''
                                cookies = session.cookie_jar.filter_cookies(
                                    'https://banhang.shopee.vn')
                                for key, cookie in cookies.items():
                                    headers['cookie'] += cookie.key+'='+cookie.value+';'
                                if js['error'] == 98:
                                    ivsToken = js['data']['ivs_token']
                                    ivsFlow = js['data']['ivs_flow_no']
                                    url = 'https://shopee.vn/api/v4/anti_fraud/ivs/methods'
                                    data = {"event": 1, "u_token": ivsToken}
                                    async with session.post(url, headers=headers, json=data) as res:
                                        js = await res.json()
                                        vToken = js['data'][0]['v_token']
                                        url = 'https://shopee.vn/api/v4/anti_fraud/ivs/link/email_verify'
                                        data = {
                                            "v_token": vToken,
                                            "request_id": ivsToken,
                                            "new_sender_meta": {
                                                "security_device_fingerprint": device#DEVICEIDS[0]
                                            }
                                        }
                                        async with session.post(url, headers=headers, json=data) as res:
                                            js = await res.json()
                                            if not email:
                                                email = js['data']['email']
                                            print('Please verify email begin ' + email)
                                            rToken = js['data']['r_token']
                                            url = 'https://shopee.vn/api/v4/anti_fraud/ivs/link/get_status'
                                            data = {'r_token': rToken}
                                            stop = False
                                            while not stop:
                                                async with session.post(url, headers=headers, json=data) as res:
                                                    js = await res.json()
                                                    if 'data' in js and 'link_status' in js['data'] and js['data']['link_status'] == 2:
                                                        stop = True
                                                        print(email + ' verified success')
                                                await asyncio.sleep(1)
                                            url = 'https://shopee.vn/api/v4/anti_fraud/ivs/token/verify'
                                            data = {
                                                "method_name": 8,
                                                "event": 1,
                                                "u_token": ivsToken, "r_token": rToken, "v_token": vToken,
                                                "misc": {
                                                    "operation": 0
                                                }
                                            }
                                            async with session.post(url, headers=headers, json=data) as res:
                                                js = await res.json()
                                                signature = js['signature']
                                                url = 'https://shopee.vn/api/v4/account/basic/login_ivs'
                                                data = {
                                                    "is_user_login": True,
                                                    "is_web": True,
                                                    "ivs_flow_no": ivsFlow,
                                                    "ivs_signature": signature,
                                                    "ivs_method": 8,
                                                    "device_sz_fingerprint": device#DEVICEIDS[0]
                                                }
                                                async with session.post(url, headers=headers, json=data) as res:
                                                    js = await res.json()
                                                    if js['error'] == 0:
                                                        cookies = session.cookie_jar.filter_cookies(
                                                            'https://banhang.shopee.vn')
                                                        for key, cookie in cookies.items():
                                                            headers['cookie'] += cookie.key + \
                                                                '='+cookie.value+';'
                                                        url = 'https://banhang.shopee.vn/api/v2/login/'
                                                        async with session.get(url, headers=headers) as res:
                                                            if res.status < 400:
                                                                js = await res.json()
                                                                if 'errcode' in js and js['errcode'] == 0:
                                                                    cookies = session.cookie_jar.filter_cookies(
                                                                        'https://shopee.vn')
                                                                    for key, cookie in cookies.items():
                                                                        headers['cookie'] += cookie.key + \
                                                                            '='+cookie.value+';'
                                                                    url = 'https://banhang.shopee.vn/api/report/miscellaneous/last_active'
                                                                    data = {"platform_id": 1, "shop_id": js['shopid'], "timestamp": round(datetime.now(
                                                                    ).timestamp()), "action_type": "impression", "page_url": "https://banhang.shopee.vn/"}
                                                                    async with session.post(url, json=data) as res:
                                                                        1
                                                                    url='https://banhang.shopee.vn/webchat/api/coreapi/v1.2/mini/login/sc?csrf_token=&source=sc&_api_source=sc'
                                                                    async with session.post(url) as res:
                                                                        jss=await res.json()
                                                                        headers['authorization']='Bearer '+jss['token']
                                                                    url = 'https://dem.shopee.com/dem/entrance/v1/apps/minichat/tags/web-custom/event/json'
                                                                    data ={"event_timestamp":round(datetime.now().timestamp()),"app_name":"minichat","app_version":"7.7.2","app_build_id":"c2066166-fe5f-44db-9968-595c7730ad3a","user_id":"","sdk_name":"mdap_web_sdk","sdk_version":"0.4.23","session_id":"6c8c215d-392d-4e32-932c-a442141edf8d","tag":"web-custom","os_name":"Mac OS","os_version":"10.15","device_id":"c95a66c3a7575e287c2e20fb0e8e3b7f","labels":{"supportFetch":"true","supportFetchKeepAlive":"false","supportSendBeacon":"true","supportLocalstorage":"true","supportObserveType":"true","supportGetEntriesByType":"true"},"data":{"browser":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0","browser_name":"Firefox","browser_version":"121.0","engine_name":"Gecko","engine_version":"121.0","screen_dpr":2,"screen_height":1440,"screen_width":2560,"connection_type":"unknown","region":"vn","environment":"live","custom_accums":[{"point_id":"36a82dac2154de34fa4c6d7e3da73a19","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"4075993c600862e7c604e35cd692a297","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"b3105979b5cc6448de8272e177db5741","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"75cbf76696b4f8d988de72cdfeb1877c","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}}]}}
                                                                    async with session.post(url, json=data,headers=headers) as res:
                                                                        1#print(res.status,await res.json())
                                                                    url = 'https://banhang.shopee.vn/webchat/api/v1.2/mini/user/sync'
                                                                    async with session.post(url,headers=headers) as res:
                                                                        1#print(res.status,await res.json())
                                                                    url='https://banhang.shopee.vn/api/onboarding/local_onboard/v1/vn_onboard/shop/info'
                                                                    async with session.get(url,headers=headers) as res:
                                                                        if res.status<400:
                                                                            jss=await res.json()
                                                                            email=jss['email']
                                                                            shopName=jss['shop_name']
                                                        headers['cookie']+='SPC_CDS='+CDS_TK+';'
                                                        print(username+' login success')
                                                        return {'header': headers, 'username': username, 'shopId': js['shopid'], 'userId': js['id'],'user': js['username'],'avatar':js['portrait'],'deviceId':device,'email':email,'shopName':shopName}
                                elif js['error'] == 0:
                                    url = 'https://banhang.shopee.vn/api/v2/login/?SPC_CDS='+CDS_TK
                                    async with session.get(url) as res:
                                        if res.status < 400:
                                            js = await res.json()
                                            if 'errcode' in js and js['errcode'] == 0:
                                                cookies = session.cookie_jar.filter_cookies(
                                                    'https://banhang.shopee.vn')
                                                for key, cookie in cookies.items():
                                                    headers['cookie'] += cookie.key + \
                                                        '='+cookie.value+';'
                                                url = 'https://banhang.shopee.vn/api/report/miscellaneous/last_active'
                                                data = {"platform_id": 1, "shop_id": js['shopid'], "timestamp": round(datetime.now(
                                                ).timestamp()), "action_type": "impression", "page_url": "https://banhang.shopee.vn/"}
                                                async with session.post(url, json=data) as res:
                                                    1
                                                url='https://banhang.shopee.vn/webchat/api/coreapi/v1.2/mini/login/sc?csrf_token=&source=sc&_api_source=sc'
                                                async with session.post(url) as res:
                                                    jss=await res.json()
                                                    headers['authorization']='Bearer '+jss['token']
                                                url = 'https://dem.shopee.com/dem/entrance/v1/apps/minichat/tags/web-custom/event/json'
                                                data ={"event_timestamp":round(datetime.now().timestamp()),"app_name":"minichat","app_version":"7.7.2","app_build_id":"c2066166-fe5f-44db-9968-595c7730ad3a","user_id":"","sdk_name":"mdap_web_sdk","sdk_version":"0.4.23","session_id":"6c8c215d-392d-4e32-932c-a442141edf8d","tag":"web-custom","os_name":"Mac OS","os_version":"10.15","device_id":"c95a66c3a7575e287c2e20fb0e8e3b7f","labels":{"supportFetch":"true","supportFetchKeepAlive":"false","supportSendBeacon":"true","supportLocalstorage":"true","supportObserveType":"true","supportGetEntriesByType":"true"},"data":{"browser":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0","browser_name":"Firefox","browser_version":"121.0","engine_name":"Gecko","engine_version":"121.0","screen_dpr":2,"screen_height":1440,"screen_width":2560,"connection_type":"unknown","region":"vn","environment":"live","custom_accums":[{"point_id":"36a82dac2154de34fa4c6d7e3da73a19","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"4075993c600862e7c604e35cd692a297","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"b3105979b5cc6448de8272e177db5741","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}},{"point_id":"75cbf76696b4f8d988de72cdfeb1877c","timestamp":round(datetime.now().timestamp()),"data":{"userType":"seller","localOrCn":"local","chatHost":"seller"}}]}}
                                                async with session.post(url, json=data,headers=headers) as res:
                                                    1#print(res.status,await res.json())
                                                url = 'https://banhang.shopee.vn/webchat/api/v1.2/mini/user/sync'
                                                async with session.post(url,headers=headers) as res:
                                                    1#print(res.status,await res.json())
                                                url='https://banhang.shopee.vn/api/onboarding/local_onboard/v1/vn_onboard/shop/info'
                                                async with session.get(url,headers=headers) as res:
                                                    if res.status<400:
                                                        jss=await res.json()
                                                        email=jss['email']
                                                        shopName=jss['shop_name']
                                                print(username+' login success')
                                                headers['cookie']+='SPC_CDS='+CDS_TK+';'
                                                return {'header': headers, 'username': username, 'shopId': js['shopid'], 'userId': js['id'], 'user': js['username'],'avatar':js['portrait'],'deviceId':DEVICEIDS[0],'email':email,'shopName':shopName}
                if no ==len(DEVICEIDS)-1 and first==True:
                    print(username+' can\'t login.') 
                    return False



async def getProductById(headers, product):
    i = 1
    url = 'https://banhang.shopee.vn/api/v3/product/get_product_info?product_id=' + \
        str(product['id'])+'&is_draft=false'
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(url, headers=headers['header']) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    print(
                        f"{headers['username']} get product **{js['data']['product_info']['id']}** success")
                    return {'product': js['data']['product_info'], 'username': headers['username']}


async def getProducts(headers):
    i = 1
    products = []
    total = None
    totalPage = 2
    while i <= totalPage:
        url = 'https://banhang.shopee.vn/api/v3/mpsku/list/get_product_list?SPC_CDS='+CDS_TK+'&page_number=' + \
            str(i)+'&page_size=12&list_type=all&count_list_types=sold_out,banned,deboosted,deleted,unlisted,reviewing'
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.get(url, headers=headers['header']) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0 and 'products' in js['data']:
                        products += js['data']['products']
                        total = js['data']['page_info']['total']
                        totalPage = math.floor(total/12)+1
                    i += 1
    print(f"{headers['username']} get product success")
    return {'products': products, 'username': headers['username']}


async def bumpProduct(headers, product):
    url = 'https://banhang.shopee.vn/api/v3/product/boost_product/?SPC_CDS='+CDS_TK
    data = {'id': product['id']}
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers['header'], json=data) as res:
            if res.status < 400:
                js = await res.json()
                msg = product['name']+' '+js['user_message']
                return msg
            print(f'{product["name"]} can\'t bump')
            return False


async def updateAddress(headers):
    url = 'https://banhang.shopee.vn/api/v3/general/get_shop_address?SPC_CDS='+CDS_TK
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(url, headers=headers['header']) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    oldPickId = js['data']['pickup_address_id']
                    url = 'https://banhang.shopee.vn/api/v3/settings/get_address?SPC_CDS='+CDS_TK
                    async with session.get(url, headers=headers['header']) as res:
                        js = await res.json()
                        for i, add in enumerate(js['data']['list']):
                            url = 'https://banhang.shopee.vn/api/v3/settings/delete_address?SPC_CDS='+CDS_TK
                            oldId = add['address_id']
                            if oldPickId == oldId:
                                oldAddress = add['address']
                            data = {"address_id": oldId}
                            async with session.post(url, headers=headers['header'], json=data) as res:
                                if res.status < 400:
                                    js = await res.json()
                                    if js['code'] == 0:
                                        print(
                                            f"{headers['username']} old address deleted with id {oldId}")
                    url = 'https://banhang.shopee.vn/api/v3/settings/add_address?SPC_CDS='+CDS_TK
                    returnAddress = {
                        "address": "Phượng Đỏ Mega, Chợ mới Dương Liễu 1",
                        "city": "Huyện Kiến Xương",
                        "country": "VN",
                        "district": "Xã Minh Tân",
                        "full_address": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 Phượng Đỏ Mega, Chợ mới Dương Liễu 1, Xã Minh Tân, Huyện Kiến Xương, Thái Bình",
                        "name": "An",
                        "phone": "+84333893909",
                        "state": "Thái Bình",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"Dương liễu 1, Minh Tân, Kiến Xương, Thái Bình, Việt Nam\",\"region\":{\"latitude\":20.3381539,\"longitude\":106.4114485}}",
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 1,
                            "pickup": 0,
                            "buyer_return": 1,
                            "seller_return": 0
                        }
                    }
                    data = [{
                        "address": "1 Đinh Tiên Hoàng",
                        "city": "Quận Hoàn Kiếm",
                        "country": "VN",
                        "district": "Phường Lý Thái Tổ",
                        "full_address": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Đinh Tiên Hoàng, Phường Lê Thạch, Quận Hoàn Kiếm, Hà Nội",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Đinh Tiên Hoàng, Phường Lê Thạch, Quận Hoàn Kiếm, Hà Nội",
                        "phone": "+84333893909",
                        "state": "Hà Nội",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"2VH3+2QF, P. Lê Thạch, French Quarter, Hoàn Kiếm, Hà Nội, Việt Nam\",\"region\":{\"latitude\":21.0275511,\"longitude\":105.8544336}}",
                        "user_id": headers['userId'],
                        "status": 1,
                        "data_fix_version": 0,
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }, {
                        "address": "1 Nam Kỳ Khởi Nghĩa",
                        "city": "Quận 1",
                        "country": "VN",
                        "district": "Phường Bến Thành",
                        "full_address": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Nam Kỳ Khởi Nghĩa, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Nam Kỳ Khởi Nghĩa, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
                        "phone": "+84333893909",
                        "state": "TP. Hồ Chí Minh",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"225 Đ. Lê Duẩn, Bến Nghé, Quận 1, Thành phố Hồ Chí Minh, Việt Nam\",\"region\":{\"latitude\":10.7783055,\"longitude\":106.6965798}}",
                        "user_id": headers['userId'],
                        "status": 1,
                        "data_fix_version": 0,
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }, {
                        "address": "1 Bạch Đằng",
                        "city": "Quận Hải Châu",
                        "country": "VN",
                        "district": "Phường Hải Châu 1",
                        "full_address": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Bạch Đằng, Phường Phước Ninh, Quận Hải Châu, Đà Nẵng",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Bạch Đằng, Phường Phước Ninh, Quận Hải Châu, Đà Nẵng",
                        "phone": "+84333893909",
                        "state": "Đà Nẵng",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"366F+HJ4, Bạch Đằng, Phước Ninh, Hải Châu, Đà Nẵng 550000, Việt Nam\",\"region\":{\"latitude\":16.0613848,\"longitude\":108.2240675}}",
                        "user_id": headers['userId'],
                        "status": 1,
                        "data_fix_version": 0,
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }, {
                        "address": "1 Quang trung",
                        "city": "Thành Phố Thái Bình",
                        "country": "VN",
                        "district": "Phường Quang Trung",
                        "full_address": "",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 Quang Trung, Phường Quang Trung, Thái Bình",
                        "phone": "+84333893909",
                        "state": "Thái Bình",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"77 Hoàng Công Chất, P. Quan Trung, Thái Bình, Việt Nam\",\"region\":{\"latitude\":20.437401,\"longitude\":106.3320341}}",
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }, {
                        "address": "1 An Bình",
                        "city": "Quận Ninh Kiều",
                        "country": "VN",
                        "district": "Phường An Bình",
                        "full_address": "",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 An Bình, Phường An Bình, Quận Ninh Kiều, Cần Thơ",
                        "phone": "+84333893909",
                        "state": "Cần Thơ",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"KV2, An Bình, Ninh Kiều, Cần Thơ, Việt Nam\",\"region\":{\"latitude\":10.0103576,\"longitude\":105.7380511}}",
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }, {
                        "address": "1 An Khê",
                        "city": "Quận Hải An",
                        "country": "VN",
                        "district": "Phường Cát Bi",
                        "full_address": "",
                        "name": "✅ Mr An 🎊 Call/SMS/Zalo- 📞 0333893909,🌏 1 An Khê, Phường Cát Bi, Quận Hải An, Hải Phòng",
                        "phone": "+84333893909",
                        "state": "Hải Phòng",
                        "town": "",
                        "zip_code": "",
                        "geo_info": "{\"formattedAddress\":\"188 P. Cát Bi, Cát Bi, Hải An, Hải Phòng, Việt Nam\",\"region\":{\"latitude\":20.825276,\"longitude\":106.709309}}",
                        "shop_id": headers['shopId'],
                        "flag_param": {
                            "default": 0,
                            "pickup": 1,
                            "buyer_return": 0,
                            "seller_return": 1
                        }
                    }
                    ]
                    for i, item in enumerate(data):
                        if 'oldAddress' in locals() and item['address'] == oldAddress:
                            newAddress = data[(i+1) if i+1 < len(data) else 0]
                        else:
                            newAddress=data[0]
                    async with session.post(url, headers=headers['header'], json=newAddress) as res:
                        if res.status < 400:
                            js = await res.json()
                            if js['code'] == 0:
                                addressId = js['data']['address_id']
                                async with session.post(url, headers=headers['header'], json=returnAddress) as res:
                                    if res.status < 400:
                                        js = await res.json()
                                        returnId = js['data']['address_id']
                                        url = 'https://banhang.shopee.vn/api/v3/logistics/get_channel_list?SPC_CDS='+CDS_TK
                                        async with session.get(url, headers=headers['header']) as res:
                                            if res.status < 400:
                                                js = await res.json()
                                                if js['code'] == 0:
                                                    shippings = js['data']['list']
                                                    arr = []
                                                    for ship in shippings:
                                                        arr.append(
                                                            ship['channel_id'])
                                                        url = 'https://banhang.shopee.vn/api/v3/settings/is_location_supported?SPC_CDS='+CDS_TK
                                                        data = {
                                                            "channel_ids": arr, "state": newAddress['state'], "city": newAddress['city'], "district": newAddress['district'], "town": ""}
                                                        async with session.post(url, headers=headers['header'], json=data) as res:
                                                            if res.status < 400:
                                                                url = 'https://banhang.shopee.vn/api/v3/settings/set_default_address?SPC_CDS='+CDS_TK
                                                                data = {"address_id": returnId,
                                                                        "shop_id": headers['shopId']}
                                                                async with session.post(url, headers=headers['header'], json=data) as res:
                                                                    if res.status < 400:
                                                                        url = 'https://banhang.shopee.vn/api/v3/settings/set_shop_address?SPC_CDS='+CDS_TK
                                                                        data = {"pick_up_address_id": addressId, "return_address_id": returnId,
                                                                                "set_as_seller_return_address": False, "shop_id": headers['shopId']}
                                                                        async with session.post(url, headers=headers['header'], json=data) as res:
                                                                            if res.status < 400:
                                                                                js = await res.json()
                                                                                if js['code'] == 0:
                                                                                    url = 'https://banhang.shopee.vn/api/v3/settings/update_channel_toggle?SPC_CDS='+CDS_TK
                                                                                    for item in arr:
                                                                                        data = {
                                                                                            "channel_id": item, "command": "set_enable", "enabled": True}
                                                                                        async with session.post(url, headers=headers['header'], json=data) as res:
                                                                                            if res.status < 400:
                                                                                                js = await res.json()
                                                                                                if js['code'] == 0:
                                                                                                    print(f'Shipping method ID= {item} enabled')
                                                                                                else:
                                                                                                    print(f'Shipping method ID= {item} can\'t be enabled')
                                                                                    print(f"{headers['username']} \'s Address and Shipping methods updated")
                                                                                    return True
            print(f"{headers['username']} can\'t update address and shipping methods. Try again")
            return False


async def copyProduct(headers, headerOld, product, images=None):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        url = 'https://banhang.shopee.vn/api/v3/listing-upload/component/get_product_channel_info?SPC_CDS='+CDS_TK
        data = {"product_id": product['id'], "is_draft": False}
        async with session.post(url, headers=headerOld['header'], json=data) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    shippings = js['data']['list']
        if shippings:
            url = 'https://banhang.shopee.vn/api/v3/product/get_product_info?SPC_CDS='+CDS_TK+'&product_id=' + \
                str(product['id'])+'&is_draft=false'
            async with session.get(url, headers=headerOld['header']) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        productOld = js['data']
                        del productOld['product_info']['id']
                        del productOld['product_info']['status']
                        if images:
                            productOld['product_info']['images'] = images
                        productOld['product_info']['name'] = product['name']
                        productOld["is_draft"] = False
                        productOld['product_info']['logistics_channels'] = []
                        productOld['product_info']['brand_id'] = productOld['product_info']['brand_info']['brand_id']
                        productOld['product_info']['unlisted'] = productOld['product_info']['is_unlisted']
                        del productOld['product_info']['complaint_policy']
                        if 'is_unlisted' in productOld['product_info']:
                            del productOld['product_info']['is_unlisted']

                        for ship in shippings:
                            if ship['enabled'] == True:
                                ship['price'] = ship['default_price']
                                ship['channelid'] = ship['channel_id']
                                productOld['product_info']['logistics_channels'].append(
                                    ship)
        if productOld:
            for item in productOld['product_info']['model_list']:
                item['id'] = 0
                item['price'] = item['price_info']['normal_price'].split('.')[
                    0]
                item['stock_setting_list'] = []
                item['stock_setting_list'].append(
                    {'sellable_stock': item['stock_detail']['total_available_stock']})
            for item in productOld['product_info']['tier_variation']:
                item['images'] = []
            url = 'https://banhang.shopee.vn/api/v3/product/create_product_info?SPC_CDS='+CDS_TK
            async with session.post(url, headers=headers['header'], json=productOld) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        newId = js['data']['product_id']
                        url = 'https://banhang.shopee.vn/api/v3/product/get_product_info?product_id=' + \
                            str(newId)+'&is_draft=false&SPC_CDS='+CDS_TK
                        async with session.get(url, headers=headers['header']) as res:
                            if res.status < 400:
                                js = await res.json()
                                if js['code'] == 0:
                                    newProduct = js['data']['product_info']
                                    print(
                                        product['name']+' copied to '+newProduct['name']+' success')
                                    return {'product': newProduct, 'username': headers['username']}
        print(product['name']+' can\'t copy. Try again')
        return False


async def createProduct(headers, title, price, description, images, category=None):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        imgsId = []
        for img in images:
            url = 'https://banhang.shopee.vn/api/v3/general/upload_image/?SPC_CDS='+CDS_TK
            data = {
                'file': open(img, 'rb')
            }
            async with session.post(url, headers=headers['header'], data=data) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        print(js)
                        imgsId.append(js['data']['resource_id'])
        categoriesRecommend = []
        url = 'https://banhang.shopee.vn/api/v3/category/get_recommended_category?item_id=0&name=' + \
            title+'&description=&description_type=normal&SPC_CDS='+CDS_TK
        async with session.get(url, headers=headers['header']) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    categoriesRecommend = js['data']['category_recommend_list']
        categoriesTree = []
        url = 'https://banhang.shopee.vn/api/v3/category/get_category_tree/?SPC_CDS='+CDS_TK
        async with session.get(url, headers=headers['header']) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    categoriesTree = js['data']['list']
        url = 'https://banhang.shopee.vn/api/v3/product/create_product_info?SPC_CDS='+CDS_TK
        data = {}
        async with session.post(url, headers=headers['header'], json=data) as res:
            if res.status < 400:
                js = await res.json()
                print(js)
                print(res.status)


async def uploadImages(headers, images):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        imgsId = []
        for img in images:
            url = 'https://banhang.shopee.vn/api/v3/general/upload_image/?SPC_CDS='+CDS_TK
            data = {
                'file': open(img, 'rb')
            }
            async with session.post(url, headers=headers['header'], data=data) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        imgsId.append(js['data']['resource_id'])
        return imgsId


async def downloadFile(url, path):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(url) as res:
            fileType = res.headers.get(
                'content-type').split('/')[1]
            dta = await res.read()
            filename = path+'/' + \
                str(datetime.now().timestamp()).split('.')[0]+'.'+fileType
            with open(filename, 'wb') as f:
                f.write(dta)
                f.close()
            return filename


async def deleteProduct(headers, product):
    url = 'https://banhang.shopee.vn/api/v3/product/delete_product/?version=3.1.0&SPC_CDS_VER=2&SPC_CDS='+CDS_TK
    data = {"product_id_list": [product['id']]}
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers['header'], json=data) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    print(f"{product['name']} deleted")
                    return True
    print(f"{product['name']} can\'t delete. Try again.")
    return False


async def genTitle(title,count=100):
    arrs=[]
    stop=False
    while not stop:
        chat_completion = gf.chat.completions.create(model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": "tạo 100 tiêu đề giới thiệu '"+title+"' với độ dài tối đa 120 kí tự bằng tiếng Việt"}]
        )
        if all(item in chat_completion.choices[0].message.content for item in [(str(item)+'.') for item in range(1,count)]):
            stop=True
    print(f'{title} generated new title success')
    arrs1=chat_completion.choices[0].message.content.split('\n')
    for n in range(1,100):
        if str(n)+'.' in str(arrs1):
            for item in arrs1:
                if str(n)+'.' in item:
                    arrs.append(item[len(str(n))+2:])
    return arrs

async def updateProduct(headers, product, title=None, description=None, price=None, images=None):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        url = 'https://banhang.shopee.vn/api/v3/listing-upload/component/get_product_channel_info?SPC_CDS='+CDS_TK
        data = {"product_id": product['id'], "is_draft": False}
        async with session.post(url, headers=headers['header'], json=data) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    shippings = js['data']['list']
        if shippings:
            url = 'https://banhang.shopee.vn/api/v3/product/get_product_info?product_id=' + \
                str(product['id'])+'&is_draft=false&SPC_CDS='+CDS_TK
            async with session.get(url, headers=headers['header']) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        productOld = js['data']
                        productOld['product_info']['logistics_channels'] = []
                        for ship in shippings:
                            if ship['enabled'] == True:
                                ship['price'] = ship['default_price']
                                ship['channelid'] = ship['channel_id']
                                productOld['product_info']['logistics_channels'].append(
                                    ship)
        if productOld:
            data = {
                "product_id": product['id'],
                "product_info": {
                    "logistics_channels": productOld['product_info']['logistics_channels'],
                },
                "is_draft": False
            }
            data['product_info']['name'] = productOld['product_info']['name'] if not title else title
            data['product_info']['description_info'] = productOld['product_info']['description_info']
            data['product_info']['description_info']['description'] = productOld['product_info'][
                'description_info']['description'] if not description else description
            if price:
                data['product_info']['model_list'] = productOld['product_info']['model_list']
                temp = []
                for i, item in enumerate(data['product_info']['model_list']):
                    temp.append({
                        'id': item['id'],
                        'price': price[i],
                        'tier_index': [i]
                    })
                data['product_info']['model_list'] = temp
                print(data['product_info']['model_list'])
            if images:
                imagesId = []
                for img in images:
                    imgId = await uploadImages(headers, img)
                    if imgId:
                        imagesId.append(imgId)
                data['product_info']['images'] = imagesId
            url = 'https://banhang.shopee.vn/api/v3/product/update_product_info?SPC_CDS='+CDS_TK
            async with session.post(url, headers=headers['header'], json=data) as res:
                if res.status < 400:
                    js = await res.json()
                    if js['code'] == 0:
                        url = 'https://banhang.shopee.vn/api/v3/product/get_product_info?product_id=' + \
                            str(data['product_id'])+'&is_draft=false&SPC_CDS='+CDS_TK
                        async with session.get(url, headers=headers['header']) as res:
                            if res.status < 400:
                                js = await res.json()
                                if js['code'] == 0:
                                    newProduct = js['data']['product_info']
                                    print(
                                        f"{product['name']} -> {data['product_info']['name']} updated")
                                    return {'product': newProduct, 'username': headers['username']}
        print(product['name']+'- '+str(product['id']) +
              ' can\'t updated. Try again')
        return False
async def createVoucherShop(headers,name,items=[]):
    url='https://banhang.shopee.vn/api/marketing/v3/voucher/?SPC_CDS='+CDS_TK
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        if len(items)>0:
            items=[{'itemid':item['id']} for item in items]
        data = {
            "name":name,
            "start_time":round(datetime.now().timestamp())+10,
            "end_time":round(datetime.now().timestamp())+3610,
            "voucher_code":headers['user'][0:4]+str(datetime.now().timestamp()*1000).split('.')[0][-5:],
            "value":None,
            "max_value":1000,
            "discount":69,
            "min_price":1000,
            "usage_quantity":200000,
            "rule":{
                "usage_limit_per_user":1,"items":items,
                "coin_cashback_voucher":{"coin_percentage_real":None,"max_coin":None},
                "voucher_landing_page":1,"display_from":None,"exclusive_channel_type":None,"hide":0,"reward_type":0,"backend_created":0,"display_voucher_early":False,
                "choose_users":{"shop_order_count":0,"shop_order_count_period":0}}
        }
        async with session.post(url, headers=headers['header'], json=data) as res:
            if res.status < 400:
                js=await res.json()
                if js['code']==0:
                    voucherId=js['data']['voucher_id']
                    url='https://banhang.shopee.vn/api/marketing/v3/voucher/?SPC_CDS_VER=2&voucher_id='+str(voucherId)+'&SPC_CDS='+CDS_TK
                    async with session.get(url, headers=headers['header']) as res:
                        if res.status < 400:
                            js=await res.json()
                            if js['code']==0:
                                print(f"{headers['username']} created new voucher **{voucherId}** success")
                                return {'voucher':js['data'],'username':headers['username']}
    print(f"{headers['username']} can\'t create new voucher")
    return False
async def getVouchers(headers):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        url = 'https://banhang.shopee.vn/api/marketing/v3/voucher/list/?offset=0&limit=1000&promotion_type=0&SPC_CDS='+CDS_TK
        async with session.get(url, headers=headers['header']) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    print(f"{headers['username']} get vouchers list success")
                    return {'vouchers':js['data']['voucher_list'],'username':headers['username']}
    print(f'{headers["username"]} can\'t get vouchers list')
    return False
async def deleteVoucher(headers,voucher):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        url = 'https://banhang.shopee.vn/api/marketing/v3/voucher/?SPC_CDS='+CDS_TK
        data={"voucher_id":voucher['voucher_id']}
        async with session.delete(url, headers=headers['header'],json=data) as res:
            if res.status < 400:
                js = await res.json()
                if js['code'] == 0:
                    print(f'{headers["username"]} deleted voucher **{voucher["voucher_id"]}** success')
                    return True
    print(f'{headers["username"]} can\'t delete voucher **{voucher["voucher_id"]}**')
    return False
async def updateAutoChat(headers,content):
    url='https://banhang.shopee.vn/webchat/api/workbenchapi/v1.2/sc/auto_reply/shop?SPC_CDS='+CDS_TK
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        data={"shop_id":headers['shopId'],"status":"enabled","content":content}
        async with session.put(url, headers=headers['header'],json=data) as res:
            if res.status < 400:
                data={
                    "shop_id":headers['shopId'],"content":content,"status":"enabled","timezone":7,"working_days":{"mon":{"start":"00:00","end":"23:30"},"tue":{"start":"00:00","end":"23:30"},"wed":{"start":"00:00","end":"23:30"},"thu":{"start":"00:00","end":"23:30"},"fri":{"start":"00:00","end":"23:30"},"sat":{"start":"00:00","end":"23:30"},"sun":{"start":"00:00","end":"23:30"}}
                }
                url='https://banhang.shopee.vn/webchat/api/workbenchapi/v1.2/sc/offline_reply/shop?SPC_CDS='+CDS_TK
                async with session.put(url, headers=headers['header'],json=data) as res:
                    if res.status < 400:
                        print(f'{headers["username"]} update auto chat success')
                        return True
    print(f'{headers["username"]} can\'t update auto chat')
    return False
async def updateTheme(headers):
    url='https://banhang.shopee.vn/api/n/decoration/homepage/draft_create/?SPC_CDS='+CDS_TK
    data={
        "template_id":38183,
    "decoration_data":[{"meta":{"id":"61b6f7e7-5c2f-419a-be89-c7adf3424a91","type":"component"},
    "type":20,"style":{"hide_header":True,"with_bottom_margin":False,"background_color":"","highlight_color":""},
    "data":{"shop_cover_image":"e03048a5576062894717bb1ab92241f2"}},
    {"meta":{"id":"ecab0354-cdc0-4578-889d-33849f310165","type":"component"},"type":1,"style":{"hide_header":True,"with_bottom_margin":False},
    "data":{"banners":[{"image":"sg-11134210-7rcea-lqz00s5mtt0o1d",
    "navigator":{"type":1,"product_id":24860828438,"url":"https://shopee.vn/product/785018462/24860828438"}},
    {"image":"sg-11134210-7rceo-lqz00s5wte7e4f","navigator":{"type":1,"product_id":25360824736,"url":"https://shopee.vn/product/785018462/25360824736"}},
    {"image":"sg-11134210-7rce6-lqz00s5wtebg93","navigator":{"type":1,"product_id":25610828056,"url":"https://shopee.vn/product/785018462/25610828056"}},
    {"image":"sg-11134210-7rcf1-lqz00rs1dpf7c6","navigator":{"type":1,"product_id":25510829057,"url":"https://shopee.vn/product/785018462/25510829057"}}],"display_ratio":2},
    "component_template_id":""},
    {"meta":{"id":"36736430-5304-4ee5-b2da-0c1ce28a76d1","type":"component"},"type":21,"style":{"hide_header":False,"with_bottom_margin":False},
    "data":{"layout":1,"type":"auto"},"component_template_id":"03a86f73-03e4-42c7-b1ac-9a0fb5249917"},{"meta":{"id":"e6e8a71b-f8b5-4677-8243-5fdc532e8847","type":"component","version":1},
    "type":6,"style":{"hide_header":False,"with_bottom_margin":False},"data":{"title":"Đồ dùng nhà bếp và hộp đựng thực phẩm","type":"auto","sort_algorithm":"personalized",
    "banners":[{"display_ratio":2.6,"image":"sg-11134210-23020-dl7ewf3lnvnvc4"}],"actual_category_type":2},"component_template_id":"d994b846-f725-4972-ad53-dfa33294149c"},
    {"meta":{"id":"7058a64f-61ec-4919-9191-4526ed4ca230","type":"component","version":1},"type":6,"style":{"hide_header":False,"with_bottom_margin":False},
    "data":{"title":"Đồ ăn vặt","type":"auto","sort_algorithm":"personalized","banners":[{"display_ratio":2.6,"image":"sg-11134210-23020-wy39bi79ovnv23"}],
    "actual_category_type":2},"component_template_id":"d994b846-f725-4972-ad53-dfa33294149c"},
    {"meta":{"id":"4b5b4953-cf1e-4062-8d2d-9ffab9fd2db8","type":"component"},"type":14,"style":{"hide_header":False,"with_bottom_margin":False},
    "data":{"sort_algorithm":"best_selling"},"component_template_id":"f813ee91-4d74-41d6-aa8e-a09188380d26"},
    {"meta":{"id":"1f3172e0-cbc0-4305-87a6-88cb29a0e83a","type":"component","version":1},"type":3,"style":{"hide_header":False,"with_bottom_margin":False},
    "data":{"type":"manual","sort_algorithm":"personalized","products":[24210824566,24460830237,25160823816,24710828981]},"component_template_id":"ce6b21d1-a97a-413a-80b5-a162509b6942"}],
    "verify":True,"draft_version":0,"name_prefix":"Thiết Kế Hiện Tại của Shop"}
    
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers['header'],json=data) as res:
            url='https://banhang.shopee.vn/api/n/decoration/pc_homepage/draft_create/?SPC_CDS='+CDS_TK
            async with session.post(url, headers=headers['header'],json=data) as res:
                if res.status<400:
                    js=await res.json()
                    url='https://banhang.shopee.vn/api/n/decoration/homepage/draft_get/?SPC_CDS='+CDS_TK
                    async with session.get(url, headers=headers['header']) as res:
                        if res.status<400:
                            js=await res.json()
                            if js['code']==0:
                                draft=js['data']
                                url='https://banhang.shopee.vn/api/n/decoration/pc_homepage/draft_get/?SPC_CDS='+CDS_TK
                                async with session.get(url, headers=headers['header']) as res:
                                    if res.status<400:
                                        js=await res.json()
                                        if js['code']==0:
                                            draftPc=js['data']
                                url='https://banhang.shopee.vn/api/n/decoration/homepage/draft_update/?SPC_CDS='+CDS_TK
                                data={
                                    "draft_id":draft['draft_id'],
                                    "decoration_data":[
                                        {"meta":{"id":"135b5d18-cd6f-4c8f-ab2e-a310fc8eda58","type":"component"},
                                        "type":20,"style":{"hide_header":True,"with_bottom_margin":False,"background_color":"","highlight_color":""},
                                        "data":{"shop_cover_image":"e03048a5576062894717bb1ab92241f2"}},{"meta":{"id":"4d77965a-a7d6-48a7-bbe0-2a1edb8512ef","type":"component"},
                                        "type":14,"style":{"hide_header":False,"with_bottom_margin":True},"data":{"sort_algorithm":"best_selling"}}],"verify":True,"draft_version":0
                                }
                                async with session.put(url, headers=headers['header'],json=data) as res:
                                    if res.status<400:
                                        url='https://banhang.shopee.vn/api/n/decoration/homepage/draft_publish_create/?SPC_CDS='+CDS_TK
                                        data={"draft_id":draft['draft_id'],"publish_mode":1}
                                        async with session.post(url, headers=headers['header'],json=data) as res:
                                            if res.status<400:
                                                js=await res.json()
                                                if js['code']==0:
                                                    url='https://banhang.shopee.vn/api/n/decoration/pc_homepage/draft_copy/?SPC_CDS='+CDS_TK
                                                    data={"mobile_draft_id":draft['draft_id'],"draft_id":draftPc['draft_id']}
                                                    print(f"{headers['username']} update theme success")
                                                    return True
    print(f"{headers['username']} can\'t update theme")
    return False
async def updateProfileShop(headers,name,description,image):
    url='https://banhang.shopee.vn/api/sellermanagement_seller/v1/shop/profile/update?SPC_CDS='+CDS_TK
    data={"shop_name":name,"shop_logo":headers['avatar'],"shop_desc":description}
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers['header'],json=data) as res:
            url='https://shopee.vn/api/v4/image_upload?SPC_CDS='+CDS_TK
            data={'images':open(image,'rb')}
            async with session.post(url, headers=headers['header'],data=data) as res:
                if res.status<400:
                    js=await res.json()
                    if js['error']==0:
                        fileId=js['data']['filenames'][0]
                        url='https://shopee.vn/api/v4/account/update_profile?SPC_CDS='+CDS_TK
                        data={"portrait":fileId}
                        async with session.post(url, headers=headers['header'],json=data) as res:
                            if res.status<400:
                                js=await res.json()
                                if js['error']==0:
                                    print(f"{headers['username']} update shop profile(name,description,avatar) success")
                                    return True
    print(f"{headers['username']} can\'t update profile")
    return False
async def updateNickname(headers,nickname):
    url='https://shopee.vn/api/v4/account/update_profile?SPC_CDS='+CDS_TK
    data={"nickname":nickname}
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers['header'],json=data) as res:
            if res.status<400:
                js=await res.json()
                if js['error']==0:
                    print(f"{headers['username']} updated nickname success")
                    return True
    print(f"{headers['username']} can\'t update nickname")
    return False
def uploadVideo(file):
    path=file
    md5=calculate_md5(path)
    fileStat=os.stat(path)
    data={
        'file_size':fileStat.st_size,
        'md5':md5,
        'file_name':path
    }
    headers={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'cookie':'SPC_CDS=ff081a36-0814-43bf-9c00-7069d82f9c0d; SPC_SC_SA_TK=; SPC_SC_SA_UD=; SPC_SC_OFFLINE_TOKEN=; SC_SSO=-; SC_SSO_U=-; SPC_SC_SESSION=99c9ce01b4446383eb0402359d1bb911_1_1320957162; REC_T_ID=9a22caaa-4e55-11ef-ac48-76ef52b3f9c7; SPC_R_T_ID=2XH1465h/KEgCMuP2jqQADv+atF7wLNfSQ8/fcf9bhB00ICrZo0ULgkTh1Ubx7+DcDgozzS6OXC2ed+h/2hpucPxx2e4+eve6OaUoW3JlJTLiDKDsT/l7WxGv793OqcxmNJWZxibyXPZMffjM8yYRYLysoPj9Hnt6nGhNtCEu90=; SPC_T_ID=2XH1465h/KEgCMuP2jqQADv+atF7wLNfSQ8/fcf9bhB00ICrZo0ULgkTh1Ubx7+DcDgozzS6OXC2ed+h/2hpucPxx2e4+eve6OaUoW3JlJTLiDKDsT/l7WxGv793OqcxmNJWZxibyXPZMffjM8yYRYLysoPj9Hnt6nGhNtCEu90=; SPC_SI=pWWfZgAAAABIcHNhOVFaQh95dgAAAAAAdkJ3VlhsTHk=; SPC_R_T_IV=dzM4MTBVMWRYZk9Ycjc5ag==; SPC_T_IV=dzM4MTBVMWRYZk9Ycjc5ag==; SPC_F=AcvvuTRCH2XF6uxv7f66J1ScD3dJzwMJ; _gcl_au=1.1.1016154499.1722331507; _ga_4GPP1ZXG63=GS1.1.1722331510.1.1.1722332439.60.0.0; _ga=GA1.1.328303395.1722331510; _fbp=fb.1.1722331513025.116154826781126136; SPC_CLIENTID=QWN2dnVUUkNIMlhGtcqdemzziagwfgkc; SPC_EC=.bFVlRHNtRVBkNHBEQmlsTDhMnvVhH5j5q+oSaSs45HXSLDx0mu+7SqZuGeF1m4Vwgj5z5MZOKUCNAbQpivcTQbAYGeeO28q4O4CuoDIBHKENH/rQuDLO4lrvcZP/xnJMDrJYRx3hCTgfJ5iC6qJ1ilpUaN3ByWee6s3DBoRLzXAyHChOay04G/uGWbaUFUaD; SPC_ST=.bFVlRHNtRVBkNHBEQmlsTDhMnvVhH5j5q+oSaSs45HXSLDx0mu+7SqZuGeF1m4Vwgj5z5MZOKUCNAbQpivcTQbAYGeeO28q4O4CuoDIBHKENH/rQuDLO4lrvcZP/xnJMDrJYRx3hCTgfJ5iC6qJ1ilpUaN3ByWee6s3DBoRLzXAyHChOay04G/uGWbaUFUaD; SPC_SC_TK=b4be9d41d494a52d2417b90565a8f2bc; SPC_SC_UD=1320957162; SPC_STK=60S0UMq+osCBRzpithDYhMxtrwdGpiwTaPAA4Azls22zMQCaE6l+xi29gueOUZK5pfNhgfz+BU7NNnHWHYeNE/hY+iz0vE0QDTuJHJAJZwwZAAiafwlFurun4ARMBelvMAugiTg3oudEAKV+PLBpW5ORJOSc2Pg3ZEQ3N/GrQtBTvw9IkldnxnhrMbVR1gJ20n7tTOxdD7gk/PW6T4gEC2WDlsaHFYiOClv/Xg835PU=; SC_DFP=UmeZALWDtTYIRXzBeJZxPUZbhlKdWDQy; CTOKEN=2Vuf4E5XEe%2BInOIxmtPGNA%3D%3D; SPC_CDS_CHAT=4b0a74ef-f06b-4e2d-8533-53b733cdaaea; _sapid=1b82beb1243116d7d2cd09f03abcbd27fecbf50d9c81e4777e2007be; _QPWSDCXHZQA=2a44b93e-7c90-4101-db49-b0fee6246e76; REC7iLP4Q=a9af79e3-ab0b-4a1b-97d8-7d913e627841; shopee_webUnique_ccd=529IxNuYH21GPgIcGf89rw%3D%3D%7CeCUwPWmnlDA%2FtVJRnRAvK7yXUXU21wwIMdWEUyy9EZtLUAy%2BwDqTLRuvg0RG3YFKbTKgYc2UCBI%3D%7CGjspzG0iQXE%2BYAzQ%7C08%7C3; ds=fb50f9a80e00855b43039060e68f9753; SPC_U=1320957162; fulfillment-language=vi'
    }
    req=requests.post('https://banhang.shopee.vn/api/upload/v1/initiate_video_upload?SPC_CDS=ff081a36-0814-43bf-9c00-7069d82f9c0d&SPC_CDS_VER=2',headers=headers,json=data)
    print(req.status_code)
    vidName=req.json()['data']['vid']
    token=req.json()['data']['cloud_services'][0]['token']
    data={
        'token':token,
        'key':vidName+'.ori.mp4',
        'mimeType':'video/mp4'
    }
    req=requests.post('https://up-ws-vn.vod.susercontent.com/file/upload',headers=headers,files={'file':open(path,'rb')},data=data)
    print(req.text)
    fileT=req.text
    data={"vids":[vidName],"need_preview":True}

    req=requests.post('https://banhang.shopee.vn/api/upload/v1/get_video_upload_result_batch?SPC_CDS=ff081a36-0814-43bf-9c00-7069d82f9c0d&SPC_CDS_VER=2',headers=headers,json=data)

    data={
        "vid":vidName,
        "upload_result":{
            "service_id":"wscloud",
            "video_url":"https://down-ws-global.vod.susercontent.com/"+vidName+".ori.mp4",
            "extend_id":fileT
            },
        "video_info":{
            "size":fileStat.st_size,
            "md5":md5
            },
        "report_data":{"cost":2254,"sdk_version":"2.3.8","os_type":"Win32","os_version":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0","app_version":"1.0.0"}
          }
    print("https://down-ws-global.vod.susercontent.com/"+vidName+".ori.mp4")
    req=requests.post('https://banhang.shopee.vn/api/upload/v1/report_video_upload?SPC_CDS=ff081a36-0814-43bf-9c00-7069d82f9c0d&SPC_CDS_VER=2',headers=headers,json=data)
    print(req.status_code,req.text)
import asyncio
import os,sys,subprocess
import re,json
import random
import server
import aiohttp
import requests
import datetime
from fastapi import FastAPI
import gradio as gr
import hashlib
from dotenv import load_dotenv
load_dotenv()
import basic
from datetime import datetime
import time
import traceback
from bs4 import BeautifulSoup as BS4
import streamlit1


APP_TOKEN=os.getenv('base_token').strip().replace("\n",'')
APP_ID=os.getenv('app_id').strip().replace("\n",'')
APP_SECRET=os.getenv('app_secret').strip().replace("\n",'')


async def my_process(lark):
    lark=basic.LarkClass(APP_ID,APP_SECRET)
    tables=await lark.get_tables(APP_TOKEN)
    streamlit_accounts_table_id=None
    streamlit_spaces_table_id=None
    for table in tables:
        if 'streamlit_accounts' in table['name']:
            streamlit_accounts_table_id=table['table_id']
        elif 'streamlit_spaces' in table['name']:
            streamlit_spaces_table_id=table['table_id']
    page_token=None
    conditions_array=[
        {
            'field_name':'STATUS',
            'operator':'contains',
            'value':['dead']
        }
    ]
    page_token=None
    user_agents=[
        'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36',
        'Mozilla/5.0 (Windows NT 11.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5520.225 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 uacq',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.1.2; MI 5X; Flow) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/347.0.0.268 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/114.0 Firefox/114.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Snapchat/10.77.5.59 (like Safari/604.1)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; ko-KR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0 (Edition beta)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0'
    ]
    hold=None
    while True:
        result=await lark.search_record(app_token=APP_TOKEN,table_id=streamlit_accounts_table_id,conditions_array=conditions_array,page_token=page_token)
        if result and 'items' in result:
            for item in result['items']:
                owner_record_id=item['record_id']
                conditions_array1=[
                    {
                        'field_name':'OWNER',
                        'operator':'contains',
                        'value':[owner_record_id]
                    }
                ]
                page_token1=None
                while True:
                    result1=await lark.search_record(app_token=APP_TOKEN,table_id=streamlit_spaces_table_id,conditions_array=conditions_array1,page_token=page_token1)
                    if result1 and 'items' in result1:
                        for item1 in result1:
                            await lark.delete_record(app_token=APP_TOKEN,table_id=streamlit_spaces_table_id,record_id=item1['record_id'])
                    if result1 and result1['has_more']:
                        page_token1=result1['page_token']
                    else:
                        break
        if result and result['has_more']:
            page_token=result['page_token']
        else:
            break
    conditions_array=[
        {
            'field_name':'OWNER',
            'operator':'isNotEmpty',
            'value':[]
        }
    ]
    page_token=None
    while True:
        result=await lark.search_record(app_token=APP_TOKEN,table_id=streamlit_spaces_table_id,conditions_array=conditions_array,page_token=page_token)
        if result and 'items' in result:
            for item in result['items']:
                url=item['fields']['URL'][0]['text'] if '?' not in item['fields']['URL'][0]['text'] else item['fields']['URL'][0]['text'].split('?')[0]
                rs=await streamlit1.keepLive(url)
                await lark.update_record(app_token=APP_TOKEN,table_id=streamlit_spaces_table_id,record_id=item['record_id'],value_fields={'LAST_STATUS_PING':str(rs['status'])})
        if result and result['has_more']:
            page_token=result['page_token']
        else:
            break

async def main():
    lark=basic.LarkClass(APP_ID,APP_SECRET)
    while True:
        try:
            await my_process(lark)
        except:
            print('Error here ')
            traceback.print_exc()
            pass
#asyncio.run(main())
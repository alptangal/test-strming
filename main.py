import asyncio
import os,sys,subprocess,time
import re,json
import random
import server
import requests
from datetime import datetime
import basic
import gradio as gr
from collections import defaultdict
from dotenv import load_dotenv
from colorama import Fore, init
import aiohttp
from PIL import Image
from command import FFMPEG_CMD,Obj1,url_to_file
import traceback

load_dotenv()
APP_TOKEN=os.getenv('base_token').strip().replace("'",'"')
APP_ID=os.getenv('app_id').strip().replace("'",'"')
APP_SECRET=os.getenv('app_secret').strip().replace("'",'"')
GATE_PROCESS_URL=None

def resize_and_crop_with_transparency(image_path, output_path, target_width, target_height):
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height
        if original_width > original_height:
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_with_transparency = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        img_resized = img_resized.convert("RGBA")
        left = (target_width - new_width) // 2
        top = (target_height - new_height) // 2
        img_with_transparency.paste(img_resized, (left, top), img_resized)
        img_with_transparency.save(output_path, format="PNG")

def generate_effect_command(effect, text, start_time, end_time, position_x, position_y):
    if effect == 'slide_right_to_left':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x='if(gte(t,{start_time}), max({position_x}, 1920-(t-{start_time})*950), 1920)':y={position_y}:box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time+2})',
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:alpha='if(gte(t,{start_time+2}), 1-(t-{start_time+2})/2, 1)':box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time+2},{end_time})'
        """
    elif effect == 'fade_in':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:alpha='if(gte(t,{start_time}), (t-{start_time})/2, 0)':box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'fade_out':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:alpha='if(gte(t,{end_time}), 1-(t-{end_time})/2, 1)':box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'shake':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x='{position_x} + 10*sin(2*PI*(mod(t-{start_time},2)/1))':y='{position_y} + 10*cos(2*PI*(mod(t-{start_time},2)/1))':box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'rotate':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:rotate='if(gte(t,{start_time}), mod((t-{start_time})*30, 360), 0)':box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'zoom_in':
        return f"""
            drawtext=text='{text}':fontsize='if(gte(t,{start_time}), min(48+(t-{start_time})*10, 72), 48)':fontcolor=red:x={position_x}:y={position_y}:box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'zoom_out':
        return f"""
            drawtext=text='{text}':fontsize='if(gte(t,{start_time}), max(48-(t-{start_time})*10, 24), 48)':fontcolor=red:x={position_x}:y={position_y}:box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'text_with_background':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})'
        """
    elif effect == 'black_and_white':
        return f"""
            drawtext=text='{text}':fontsize=48:fontcolor=red:x={position_x}:y={position_y}:box=1:boxcolor=white@0.8:boxborderw=5:enable='between(t,{start_time},{end_time})',hue=s=0
        """
    else:
        raise ValueError("Unknown effect")

def run_ffmpeg_with_text(text, start_time, end_time, position_x, position_y, video_url, output_stream_url, effect):
    effect_command = generate_effect_command(effect, text, start_time, end_time, position_x, position_y)
    
    command = [
        'ffmpeg', '-re', '-i', video_url,
        '-vf', effect_command,
        '-c:v', 'libx264', '-preset', 'veryfast', '-maxrate', '3000k', '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
        '-f', 'flv', output_stream_url
    ]
    return command

def run_ffmpeg_with_image(image_path, start_time, end_time, position_x, position_y, video_url, output_stream_url, effect):
    resize_and_crop_with_transparency(image_path, 're.png', 300, 300)
    effect_command = f"""
        movie=re.png[img];
        [in][img] overlay=enable='between(t,{start_time},{end_time})':
            x='if(lte(t,{start_time+15}), 
               max({position_x}, 1920-(t-{start_time})*950), 
               {position_x})'
            :y={position_y} [out]
    """
    command = [
        'ffmpeg', '-re', '-i', video_url,
        '-vf', f"{effect_command},",
        '-c:v', 'libx264', '-preset', 'veryfast', '-maxrate', '3000k', '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
        '-f', 'flv', output_stream_url
    ]
    return command

async def stream_video(email,profile_url,duration_file,command):
    print(f'''
          Beginning {command}
          from {email}
          on {profile_url}
          ''')
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        last_read_time = time.time() 
        while True:
            try:
                #stdout_line=await asyncio.wait_for(process.stdout.readline(), timeout=1)
                stderr_line = await asyncio.wait_for(process.stderr.readline(), timeout=duration_file)
            except ValueError as e:
                print(f"Error reading stderr: {e}")
                stderr_line = b""  # Hoặc xử lý theo cách khác
            if stderr_line:
                try:
                    print(Fore.RED + stderr_line.decode('utf-8').strip())
                except Exception as err:
                    print(err)
            await asyncio.sleep(.1)  # Chờ một chút trước khi kiểm tra lại
        
            # Kiểm tra nếu tiến trình kết thúc bằng cách kiểm tra returncode
            if stderr_line == b'' and process.returncode is not None:
                break

        returncode = process.returncode
        if returncode != 0:
            print(f"FFmpeg process ended with error code {returncode}")
            return False
        return True
    except asyncio.TimeoutError:
        print(Fore.YELLOW + "Timeout reached, killing the ffmpeg process.")
        process.kill()  # Kill process nếu hết thời gian chờ
        await process.wait()  # Đảm bảo tiến trình kết thúc

async def get_video_duration(file_url):
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_url
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Error: {stderr.decode()}")
            return None

        data = json.loads(stdout.decode())
        duration = float(data['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None
async def create_new_process(lark,process_id,life_time):
    try:
        data={
            'id':process_id,
            'life_time':life_time
        }
        url=f'{GATE_PROCESS_URL}create-process'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as res:
                if res.status<400:
                    js=await res.json()
                    if js['status']=='success':
                        new_process_record_id=js['data']['record_id']
                        print(f'Processing- {process_id} created success')
                        return {'new_process_record_id':new_process_record_id,'lark_app_info':js['data']['lark_app_info']}
        print(f'{process_id} can\'t create new process, try again!')
    except:
        traceback.print_exc()
    return False
async def update_complete_process(lark,record_id):
    data={
        'record_id':record_id,
        'data':{'STATUS':'completed'}
    }
    url=f'{GATE_PROCESS_URL}update-process'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as res:
            if res.status<400:
                js=await res.json()
                if js['status']=='success':
                    print(f'Record- {record_id} updated success')
                    return True
    print(f'{record_id} can\'t update, try again!')
    return False

async def run_command(lark):
    global GATE_PROCESS_URL
    while True:
        tables=await lark.get_tables(APP_TOKEN)
        if tables and 'code' not in tables:
            streamers_table_id=None
            media_table_id=None
            accounts_table_id=None
            ads_content_table_id=None
            huggingface_spaces_table_id=None
            for table in tables:
                if 'processing' == table['name'].lower():
                    processing_table_id=table['table_id']
                elif 'bots' == table['name'].lower():
                    bot_table_id=table['table_id']
                elif 'tasks' == table['name'].lower():
                    tasks_table_id=table['table_id']
                elif 'streamers' == table['name'].lower():
                    streamers_table_id=table['table_id']
                elif 'media' == table['name'].lower():
                    media_table_id=table['table_id']
                elif 'streaming_accounts' == table['name'].lower():
                    accounts_table_id=table['table_id']
                elif 'ads_contents' == table['name'].lower():
                    ads_content_table_id=table['table_id']
                elif 'huggingface_spaces' == table['name'].lower():
                    huggingface_spaces_table_id=table['table_id']
            conditions_array=[
                {
                    'field_name':'TYPE',
                    'operator':'contains',
                    'value':['gate_process_for_stream']
                },
                {
                    'field_name':'STATUS',
                    'operator':'contains',
                    'value':['alive']
                }
            ]
            while True:
                rs=await lark.search_record(app_token=APP_TOKEN,table_id=huggingface_spaces_table_id,conditions_array=conditions_array)
                if rs and 'total' in rs and rs['total']>0:
                    GATE_PROCESS_URL=rs['items'][0]['fields']['URL'][0]['text']
                    if 'huggingface.co' in GATE_PROCESS_URL:
                            st=GATE_PROCESS_URL.split('/')
                            GATE_PROCESS_URL=f"https://{st[4]}-{st[5]}.hf.space/"
                    GATE_PROCESS_URL=GATE_PROCESS_URL+('/' if GATE_PROCESS_URL[-1] !='/' else '')
                    break
                await asyncio.sleep(.5)
            if GATE_PROCESS_URL:
                stop=False
                page_token=None
                records=[]
                i=0
                conditions_array=[
                    {
                        'field_name':'STATUS',
                        'operator':'contains',
                        'value':['alive']
                    },
                    {
                        'field_name':'STREAMING_STATUS',
                        'operator':'doesNotContain',
                        'value':['live']
                    }
                ]
                while not stop:
                    try:
                        rs=await lark.search_record(APP_TOKEN,accounts_table_id,page_token=page_token,conditions_array=conditions_array)
                        if rs and rs['total']>0:
                            for item in rs['items']:
                                records.append(item)
                        if rs['has_more']:
                            page_token=rs['page_token']
                        else:
                            stop=True
                    except Exception as err:
                        print(err)
                    await asyncio.sleep(1)
                run_first=False
                for record in records:
                    try:
                        record_id=record['record_id']
                        record=record['fields']
                        secret_key=''
                        if 'KEY' in record and len(record['KEY'])>0:
                            for item in record['KEY']:
                                if item['type']=='text':
                                    secret_key+=item['text']
                        email=''
                        if 'EMAIL' in record and len(record['EMAIL'])>0:
                            for item in record['EMAIL']:
                                if item['type']=='url':
                                    email+=item['text']
                        profile_url=''
                        if 'PROFILE_URL' in record and len(record['PROFILE_URL'])>0:
                            profile_url=  record['PROFILE_URL']['text']
                        rtmp_server=record['RTMP_SERVER'] if 'RTMP_SERVER' in record else None
                        rtmp_server=rtmp_server+('/' if rtmp_server[-1]!='/' else '')
                        if (('STREAMING_STATUS' not in record or record['STREAMING_STATUS']=='offline') or (int(datetime.now().timestamp())-record['UPDATED_AT']/1000>1200)) and 'STATUS' in record and record['STATUS']=='alive' and all([item!='' for item in [secret_key,rtmp_server,email]]) and not run_first:# and 'CONTENT_FROM' in record and len(record['CONTENT_FROM'][0]['text_arr'])>0:
                            process_id=f"{email}-|-{rtmp_server}-|-{secret_key}"
                            life_time=1200
                            response=await create_new_process(lark,process_id,life_time)
                            if response:
                                lark=basic.LarkClass(app_id=response['lark_app_info']['lark_app_id'],app_secret=response['lark_app_info']['lark_app_secret'])
                                ads_records=[]
                                page_token1=None
                                conditions_array=[
                                    {
                                        'field_name':'STREAMING_ACCOUNTS',
                                        'operator':'contains',
                                        'value':[record_id]
                                    }
                                ]
                                while True:
                                    rs=await lark.search_record(APP_TOKEN,ads_content_table_id,conditions_array,page_token=page_token)
                                    if rs:
                                        if 'items' in rs:
                                            ads_records+=rs['items']
                                        if rs['has_more']:
                                            page_token=rs['page_token']
                                        else:
                                            break
                                if rtmp_server and secret_key:
                                    run_first=True
                                    streamers=[]
                                    page_token1=None
                                    while True:
                                        rs=await lark.get_list_record(APP_TOKEN,streamers_table_id,page_token=page_token1)
                                        if rs:
                                            if 'items' in rs:
                                                streamers+=rs['items']
                                            if rs['has_more']:
                                                page_token=rs['page_token']
                                            else:
                                                break
                                    while True:
                                        rs=await lark.update_record(APP_TOKEN,accounts_table_id,record_id,{'STREAMING_STATUS':'live'})
                                        await asyncio.sleep(3)
                                        if rs:
                                            rs=rs['record']
                                            media_using_array=[]
                                            streamer_using_array=[]
                                            stop1=False
                                            page_token1=None
                                            while not stop1:
                                                records1=await lark.get_list_record(APP_TOKEN,accounts_table_id,page_token=page_token1)
                                                if records1:
                                                    if records1['has_more']:
                                                        page_token1=records1['page_token']
                                                    else:
                                                        stop1=True
                                                    for record1 in records1['items']:
                                                        record1_id=record1['record_id']
                                                        record1=record1['fields']
                                                        if record1_id!=record_id and 'STREAMING_STATUS' in record1 and 'STREAMING_STATUS' in record1 and record1['STREAMING_STATUS']=='live' and len(record1['STREAMING_ON'][0]['text_arr'])>0:
                                                            media_using_array.append(record1['STREAMING_ON'][0])
                                            for item in media_using_array:
                                                info_media=(await lark.get_record(APP_TOKEN,item['table_id'],item['record_ids'][0]))
                                                if info_media:
                                                    info_media=info_media['record']
                                                    streamer_using_array.append(info_media['fields']['STREAMED_BY'][0])
                                            if 'CONTENT_FROM' in record and 'link_record_ids' in record['CONTENT_FROM']:
                                                streamer_record_id=record['CONTENT_FROM']['link_record_ids'][0]
                                                media_array=[]
                                                stop1=False
                                                page_token1=None
                                                first=False
                                                while not stop1:
                                                    conditions_array=[
                                                        {
                                                            'field_name':'STREAMED_BY',
                                                            'operator':'contains',
                                                            'value':[streamer_record_id]
                                                        }
                                                    ]
                                                    records1=await lark.search_record(APP_TOKEN,media_table_id,conditions_array=conditions_array,page_token=page_token1)
                                                    if records1:
                                                            if records1['has_more']:
                                                                page_token1=records1['page_token']
                                                            else:
                                                                stop1=True
                                                            if 'items' in records1:
                                                                media_array+=records1['items']
                                                grouped_by_source = defaultdict(list)
                                                for item in media_array:
                                                    if item['fields']['PART'][0]['text'] not in str(grouped_by_source[item['fields']['VIDEO_SOURCE']['text']]):
                                                        grouped_by_source[item['fields']['VIDEO_SOURCE']['text']].append(item)
                                                for item in grouped_by_source:
                                                    grouped_by_source[item] = sorted(grouped_by_source[item], key=lambda x: x['fields']['PART'][0]['text'])
                                                result=list(grouped_by_source)
                                                random_content=random.choice(result) if len(result)>0 else None
                                                if len(result)>0:
                                                    i=0
                                                    for item in grouped_by_source[random_content]:
                                                        while True:
                                                            rs=await lark.update_record(APP_TOKEN,accounts_table_id,record_id,{'STREAMING_ON':[item['record_id']]})
                                                            if rs:
                                                                break
                                                            await asyncio.sleep(1)
                                                        duration_file=await get_video_duration(item['fields']['URL']['text'])
                                                        ffmpeg_command=[
                                                            "ffmpeg",
                                                            "-re",
                                                            "-i", f"{item['fields']['URL']['text']}",
                                                            "-vf","drawtext=text='contact for work':x=10:y=10:fontsize=42:fontcolor=red:box=1:boxcolor=white@0.8:boxborderw=5",
                                                            "-c:v", "libx264",
                                                            "-preset", "veryfast",
                                                            "-maxrate", "3000k",
                                                            "-bufsize", "6000k",
                                                            "-pix_fmt", "yuv420p",  
                                                            "-vf", "format=yuv420p",
                                                            "-g", "50",
                                                            "-c:a", "aac",
                                                            "-b:a", "128k",
                                                            "-ar", "44100",
                                                            "-f", "flv",
                                                            #'-loglevel','error',
                                                            f"{rtmp_server}{secret_key}",
                                                        ]
                                                        ffmpeg_command=run_ffmpeg_with_text('Contact me for work!', 15, 35, 20, 20, f"{item['fields']['URL']['text']}", f"{rtmp_server}{secret_key}", 'slide_right_to_left')
                                                        if len(ads_records)>0:
                                                            ads_record=random.choice(ads_records)
                                                            point_a=eval(ads_record['fields']['POINT_A']) if 'POINT_A' in ads_record['fields'] else (1920,20)
                                                            point_b=eval(ads_record['fields']['POINT_B']) if 'POINT_B' in ads_record['fields'] else (20,20)
                                                            point_c=eval(ads_record['fields']['POINT_C']) if 'POINT_C' in ads_record['fields'] else (-200,20)
                                                            start_time=ads_record['fields']['BEGIN_AT'] if 'BEGIN_AT' in ads_record['fields'] else 0
                                                            time_a_b=ads_record['fields']['TIME_A_B'] if 'TIME_A_B' in ads_record['fields'] else 2
                                                            time_hold_b=ads_record['fields']['TIME_HOLD_B'] if 'TIME_HOLD_B' in ads_record['fields'] else int(duration_file)
                                                            time_b_c=ads_record['fields']['TIME_B_C'] if 'TIME_B_C' in ads_record['fields'] else 2
                                                            img_url=ads_record['fields']['IMAGE_FILE'][0]['url']
                                                            image_path=await lark.download_file(img_url,'ads_image')
                                                            if image_path:
                                                                obj=Obj1(image_path=image_path if 'image_path' in locals() else None,point_a=point_a,point_b=point_b,point_c=point_c,start_time=start_time,time_a_b=time_a_b,time_hold_at_b=time_hold_b,time_b_c=time_b_c)
                                                                ffmpeg_command=FFMPEG_CMD.create_ffmpeg_command_with_repeat(input_video=item['fields']['URL']['text'],rtmp_url=f"{rtmp_server}{secret_key}",obj=obj)
                                                                rs=await stream_video(email,profile_url,duration_file,ffmpeg_command)
                                                        if rs==True or rs==False:
                                                            i+=1
                                                        await asyncio.sleep(2)
                                                if not random_content or i==len(grouped_by_source[random_content]):
                                                    while True:
                                                        rs=await lark.update_record(APP_TOKEN,accounts_table_id,record_id,{'STREAMING_STATUS':'offline','STREAMING_ON':[],'STREAMING_BY':[]})
                                                        if rs:
                                                            break
                                                        await asyncio.sleep(1)
                                                    await update_complete_process(lark,response['new_process_record_id'])
                                            else:
                                                media_array=[]
                                                stop1=False 
                                                page_token1=None
                                                random_choice_streamer=random.choice(streamers)
                                                first=False
                                                while not stop1:
                                                    conditions_array=[
                                                        {
                                                            'field_name':'STREAMED_BY',
                                                            'operator':'contains',
                                                            'value':[random_choice_streamer['record_id']]
                                                        }
                                                    ]
                                                    records1=await lark.search_record(APP_TOKEN,media_table_id,conditions_array=conditions_array,page_token=page_token1)
                                                    if records1:
                                                        if records1['total']<1 and not first:
                                                            random_choice_streamer=random.choice(streamers)
                                                        elif not records1['has_more'] and first:
                                                            break
                                                        else:
                                                            first=True
                                                            if records1['has_more']:
                                                                page_token1=records1['page_token']
                                                            media_array+=records1['items']
                                                media_array_filter=[]
                                                for item in streamer_using_array:
                                                    for record1 in media_array:
                                                        if item['record_ids'][0] not in str(record1):
                                                            media_array_filter.append(record1) 
                                                grouped_by_source = defaultdict(list)
                                                for item in media_array_filter:
                                                    if item['fields']['PART'][0]['text'] not in str(grouped_by_source[item['fields']['STREAMED_BY']['link_record_ids'][0]]):
                                                        grouped_by_source[item['fields']['STREAMED_BY']['link_record_ids'][0]].append(item)
                                                for item in grouped_by_source:
                                                    grouped_by_source[item] = sorted(grouped_by_source[item], key=lambda x: x['fields']['PART'][0]['text'])
                                                result=list(grouped_by_source)
                                                random_content=random.choice(result) if len(result)>0 else None
                                                if len(result)>0:
                                                    i=0
                                                    for item in grouped_by_source[random_content]:
                                                        while True:
                                                            rs=await lark.update_record(APP_TOKEN,accounts_table_id,record_id,{'STREAMING_ON':[item['record_id']]})
                                                            if rs:
                                                                break
                                                            await asyncio.sleep(1)
                                                        duration_file=await get_video_duration(item['fields']['URL']['text'])
                                                        ffmpeg_command=[
                                                            "ffmpeg",
                                                            "-re",
                                                            "-i", f"{item['fields']['URL']['text']}",
                                                            "-vf","drawtext=text='contact for work':x=10:y=10:fontsize=42:fontcolor=red:box=1:boxcolor=white@0.8:boxborderw=5",
                                                            "-c:v", "libx264",
                                                            "-preset", "veryfast",
                                                            "-maxrate", "3000k",
                                                            "-bufsize", "6000k",
                                                            "-pix_fmt", "yuv420p",  
                                                            "-vf", "format=yuv420p",
                                                            "-g", "50",
                                                            "-c:a", "aac",
                                                            "-b:a", "128k",
                                                            "-ar", "44100",
                                                            "-f", "flv",
                                                            #'-loglevel','error',
                                                            f"{rtmp_server}{secret_key}",
                                                        ]
                                                        ffmpeg_command=run_ffmpeg_with_text('Contact me for work!', 15, 35, 20, 20, f"{item['fields']['URL']['text']}", f"{rtmp_server}{secret_key}", 'slide_right_to_left')
                                                        if len(ads_records)>0:
                                                            ads_record=random.choice(ads_records)
                                                            point_a=eval(ads_record['fields']['POINT_A']) if 'POINT_A' in ads_record['fields'] else (1920,20)
                                                            point_b=eval(ads_record['fields']['POINT_B']) if 'POINT_B' in ads_record['fields'] else (20,20)
                                                            point_c=eval(ads_record['fields']['POINT_C']) if 'POINT_C' in ads_record['fields'] else (-200,20)
                                                            start_time=ads_record['fields']['BEGIN_AT'] if 'BEGIN_AT' in ads_record['fields'] else 0
                                                            time_a_b=ads_record['fields']['TIME_A_B'] if 'TIME_A_B' in ads_record['fields'] else 2
                                                            time_hold_b=ads_record['fields']['TIME_HOLD_B'] if 'TIME_HOLD_B' in ads_record['fields'] else int(duration_file)
                                                            time_b_c=ads_record['fields']['TIME_B_C'] if 'TIME_B_C' in ads_record['fields'] else 2
                                                            img_url=ads_record['fields']['IMAGE_FILE'][0]['url']
                                                            image_path=await lark.download_file(img_url,'ads_image')
                                                            obj=Obj1(image_path=image_path if 'image_path' in locals() else None,point_a=point_a,point_b=point_b,point_c=point_c,start_time=start_time,time_a_b=time_a_b,time_hold_at_b=time_hold_b,time_b_c=time_b_c)
                                                            ffmpeg_command=FFMPEG_CMD.create_ffmpeg_command_with_repeat(input_video=item['fields']['URL']['text'],rtmp_url=f"{rtmp_server}{secret_key}",obj=obj)
                                                        rs=await stream_video(email,profile_url,duration_file,ffmpeg_command)
                                                        if i==True or i==False:
                                                            i+=1
                                                        await asyncio.sleep(2)
                                                if not random_content or i==len(grouped_by_source[random_content]):
                                                    while True:
                                                        rs=await lark.update_record(APP_TOKEN,accounts_table_id,record_id,{'STREAMING_STATUS':'offline','STREAMING_ON':[],'STREAMING_BY':[]})
                                                        if rs:
                                                            break
                                                        await asyncio.sleep(1)
                                                    await update_complete_process(lark,response['new_process_record_id'])
                                            await asyncio.sleep(1)
                                            break
                    except Exception as err:
                        traceback.print_exc()
                        pass
                break
            else:
                print('ERROR- NEED A GATE PROCESS TO CREATE UNIQUE PROCESSING')
            await asyncio.sleep(1)
            break
async def main():
    try:
        req=requests.get('http://localhost:8888')
        if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
            raise Exception("Server not response")
        sys.exit("Exited")
    except Exception as error:
        print(error)
        server.b() 
        while True:
            try:
                lark=basic.LarkClass(APP_ID,APP_SECRET)
                await run_command(lark)
            except:
                traceback.print_exc()
            await asyncio.sleep(5)
asyncio.run(main())
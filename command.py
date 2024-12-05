import subprocess
from PIL import Image
from pydantic import BaseModel, ValidationError
import os
import requests
from urllib.parse import urlsplit

def url_to_file(url,file_name,ext):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = ext
            if 'image' in content_type:
                file_extension = '.' + content_type.split('/')[1]
            elif 'video' in content_type: 
                file_extension = '.' + content_type.split('/')[1]
            elif 'pdf' in content_type:
                file_extension = '.pdf'
            elif 'text' in content_type:
                file_extension = '.txt'
            else:
                file_extension = '.bin'
            file_name = file_name + file_extension
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Tệp đã được tải xuống thành công và lưu thành {file_name}.")
            return file_name
        else:
            print(f"Lỗi tải tệp: {response.status_code}")
    except:
        print('Can\'t download file')
    return False
class Obj1(BaseModel):
    image_path:str
    point_a:tuple[int,int]
    point_b:tuple[int,int]
    point_c:tuple[int,int]
    start_time:int
    time_a_b:int
    time_hold_at_b:int
    time_b_c:int
class FFMPEG_CMD:
    def __init__(self):
        pass
    def create_ffmpeg_command_with_repeat(input_video,rtmp_url,obj:Obj1,repeat_time=1,repeat_each=10):
        if obj.image_path:
            xA, yA = obj.point_a
            xB, yB = obj.point_b
            xC, yC = obj.point_c # Thay thế bằng đường dẫn tới ảnh của bạn
            start_time=obj.start_time
            time_a_b=obj.time_a_b
            time_hold_at_b=obj.time_hold_at_b
            time_b_c=obj.time_b_c
            duration=time_hold_at_b+time_a_b+time_b_c
            image = Image.open(obj.image_path)
            width, height = image.size
            st=''
            if repeat_time>1:
                for i in range(repeat_time):
                    start_time=start_time if i==0 else start_time+duration+repeat_each
                    st+=f"""{'[0][1]' if i==0 else f'[out{i-1}][1]'}overlay=enable='between(t,{start_time},{start_time+duration})':x='if(lt(t,{start_time+time_a_b}), {xA+width} + ({xB}-{xA+width})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {xB}, {xB} + ({xC}-{xB+width})*(t-{start_time+duration-time_a_b})/{time_b_c}))':y='if(lt(t,{start_time+time_a_b}), {yA} + ({yB}-{yA})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {yB}, {yB} + ({yC}-{yB})*(t-{start_time+duration-time_a_b})/{time_b_c}))'[out{i if i !=repeat_time-1 else ''}];
                        """
            else:
                st=f"""[0][1]overlay=enable='between(t,{start_time},{start_time+duration})':x='if(lt(t,{start_time+time_a_b}), {xA+width} + ({xB}-{xA+width})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {xB}, {xB} + ({xC}-{xB+width})*(t-{start_time+duration-time_a_b})/{time_b_c}))':y='if(lt(t,{start_time+time_a_b}), {yA} + ({yB}-{yA})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {yB}, {yB} + ({yC}-{yB})*(t-{start_time+duration-time_a_b})/{time_b_c}))';
                    """
        ffmpeg_command = ['ffmpeg']
        if obj.image_path:
            if repeat_time==1:
                ffmpeg_command+=['-re']
            ffmpeg_command+=[
                '-i', f'{input_video}',
                '-i', f'{obj.image_path}',
                '-filter_complex', f'{st.strip()}']
            if repeat_time>1:
                ffmpeg_command+=['-map','[out]']
        else:
            ffmpeg_command+=["-vf", "format=yuv420p"]
        ffmpeg_command+=[
            '-c:v', 'libx264', 
            '-preset', 'veryfast', 
            '-maxrate', '3000k', 
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p', 
            '-g', '50', 
            '-c:a', 'aac', 
            '-b:a', '128k', 
            '-ar', '44100',
            '-f', 'flv', 
            f'{rtmp_url}'
        ]
        return ffmpeg_command
    def create_ffmpeg_command_with_multi_items(input_video,rtmp_url,array_object):
        if len(array_object)>1:
            last_output=None
            first_output=None
            st=''
            arr=[]
            for idx,obj in enumerate(array_object):
                xA, yA = obj.point_a
                xB, yB = obj.point_b
                xC, yC = obj.point_c 
                start_time=obj.start_time
                time_a_b=obj.time_a_b
                time_hold_at_b=obj.time_hold_at_b
                time_b_c=obj.time_b_c
                duration=time_hold_at_b+time_a_b+time_b_c
                image = Image.open(obj.image_path)
                width, height = image.size
                repeat_time=obj.repeat_time
                repeat_each=obj.repeat_each
                st=f'movie={obj.image_path}[img{idx}];'
                for i in range(repeat_time):
                    start_time=start_time if i==0 else start_time+duration+repeat_each
                    it=f"""overlay=enable='between(t,{start_time},{start_time+duration})':x='if(lt(t,{start_time+time_a_b}), {xA+width} + ({xB}-{xA+width})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {xB}, {xB} + ({xC}-{xB+width})*(t-{start_time+duration-time_a_b})/{time_b_c}))':y='if(lt(t,{start_time+time_a_b}), {yA} + ({yB}-{yA})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {yB}, {yB} + ({yC}-{yB})*(t-{start_time+duration-time_a_b})/{time_b_c}))'
                        """
                    arr.append(it)
                big_st=''
                for i,item in enumerate(arr):
                    big_st+=f"[0][img{idx}]"+item+'[]'
        else:
            xA, yA = obj.point_a
            xB, yB = obj.point_b
            xC, yC = obj.point_c 
            start_time=obj.start_time
            time_a_b=obj.time_a_b
            time_hold_at_b=obj.time_hold_at_b
            time_b_c=obj.time_b_c
            duration=time_hold_at_b+time_a_b+time_b_c
            image = Image.open(obj.image_path)
            width, height = image.size
            repeat_time=obj.repeat_time
            repeat_each=obj.repeat_each
            st=f'movie={obj.image_path}[img];'
            if repeat_time>1:
                for i in range(repeat_time):
                    start_time=start_time if i==0 else start_time+duration+repeat_each
                    st+=f"""{'[0][img]' if i==0 else f'[out{i-1}][1]'}overlay=enable='between(t,{start_time},{start_time+duration})':x='if(lt(t,{start_time+time_a_b}), {xA+width} + ({xB}-{xA+width})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {xB}, {xB} + ({xC}-{xB+width})*(t-{start_time+duration-time_a_b})/{time_b_c}))':y='if(lt(t,{start_time+time_a_b}), {yA} + ({yB}-{yA})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {yB}, {yB} + ({yC}-{yB})*(t-{start_time+duration-time_a_b})/{time_b_c}))'[out{i if i !=repeat_time-1  else ''}];
                        """
            else:
                st+=f"""[0][img]overlay=enable='between(t,{start_time},{start_time+duration})':x='if(lt(t,{start_time+time_a_b}), {xA+width} + ({xB}-{xA+width})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {xB}, {xB} + ({xC}-{xB+width})*(t-{start_time+duration-time_a_b})/{time_b_c}))':y='if(lt(t,{start_time+time_a_b}), {yA} + ({yB}-{yA})*(t-{start_time})/{time_a_b}, if(lt(t,{start_time+duration-time_a_b}), {yB}, {yB} + ({yC}-{yB})*(t-{start_time+duration-time_a_b})/{time_b_c}))'[out];
                    """
        ffmpeg_command = ['ffmpeg']
        if repeat_time==1:
            ffmpeg_command+=['-re']
        ffmpeg_command+=[
            '-i', input_video,
            '-i', obj.image_path,
            '-filter_complex', st]
        ffmpeg_command+=['-map','[out]']
        ffmpeg_command+=[
            '-c:v', 'libx264', 
            '-preset', 'veryfast', 
            '-maxrate', '3000k', 
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p', 
            '-g', '50', 
            '-c:a', 'aac', 
            '-b:a', '128k', 
            '-ar', '44100',
            '-f', 'flv', 
            rtmp_url
        ]
        return ffmpeg_command

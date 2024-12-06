import subprocess
import os,sys
import server
import requests
import datetime
import asyncio
import main as main1

async def main():
    try:
        req=requests.get('http://localhost:8888')
        if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
            raise Exception("Server not response")
        sys.exit("Exited")
    except Exception as error:
        server.b()
        run_command = [
            "python3", "main.py"
        ]
        main1.test()
        '''run_command = [
            "python", "main.py"
        ]
        try:
            process = subprocess.run(run_command)
            returncode = process.returncode
            if returncode != 0:
                print(f"FFmpeg process ended with error code {returncode}")
                return False
            return True
        except asyncio.TimeoutError:
            print("Timeout reached, killing the ffmpeg process.")
            process.kill()  # Kill process nếu hết thời gian chờ
            await process.wait()  # Đảm bảo tiến trình kết thúc'''
        '''project_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn tuyệt đối tới thư mục chứa file Python
        

        # Thực thi lệnh chạy Docker container
        try:
            result = subprocess.run(run_command, check=True, capture_output=True, text=True)
            print("Docker container is running!")
            print(result.stdout)  # In ra thông báo thành công từ Docker
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running Docker container: {e}")
            print(e.stderr)  # In ra thông báo lỗi nếu có'''
asyncio.run(main())
import subprocess
import os,sys
import server
import requests
import datetime

try:
    req=requests.get('http://localhost:8888')
    if int(str(datetime.datetime.now().timestamp()).split('.')[0])-int(req.text.split('.')[0])>=10:
        raise Exception("Server not response")
    sys.exit("Exited")
except Exception as error:
    server.b()

    project_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn tuyệt đối tới thư mục chứa file Python
    run_command = [
        "python", "main.py"
    ]

    # Thực thi lệnh chạy Docker container
    try:
        result = subprocess.run(run_command, check=True, capture_output=True, text=True)
        print("Docker container is running!")
        print(result.stdout)  # In ra thông báo thành công từ Docker
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Docker container: {e}")
        print(e.stderr)  # In ra thông báo lỗi nếu có
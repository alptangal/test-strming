import subprocess
import os

project_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn tuyệt đối tới thư mục chứa file Python
run_command = [
    "docker", "run", "-p", "7860:7860", "Dockerfile"
]

# Thực thi lệnh chạy Docker container
try:
    result = subprocess.run(run_command, check=True, capture_output=True, text=True)
    print("Docker container is running!")
    print(result.stdout)  # In ra thông báo thành công từ Docker
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running Docker container: {e}")
    print(e.stderr)  # In ra thông báo lỗi nếu có
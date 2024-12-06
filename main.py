import requests
import time

def test():
    while True:
        req=requests.get('http://127.0.0.1:8888')
        print(req.status_code)
        time.sleep(3)
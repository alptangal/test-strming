import requests
import time

def test():
    while True:
        req=requests.get('http://localhost:8888')
        print(req.status_code)
        time.sleep(3)
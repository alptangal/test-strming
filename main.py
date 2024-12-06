import requests
import time

def test():
    while True:
        req=requests.get('https://test-strming-acjbcxftehuxflusvskipn.streamlit.app/')
        print(req.status_code)
        time.sleep(3)
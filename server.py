from flask import Flask
from threading import Thread
import datetime

app = Flask('')

@app.route('/')
def main():
    return str(datetime.datetime.now().timestamp())

def run():
    app.run(host='0.0.0.0', port=8888)

def b():
    server = Thread(target=run)
    server.start()
    
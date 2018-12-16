from clarifai import rest
from clarifai.rest import ClarifaiApp
import signal
import sys
import websocket
import json
import requests
import SSD1331
import _thread
import time
import datetime
import os
import picamera
import threading

your_access_token = "o.jd9hKkopWYUYLiyVOBnnHMeHYWH7A4EU"
url_base = "https://api.pushbullet.com/v2/"

def signal_handler(sig, frame):
        global clock
        clock=False
        device.Clear()
        cam.resolution = (480, 360)
        y = 2
        print ('taking snapshot')
        cam.capture('snapshot.jpg')

        d = model.predict_by_filename('snapshot.jpg')

        for i in d['outputs'][0]['data']['concepts']:
                if(y<5):
                        y = y+1
                        print (i['name'])
                        device.DrawString(30, y*10, i['name'], SSD1331.COLOR_WHITE)
        time.sleep(5)
        device.Clear()
        clock=True

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

def run_clock():
        while True:
                if clock:
                        my_now = datetime.datetime.now()
                        today_date = my_now.strftime("%B-%d")
                        today_day = my_now.strftime("%A")
                        today_time = my_now.strftime("%H:%M:%S")
                        device.DrawString(15, 20, str(today_time), SSD1331.COLOR_WHITE)
                        device.DrawString(15, 30, str(today_date), SSD1331.COLOR_WHITE)
                        device.DrawString(15, 30, str(today_day), SSD1331.COLOR_WHITE)
                        time.sleep(1)

def on_message(ws, raw):
        global clock
        clock=False
        device.Clear()

        data = json.loads(raw)
        print (json.dumps(data,indent=2))
        global modified

        try:
                type = data['type']
        except:
                print ("Error in reading the type")

        if type == "push":
                try:
                        application=data['push']['application_name']
                        device.DrawString(5, 20, application, SSD1331.COLOR_WHITE)
                        print (data['push']['application_name'])
                except:
                        print ("error in application name")
                try:
                        title=data['push']['title'].rsplit(' (',1)[0]
                        device.DrawString(5, 30, title, SSD1331.COLOR_WHITE)
                        print (data['push']['title'])
                except:
                        print ("error in title")
                try:
                        body=data['push']['body'].rsplit('\n',1)[-1]
                        device.DrawString(5, 40, body, SSD1331.COLOR_WHITE)
                        print (data['push']['body'])
                except:
                        print ("error in body")

                time.sleep(5)
                device.Clear()

        elif type == "tickle":
                url_pushes = url_base+"pushes?modified_after="+str(modified)
                response = requests.get(url=url_pushes, headers=headers)
                data=response.json()
                print (json.dumps(data,indent=2))
                try:
                        modified = data['pushes'][0]['modified']
                except:
                        print ("not a traditional push")
                for push in data['pushes']:
                        try:
                                body=push['body'].rsplit('\n',1)[-1]
                                print(body)
                                if(body=="cam"):
                                        os.kill(os.getpid(), signal.SIGTSTP)
                                else:
                                        device.DrawString(30, 20, "message", SSD1331.COLOR_WHITE)
                                        device.DrawString(30, 30, body, SSD1331.COLOR_WHITE)
                                        time.sleep(5)
                                        device.Clear()
                        except:
                                print ("error in reading message")

        clock=True

def on_error(ws, error):
        print (error)

def on_close(ws):
        device.EnableDisplay(False)
        device.Remove()
        print ("### closed ###")

url_pushes = url_base+"pushes"
headers = { 'Access-Token': your_access_token,
            'Content-Type': 'application/json',}

try:
        app = ClarifaiApp(api_key='a653edc0184247e0a6b61c556ca691a8')
except:
        print ("error in clarifai")
try:
        model = app.public_models.general_model
except:
        print ("error in getting model")

model.model_version = 'aa7f35c01e0642fda5cf400f543e7c40'

device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
device.EnableDisplay(True)
device.Clear()

cam = picamera.PiCamera()

response = requests.get(url=url_pushes, headers=headers)
data = response.json()
modified = data['pushes'][0]['modified']

#print (type(modified))
#print (modified)

signal.signal(signal.SIGTSTP, signal_handler)

clock=True
t1 = threading.Thread(target=run_clock, name='t1')
t1.start()

websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/"+your_access_token,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)

ws.run_forever()

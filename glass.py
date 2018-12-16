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
import math

your_access_token = "o.jd9hKkopWYUYLiyVOBnnHMeHYWH7A4EU"
url_base = "https://api.pushbullet.com/v2/"

def upload_file():
        url_request = url_base+"upload-request"
        data = json.dumps({'file_name': 'snapshot.jpg',
                            'file_type': 'image/jpeg'})

        res = requests.post(url=url_request, data=data, headers=headers)
        if res.status_code != 200:
                raise Exception('failed to request upload')
        r = res.json()
        res = requests.post(r['upload_url'], data=r['data'], files={'file': open('snapshot.jpg', 'rb')})
        if res.status_code != 204:
                raise Exception('failed to upload file')

        print (r['file_name'], "url: ", r['file_url'])

        url_pushes = url_base+"pushes"
        data = json.dumps({'file_name': r['file_name'],
                           'file_type': r['file_type'],
                           'file_url': r['file_url'],
                           'type': 'file'})
        res = requests.post(url=url_pushes, data=data, headers=headers)

def signal_handler(sig, frame):
        global clock
        clock=False
        device.Clear()
        cam.resolution = (480, 360)
        y = 2
        print ('taking snapshot')
        cam.capture('snapshot.jpg')

        t2 = threading.Thread(target=upload_file, name='t2')
        t2.start()

        d = model.predict_by_filename('snapshot.jpg')

        for i in d['outputs'][0]['data']['concepts']:
                if(y<5):
                        y = y+1
                        print (i['name'])
                        device.DrawString(15, y*10, i['name'], SSD1331.COLOR_WHITE)
        time.sleep(5)
        device.Clear()
        clock=True

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25


def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

def run_clock():
        while True:
                if clock:
                        device.Clear()
                        my_now = datetime.datetime.now()
                        today_date = my_now.strftime("%b-%d")
                        today_day = my_now.strftime("%a")
                        today_time = my_now.strftime("%H:%M")
                        device.DrawString(60, 20, str(today_time), SSD1331.COLOR_WHITE)
                        device.DrawString(60, 30, str(today_date), SSD1331.COLOR_WHITE)
                        device.DrawString(60, 40, str(today_day), SSD1331.COLOR_WHITE)
                        hours_angle = 270 + (30 * (my_now.hour + (my_now.minute / 60.0)))
                        hours_dx = int(math.cos(math.radians(hours_angle)) * 12)
                        hours_dy = int(math.sin(math.radians(hours_angle)) * 12)
                        minutes_angle = 270 + (6 * my_now.minute)
                        minutes_dx = int(math.cos(math.radians(minutes_angle)) * 18)
                        minutes_dy = int(math.sin(math.radians(minutes_angle)) * 18)
                        device.DrawCircle(28, 32, 28, SSD1331.COLOR_RED)
                        device.DrawLine(28, 32, 30 + hours_dx, 32 + hours_dy, SSD1331.COLOR_WHITE)
                        device.DrawLine(28, 32, 30+ minutes_dx, 32 + minutes_dy, SSD1331.COLOR_WHITE)
                        #device.DrawString(60, 28, today_time, SSD1331.COLOR_WHITE)
                        time.sleep(3)

def on_message(ws, raw):
        global clock

        device.Clear()

        data = json.loads(raw)
        print (json.dumps(data,indent=2))
        global modified

        try:
                type = data['type']
        except:
                print ("Error in reading the type")

        if type == "push":
                clock=False
                device.Clear()
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
                        clock=False
                        device.Clear()
                        try:
                                body=push['body'].rsplit('\n',1)[-1]
                                print(body)
                                if(body=="Cam"):
                                        os.kill(os.getpid(), signal.SIGTSTP)
                                else:
                                        device.DrawString(5, 20, "Message", SSD1331.COLOR_WHITE)
                                        device.DrawString(5, 30, body, SSD1331.COLOR_WHITE)
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
            'Content-Type': 'application/json'}

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

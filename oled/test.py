from clarifai import rest
from clarifai.rest import ClarifaiApp
import datetime
import json
import picamera
import SSD1331
import signal
import sys
import time

def signal_handler(sig, frame):
	device.Clear()
	y = 0
	print ('taking snapshot')
	cam.capture('snapshot.jpg')

	d = model.predict_by_filename('snapshot.jpg')

	for i in d['outputs'][0]['data']['concepts']:
		if(y<3):
			y = y+1
			print (i['name'])
			device.DrawString(30, y*10, i['name'], SSD1331.COLOR_WHITE)


SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

app = ClarifaiApp(api_key='a653edc0184247e0a6b61c556ca691a8')
model = app.models.get('general-v1.3')

device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
device.EnableDisplay(True)
device.Clear()

cam = picamera.PiCamera()
cam.resolution = (480, 360)

signal.signal(signal.SIGTSTP, signal_handler)
time.sleep(500)

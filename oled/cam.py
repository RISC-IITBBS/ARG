from clarifai import rest
from clarifai.rest import ClarifaiApp
import datetime
import json
import picamera
import SSD1331

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

time1 = datetime.datetime.now()
app = ClarifaiApp(api_key='a653edc0184247e0a6b61c556ca691a8')
model = app.models.get('general-v1.3')
#model = app.public_models.general_model
time2 = datetime.datetime.now()
print (time2-time1)
device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
device.EnableDisplay(True)
device.Clear()
y = 0

cam = picamera.PiCamera()
cam.resolution = (480, 360)
cam.capture('snapshot.jpg')

d = model.predict_by_filename('snapshot.jpg')
device.Clear()

for i in d['outputs'][0]['data']['concepts']:
	if(y<3):
		y = y+1
		#print (i['name'])
		device.DrawString(30, y*10, i['name'], SSD1331.COLOR_WHITE)

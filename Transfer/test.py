from clarifai import rest
from clarifai.rest import ClarifaiApp
import datetime
import json
import picamera
import SSD1331

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

#time1 = datetime.datetime.now()

app = ClarifaiApp(api_key='a653edc0184247e0a6b61c556ca691a8')
model = app.models.get('general-v1.3')
device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
device.EnableDisplay(True)
device.Clear()
y = 0

while(True):
	#time2 = datetime.datetime.now()
	cam = picamera.PiCamera()
	cam.resolution = (480, 360)
	cam.capture('snapshot.jpg')

	#time3 = datetime.datetime.now()

	d = model.predict_by_filename('snapshot.jpg')

	device.Clear()
	for i in d['outputs'][0]['data']['concepts']:
        	if(i['value']>0.95):
        		y = y+5
        		device.DrawString(40, y, i['name'], SSD1331.COLOR_WHITE)

	#print('\n\n')
	#time.sleep(4)
	#time4 = datetime.datetime.now()
	#print("Time Delay: "+str(time2-time1)+" "+str(time3-time2)+" "+str(time4-time3))

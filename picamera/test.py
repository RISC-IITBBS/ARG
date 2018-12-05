from clarifai import rest
from clarifai.rest import ClarifaiApp
import datetime
import json
import picamera
import time

#time1 = datetime.datetime.now()

app = ClarifaiApp(api_key='a653edc0184247e0a6b61c556ca691a8')
model = app.models.get('general-v1.3')

#time2 = datetime.datetime.now()
cam = picamera.PiCamera()
cam.resolution = (480, 360)
cam.capture('snapshot.jpg')
#time3 = datetime.datetime.now()
d = model.predict_by_filename('snapshot.jpg')

for i in d['outputs'][0]['data']['concepts']:
	if(i['value']>0.94):
		print(i['name'])
#time.sleep(1)

#print('\n\n')
#time.sleep(4)
#time4 = datetime.datetime.now()
#print("Time Delay: "+str(time2-time1)+" "+str(time3-time2)+" "+str(time4-time3))

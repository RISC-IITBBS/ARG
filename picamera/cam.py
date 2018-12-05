import picamera
import time

cam = picamera.PiCamera()

# Settings
cam.resolution = (1280, 720)

# For Preview
#cam.start_preview()

# For Snapshot
cam.capture('snapshot.jpg')
#cam.capture('snapshot.jpg', resize=(96, 64))

#time.sleep(5)
#cam.stop_preview()

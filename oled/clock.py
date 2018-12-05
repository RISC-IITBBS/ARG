import SSD1331
import datetime
import time
import math

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

if __name__ == '__main__':
    device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
    try:
        device.EnableDisplay(True)
        device.Clear()
        today_last_time = "Unknown"
        while True:
            my_now = datetime.datetime.now()
            today_date = my_now.strftime("%Y-%B-%d %A")
            today_time = my_now.strftime("%H:%M")
            if today_time != today_last_time:
                device.Clear()
                time.sleep(0.01)
                hours_angle = 270 + (30 * (my_now.hour + (my_now.minute / 60.0)))
                hours_dx = int(math.cos(math.radians(hours_angle)) * 12)
                hours_dy = int(math.sin(math.radians(hours_angle)) * 12)
                minutes_angle = 270 + (6 * my_now.minute)
                minutes_dx = int(math.cos(math.radians(minutes_angle)) * 18)
                minutes_dy = int(math.sin(math.radians(minutes_angle)) * 18)
                device.DrawCircle(50, 32, 28, SSD1331.COLOR_RED)
                device.DrawLine(50, 32, 30 + hours_dx, 32 + hours_dy, SSD1331.COLOR_WHITE)
                device.DrawLine(50, 32, 30+ minutes_dx, 32 + minutes_dy, SSD1331.COLOR_WHITE)
                #device.DrawString(60, 28, today_time, SSD1331.COLOR_WHITE)
                today_last_time = today_time
            time.sleep(0.5)
    finally:
        device.EnableDisplay(False)
        device.Remove()

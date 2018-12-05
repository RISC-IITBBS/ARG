import SSD1331
import datetime
import time
import math
import random

arrow = [0x04, 0x02, 0x01, 0x02, 0x04]
alien1 = [0x4C, 0x1A, 0xB6, 0x5F, 0x5F, 0xB6, 0x1A, 0x4C]
alien2 = [0x18, 0xFD, 0xA6, 0x3C, 0x3C, 0xA6, 0xFD, 0x18]
alien3 = [0xFC, 0x98, 0x35, 0x7E, 0x7E, 0x35, 0x98, 0xFC]
ARMY_SIZE_ROWS = 2
ARMY_SIZE_COLS = 6

class Bullet:
    def __init__(self, device, x, y):
        self._device = device
        self.x = x
        self.y = y
        self.Alive = False

    def Render(self, on):
        if self.Alive:
            if on:
                c = SSD1331.COLOR_WHITE
            else:
                c = SSD1331.COLOR_BLACK
            self._device.DrawPixel(self.x, self.y + 0, c)
            self._device.DrawPixel(self.x, self.y + 1, c)
            self._device.DrawPixel(self.x, self.y + 2, c)
        return

    def Reset(self, x, y):
        self.x = x
        self.y = y
        self.Alive = True
        return

    def Update(self, direction):
        if self.Alive:
            self.y = self.y + (direction * 4)
            if self.y < 10:
                self.Alive = False
        return

class Player:
    def __init__(self, device):
        self._device = device
        self.x = 48
        self.y = 54
        self.Bullets = []
        for i in xrange(0, 4, 1):
            self.Bullets.append(Bullet(device, 0, 0))
        return

    def Render(self, on):
        if on:
            c = SSD1331.COLOR_WHITE
        else:
            c = SSD1331.COLOR_BLACK
        for i in xrange(0, len(arrow), 1):
            line = arrow[i]
            for j in xrange(0, 3, 1):
                if line & 0x1:
                    self._device.DrawPixel(self.x - 2 + i, self.y + j, c)
                line >>= 1
        for i in xrange(0, len(self.Bullets), 1):
            self.Bullets[i].Render(on)
        return

    def Update(self, direction):
        t = self.x + (direction * 2)
        if  t > 4 and t < 92:
            self.x = t
        for i in xrange(0, len(self.Bullets), 1):
            self.Bullets[i].Update(-1)
        return

    def Shoot(self):
        for i in xrange(0, len(self.Bullets), 1):
            if self.Bullets[i].Alive == False:
                self.Bullets[i].Reset(self.x, self.y)
                break
        return

class Invader:
    def __init__(self, device, minx, maxx, x, y):
        self._device = device
        self.x = x
        self.y = y
        self._direction = 1
        self.Alive = True
        self.Score = 10
        self._minx = minx
        self._maxx = maxx
        return

    def Render(self, on):
        if self.Alive:
            if on:
                c = SSD1331.COLOR_GREEN
            else:
                c = SSD1331.COLOR_BLACK
            for i in xrange(0, len(alien2), 1):
                line = alien2[i]
                for j in xrange(0, 8, 1):
                    if line & 0x1:
                        self._device.DrawPixel(self.x - 4 + i, self.y - 4 + j, c)
                    line >>= 1
        return

    def Update(self):
        invaded = False
        if self.Alive:
            t = self.x + self._direction
            if  t > self._minx and t < self._maxx:
                self.x = self.x + self._direction
            else:
                self._direction = self._direction * -1
                self.y = self.y + 2
                if self.y > 44:
                    invaded = True
        return invaded

class Army:
    def __init__(self, device):
        self._device = device
        self.Invaded = False
        self.Invaders = []
        for i in xrange(0, ARMY_SIZE_ROWS, 1):
            row = []
            for j in xrange(0, ARMY_SIZE_COLS, 1):
                row.append(Invader(device, 4 + (j * 12) , 30 + (j * 12), 4 + (j * 12), 14 + (i * 12)))
            self.Invaders.append(row)
        return

    def Render(self, on):
        for i in xrange(0, len(self.Invaders), 1):
            for j in xrange(0, len(self.Invaders[i]), 1):
               self.Invaders[i][j].Render(on)
        return

    def Update(self, bullets):
        for i in xrange(0, len(self.Invaders), 1):
            for j in xrange(0, len(self.Invaders[i]), 1):
               if self.Invaders[i][j].Update():
                   self.Invaded = True
        for i in xrange(0, len(self.Invaders), 1):
            for j in xrange(0, len(self.Invaders[i]), 1):
                if self.Invaders[i][j].Alive:
                    for k in xrange(0, len(bullets), 1):
                        if bullets[k].Alive:
                            t = (self.Invaders[i][j].x - bullets[k].x) * (self.Invaders[i][j].x - bullets[k].x) + (self.Invaders[i][j].y - bullets[k].y) * (self.Invaders[i][j].y - bullets[k].y)
                            # if point is in circle
                            if t < 25: # 5 * 5 = r * r
                                self.Invaders[i][j].Alive = False
                                bullets[k].Alive = False
        return

    def Size(self):
        size = 0
        for i in xrange(0, len(self.Invaders), 1):
            for j in xrange(0, len(self.Invaders[i]), 1):
               if self.Invaders[i][j].Alive:
                  size = size + 1
        return size

    def Score(self):
        score = 0
        for i in xrange(0, len(self.Invaders), 1):
            for j in xrange(0, len(self.Invaders[i]), 1):
                if self.Invaders[i][j].Alive == False:
                    score = score + self.Invaders[i][j].Score
        return score

def AiLogicShoot(army, plyr):
    for i in xrange(0, len(army.Invaders), 1):
        for j in xrange(0, len(army.Invaders[i]), 1):
            if army.Invaders[i][j].Alive != False:
                if plyr.x > (army.Invaders[i][j].x - 2) and plyr.x < (army.Invaders[i][j].x + 2):
                    if random.random() < 0.75:
                        plyr.Shoot()
                        return
    return

def AiLogicMove(army, plyr, rows):
    for i in xrange(0, len(rows), 1):
        for j in xrange(0, len(rows[i]), 1):
            if army.Invaders[i][rows[i][j]].Alive != False:
                if plyr.x < army.Invaders[i][rows[i][j]].x:
                    plyr.Update(1)
                    return
                elif plyr.x > army.Invaders[i][rows[i][j]].x:
                    plyr.Update(-1)
                    return
    return

SSD1331_PIN_CS  = 23
SSD1331_PIN_DC  = 24
SSD1331_PIN_RST = 25

if __name__ == '__main__':
    device = SSD1331.SSD1331(SSD1331_PIN_DC, SSD1331_PIN_RST, SSD1331_PIN_CS)
    plyr   = Player(device)
    army   = Army(device)
    rows = []
    rows.append(random.sample(range(6), 6))
    rows.append(random.sample(range(6), 6))
    try:
        raw_splash  = SSD1331.GetRawPixelDataFromBmp24File("snapshot.bmp")
        data_splash = SSD1331.UnpackRawPixelBmp24Data(raw_splash)
        device.EnableDisplay(True)
        device.Clear()
        time.sleep(0.1)
        device.DrawFullScreenBitMap(data_splash) # Splash screen.
        time.sleep(3)
        device.Clear()
        time.sleep(0.1)
        device.DrawLine(0, 61, 95, 61, SSD1331.COLOR_WHITE)
        device.DrawLine(0, 63, 95, 63, SSD1331.COLOR_WHITE)
        time.sleep(0.1)
        while army.Invaded == False and army.Size() > 0:
            plyr.Render(False)
            army.Render(False)
            AiLogicShoot(army, plyr)
            AiLogicMove(army, plyr, rows)
            army.Update(plyr.Bullets)
            army.Render(True)
            plyr.Render(True)
            device.DrawStringBg(8, 0, "Score:" + str(army.Score()), SSD1331.COLOR_BLUE, SSD1331.COLOR_BLACK)
            time.sleep(0.8)
        if army.Size() == 0:
            device.DrawStringBg(27, 28, "Victory", SSD1331.COLOR_BLUE, SSD1331.COLOR_BLACK)
        else:
            device.DrawStringBg(30, 28, "Defeat", SSD1331.COLOR_RED, SSD1331.COLOR_BLACK)
        time.sleep(10)
    finally:
         device.EnableDisplay(False)
         device.Remove()

#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from Tkinter import *

import time
import pigpio
import spidev
import atexit
import threading
from subprocess import Popen, PIPE
import logging


def labelrun(temp):
    root = Tk()
    labbel = Label(root, text=temp)
    labbel.pack()
    root.mainloop()

panel = threading.Thread(name='panel',target=labelrun)
panel.setDaemon(True)

panel.start()


"""
# set the speed to start, from 0 (off) to 255 (max speed)
myMotor.setSpeed(150)
myMotor.run(Adafruit_MotorHAT.FORWARD);
# turn on motor
myMotor.run(Adafruit_MotorHAT.RELEASE);
"""


class MotorRunner(threading.Thread):
    def run(self):
        spi = spidev.SpiDev()
        spi.open(0, 0)

        spi.max_speed_hz = 500000
        spi.mode = 0

        mh = Adafruit_MotorHAT(addr=0x60)
        def turnOffMotors():
            mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)

        atexit.register(turnOffMotors)
        myMotor = mh.getMotor(1)

        pi = pigpio.pi()

        if not pi.connected:
           exit(0)

        sensorMeat = pi.spi_open(0, 1000000, 0) # CE0 on main SPI
        sensorBot = pi.spi_open(1, 1000000, 0) # CE1 on main SPI
        timeStat = time.time()
        target = 100.0
        motorState = False
        while True:
           myMotor.run(Adafruit_MotorHAT.FORWARD)
           c, d = pi.spi_read(sensorMeat, 2)
           e, f = pi.spi_read(sensorBot, 2)
           if c == 2 and e == 2:
              wordMeat = (d[0]<<8) | d[1]
              wordBot = (f[0]<<8) | f[1]
              if (wordMeat & 0x8006) == 0 and (wordBot & 0x8006) == 0: # Bits 15, 2, and 1 should be zero.
                 t = 9*(wordMeat >> 3)/20.0 + 32.0
                 u = 9*(wordBot >> 3)/20.0 + 32.0
                 delta = t - target
                 if(abs(time.time() - timeStat - 10) < 1):
                     timeStat = time.time()
                     if delta < -20:
                         print('Delta is smaller than -20')
                         if motorState == False:
                             motorState = True
                             myMotor.setSpeed(100)
                         else:
                             motorState = False
                             myMotor.setSpeed(0)
                     elif delta < 0:
                         print('Delta is smaller than 0 but not -20')
                         if motorState == False:
                             motorState = True
                             myMotor.setSpeed(60)
                         else:
                             motorState = False
                             myMotor.setSpeed(0)
                 labelrun(text = "{:.2f}".format(t) + ' ' + "{:.2f}".format(u))
                 print("{:.2f}".format(t) + ' ' + "{:.2f}".format(u) + ' ' + "{:.2f}".format(delta) + ' ' + str(motorState))
              else:
                 print("bad reading {:b}".format(word))
           time.sleep(1) # Don't try to read more often than 4 times a second.

x = MotorRunner(name='Motor')
x.start()

pi.spi_close(sensorMeat)
pi.spi_close(sensorBot)

pi.stop()

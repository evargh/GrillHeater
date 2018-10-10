#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from Tkinter import *
import RPi.GPIO as GPIO

import time
import pigpio
import spidev
import atexit
import threading
from subprocess import Popen, PIPE
import logging

root = Tk()
target = IntVar()
target.set(100)
temp = StringVar()
motSpeed = StringVar()
temp.set('Temperature: 0 degrees F')
motSpeed.set('Motor Speed: 0')
labbel = Label(root, textvariable = temp)
labbel.pack()
labbel2 = Label(root, textvariable = motSpeed)
labbel2.pack()

ent = Entry(root)
ent.pack()
submit = Button(root, text="Enter", width = 15, command = lambda: setTemp(ent.get()))
submit.pack()
ent.insert(0,"100")

pi = pigpio.pi()


GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
valveControl = GPIO.PWM(24, 100)
valveControl.start(5)

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 500000
spi.mode = 0
mh = Adafruit_MotorHAT(addr=0x60)
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)
myMotor = mh.getMotor(1)

if not pi.connected:
   exit(0)

def setTemp(nice):
    target.set(int(nice))

sensorMeat = pi.spi_open(0, 1000000, 0) # CE0 on main SPI
sensorBot = pi.spi_open(1, 1000000, 0) # CE1 on main SPI
timeStat = time.time()
motorState = False
while True:
   myMotor.run(Adafruit_MotorHAT.FORWARD)
   c, d = pi.spi_read(sensorBot, 2)
   if c == 2:
      wordMeat = (d[0]<<8) | d[1]
      if (wordMeat & 0x8006) == 0: # Bits 15, 2, and 1 should be zero.
         t = 9*(wordMeat >> 3)/20.0 + 32.0
         delta = t - target.get()
         if(abs(time.time() - timeStat - 10) < 1):
             timeStat = time.time()
             if delta < -20:
                 print('Delta is smaller than -20')
                 if motorState == False:
                     motorState = True
                     motSpeed.set('Motor Speed: 100')
                     myMotor.setSpeed(100)
                     valveControl.ChangeDutyCycle(15)
                 else:
                     motorState = False
                     motSpeed.set('Motor Speed: 0')
                     myMotor.setSpeed(0)
                     valveControl.ChangeDutyCycle(5)
             elif delta < 0:
                 print('Delta is smaller than 0 but not -20')
                 if motorState == False:
                     motorState = True
                     motSpeed.set('Motor Speed: 60')
                     myMotor.setSpeed(60)
                     valveControl.ChangeDutyCycle(15)
                 else:
                     motorState = False
                     motSpeed.set('Motor Speed: 0')
                     myMotor.setSpeed(0)
                     valveControl.ChangeDutyCycle(5)
         temp.set('Temperature: ' + "{:.2f}".format(t) + ' degrees F')
         root.update_idletasks()
         root.update()
         print("{:.2f}".format(t) + ' ' + "{:.2f}".format(delta) + ' ' + str(motorState) + ' ' + "{:.2f}".format(GPIO.input(24)))
      else:
         print("bad reading {:b}".format(word))
   time.sleep(1) # Don't try to read more often than 4 times a second.

pi.spi_close(sensorMeat)
pi.spi_close(sensorBot)
GPIO.cleanup()

pi.stop()

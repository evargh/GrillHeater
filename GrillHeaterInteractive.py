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
motSpeed = IntVar()
motSpeed.set(100)
runt = IntVar()
runt.set(10)
endt = IntVar()
endt.set(10)

temp = StringVar()
temp.set('Temp: 0')
labbelTemp = Label(root, textvariable=temp)
labbelTemp.pack()
delts = StringVar()
delts.set('Delta: 0')
labbelDelt = Label(root, textvariable=delts)
labbelDelt.pack()

tempEnt = Entry(root)
tempEnt.pack()
submit1 = Button(root, text="Target Temperature", width=15, command=lambda: setTemp(tempEnt.get()))
submit1.pack()
tempEnt.insert(0,"100")

speedEnt = Entry(root)
speedEnt.pack()
submit2 = Button(root, text="Motor Speed", width=15, command=lambda: setSpeed(speedEnt.get()))
submit2.pack()
speedEnt.insert(0,"100")

runtEnt = Entry(root)
runtEnt.pack()
submit3 = Button(root, text="Fan Run Time", width=15, command=lambda: setRun(runtEnt.get()))
submit3.pack()
runtEnt.insert(0,"10")

endtEnt = Entry(root)
endtEnt.pack()
submit3 = Button(root, text="Wait Time", width=15, command=lambda: setEnd(endtEnt.get()))
submit3.pack()
endtEnt.insert(0,"10")

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

def setSpeed(nice):
    motSpeed.set(int(nice))

def setRun(nice):
    runt.set(int(nice))

def setEnd(nice):
    endt.set(int(nice))

sensorMeat = pi.spi_open(0, 1000000, 0) # CE0 on main SPI
sensorBot = pi.spi_open(1, 1000000, 0) # CE1 on main SPI
timeStat = time.time()
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
         delta = t - target.get()
         delts.set('Delta: ' + "{:.2f}".format(delta))
         if not motorState and time.time() > timeStat + endt.get():
             timeStat = time.time()
             motorState = True
             myMotor.setSpeed(motSpeed.get())
             valveControl.ChangeDutyCycle(15)
         if motorState and time.time() > timeStat + runt.get():
             timeStat = time.time()
             motorState = False
             myMotor.setSpeed(0)
             valveControl.ChangeDutyCycle(5)
         temp.set('Meat Temperature: ' + "{:.2f}".format(t) + '    Smoker Temperature ' + "{:.2f}".format(u))
         root.update_idletasks()
         root.update()
         print("{:.2f}".format(motSpeed.get()) + ' ' + "{:.2f}".format(target.get()) +
               ' ' + "{:.2f}".format(runt.get()) + ' ' + "{:.2f}".format(endt.get()))
      else:
         print("bad reading {:b}".format(wordMeat) + ' ' + "bad reading {:b}".format(wordBot))
   time.sleep(1) # Don't try to read more often than 4 times a second.

pi.spi_close(sensorMeat)
pi.spi_close(sensorBot)
GPIO.cleanup()

pi.stop()

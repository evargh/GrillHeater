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

# Initialize the grid
root = Tk()
root.geometry('500x500')

rows=0
while rows < 50:
    root.rowconfigure(rows, weight=1)
    root.columnconfigure(rows, weight=1)
    rows += 1

# Initialize all Integer variables
target = IntVar()
target.set(230)
motSpeed = IntVar()
motSpeed.set(120)
runt = IntVar()
runt.set(10)
endt = IntVar()
endt.set(60)

# Initialize temperature display
temp = StringVar()
temp.set('Temp: 0')
labbelTemp = Label(root, textvariable = temp, font = ("Helvetica", 14))
labbelTemp.grid(row = 10,column = 5)

# Initialize delta (difference between target temperature and smoker temperature) display
delts = StringVar()
delts.set('Delta Temp: 0')
labbelDelt = Label(root, textvariable = delts, font = ("Helvetica", 14))
labbelDelt.grid(row = 15, column = 5)

# Initialize field for entering target temperature
tempEnt = Entry(root)
tempEnt.grid(row = 10, column = 30)
submit1 = Button(root, text = "Smoker Set Temp", width=15, command = lambda: setTemp(tempEnt.get()))
submit1.grid(row=15 ,column = 30)
tempEnt.insert(0,"230")

# Initialize title field
labbelTitle = Label(root, text = "Smoke&Temp Master", font = ("Helvetica", 20))
labbelTitle.grid(row = 40, column = 5)

# Set up pigpio to start up all the GPIO pins and set up thermocouples
pi = pigpio.pi()
sensorMeat = pi.spi_open(0, 1000000, 0) # CE0 on main SPI
sensorBot = pi.spi_open(1, 1000000, 0) # CE1 on main SPI

# Set BCM pin 24 as a PWM output, and set its initial duty cycle to 5
# This is for the servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
valveControl = GPIO.PWM(24, 100)
valveControl.start(5)

# This is for the fan
spi = spidev.SpiDev()
spi.open(0,0)

spi.max_speed_hz = 500000
spi.mode = 0
mh = Adafruit_MotorHAT(addr = 0x60)
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

# Set current system time
timeStat = time.time()
motorState = False

while True:
    # Read sensor values
    c, d = pi.spi_read(sensorMeat, 2)
    e, f = pi.spi_read(sensorBot, 2)

    # Confirm that all values are being read. If so, shift bits 8 to the left and compare
    if c == 2 and e == 2:
        wordMeat = (d[0] << 8) | d[1]
        wordBot = (f[0] << 8) | f[1]

        # Bits 15, 2, and 1 should be zero
        if (wordMeat & 0x8006) == 0 and (wordBot & 0x8006) == 0:
            # Converts reading to fahrenheit
            t = 9 * (wordMeat >> 3) / 20.0 + 32.0
            u = 9 * (wordBot >> 3) / 20.0 + 32.0
            delta = target.get() - u
            timesetter(delta)
            delts.set('Delta Temp: ' + "{:.2f}".format(delta))

            if not motorState and time.time() > timeStat + endt.get():
                timeStat = time.time()
                motorState = True
                myMotor.setSpeed(motSpeed.get())
                # Duty cycle 15 is open
                valveControl.ChangeDutyCycle(15)

            if motorState and time.time() > timeStat + runt.get():
                timeStat = time.time()
                motorState = False
                myMotor.setSpeed(0)
                # Duty cycle 5 is closed
                valveControl.ChangeDutyCycle(5)

            temp.set('Meat Temperature: ' + "{:.2f}".format(t) + '\nSmoker Temperature: ' + "{:.2f}".format(u))
            root.update_idletasks()
            root.update()
            print("{:.2f}".format(motSpeed.get()) + ' ' + "{:.2f}".format(target.get()) +
               ' ' + "{:.2f}".format(runt.get()) + ' ' + "{:.2f}".format(endt.get()))
        else:
            print("bad reading {:b}".format(wordMeat) + ' ' + "bad reading {:b}".format(wordBot))

    time.sleep(1)

# Lookup table for delta values
def timesetter(dlt):
    if dlt > 50:
        setRun(30)
        setEnd(30)
    elif dlt > 25:
        setRun(25)
        setEnd(60)
    elif dlt > 6:
        setRun(15)
        setEnd(60)
    elif dlt > 3:
        setRun(10)
        setEnd(60)
    elif dlt < -5:
        setRun(3)
        setEnd(120)
    else:
        setRun(3)
        setEnd(60)

pi.spi_close(sensorMeat)
pi.spi_close(sensorBot)
GPIO.cleanup()

pi.stop()

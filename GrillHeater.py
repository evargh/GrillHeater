#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import pigpio
import spidev
import atexit

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 500000
spi.mode = 0

mh = Adafruit_MotorHAT(addr=0x60)
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)
myMotor = mh.getMotor(1)

"""
# set the speed to start, from 0 (off) to 255 (max speed)
myMotor.setSpeed(150)
myMotor.run(Adafruit_MotorHAT.FORWARD);
# turn on motor
myMotor.run(Adafruit_MotorHAT.RELEASE);
"""

pi = pigpio.pi()

if not pi.connected:
   exit(0)

sensor = pi.spi_open(0, 1000000, 0) # CE0 on auxiliary SPI

stop = time.time() + 600

while time.time() < stop:
   myMotor.run(Adafruit_MotorHAT.FORWARD)
   c, d = pi.spi_read(sensor, 2)
   if c == 2:
      word = (d[0]<<8) | d[1]
      if (word & 0x8006) == 0: # Bits 15, 2, and 1 should be zero.
         t = 9.0*(word >> 3)/20.0 + 32.0
         yeet = "{:.2f}".format(t)
         speed = int(t) * 2
         myMotor.setSpeed(speed)
         print(yeet + ' '+ str(speed))
      else:
         print("bad reading {:b}".format(word))
   time.sleep(0.25) # Don't try to read more often than 4 times a second.

pi.spi_close(sensor)

pi.stop()


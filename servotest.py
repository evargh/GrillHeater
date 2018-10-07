#!/usr/bin/env python

import RPi.GPIO as GPIO

import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
pwm = GPIO.PWM(24, 100)
pwm.start(2.5) # Initialization
try:
    while True:
        pwm.ChangeDutyCycle(5)
        time.sleep(1)
        pwm.ChangeDutyCycle(7.5)
        time.sleep(1)
        pwm.ChangeDutyCycle(10)
        time.sleep(1)
        pwm.ChangeDutyCycle(12.5)
        time.sleep(1)
        pwm.ChangeDutyCycle(10)
        time.sleep(1)
        pwm.ChangeDutyCycle(7.5)
        time.sleep(1)
        pwm.ChangeDutyCycle(5)
        time.sleep(1)
        pwm.ChangeDutyCycle(2.5)
        time.sleep(1)
except KeyboardInterrupt:
  pwm.stop()
  GPIO.cleanup()

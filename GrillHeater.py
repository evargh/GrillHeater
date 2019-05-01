#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

import threading
import time
import pigpio
import spidev
import atexit
import threading
from subprocess import Popen, PIPE
import logging


# target = IntVar()
# target.set(100)
# temp = StringVar()
# temp.set('0')
# labbel = Label(root, textvariable=temp)
# labbel.pack()
# ent = Entry(root)

# ent.pack()
# submit = Button(root, text="Enter", width=15, command=lambda: setTemp(ent.get()))
# submit.pack()
# ent.insert(0,"100")
# time.sleep(10)

app = Flask(__name__)

pi = pigpio.pi()

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
motorState = False

meatTemps = {
    0: 150
}
smokeTemps = {
    0: 150
}

# TODO:  make two arrays, one for meat temperature and the other for the smoker
# temperature with a limit of 30 indices and store it to JSON. The index page
# will then be able to read both of them in

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Send these arguments to motorRunner
        runnerMan = Treading.Thread(target=motorRunner, arg=())
        return render_template('index.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

# TODO: Improve multithreading here. Be completely certain that this part of it actually works

def motorRunner(target = 200, timeState = time.time()):
    int index = 3
    myMotor.run(Adafruit_MotorHAT.FORWARD)
    c, d = pi.spi_read(sensorMeat, 2)
    e, f = pi.spi_read(sensorBot, 2)
    if c == 2 and e == 2:
        wordMeat = (d[0]<<8) | d[1]
        wordBot = (f[0]<<8) | f[1]
        if (wordMeat & 0x8006) == 0 and (wordBot & 0x8006) == 0:
            t = 9*(wordMeat >> 3)/20.0 + 32.0
            nu = 9*(wordBot >> 3)/20.0 + 32.0
            meatTemps.update([index, t])
            smokeTemps.update([index, nu])
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
             temp.set("{:.2f}".format(t))
             root.update_idletasks()
             root.update()
             print("{:.2f}".format(t) + ' ' + "{:.2f}".format(u) + ' ' + "{:.2f}".format(delta) + ' ' + str(motorState))
         else:
             print("bad reading {:b}".format(word))
     time.sleep(1)
     index += 3
     json.dump(meatTemps, "meatTemp.txt")
     json.dump(smokeTemps, "smokeTemp.txt")
   # Don't read more often than 4 times a second

open('meatTemp.txt', 'w').close()
open('smokeTemp.txt', 'w').close()
pi.spi_close(sensorMeat)
pi.spi_close(sensorBot)

pi.stop()

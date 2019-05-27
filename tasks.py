from celery import Celery
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import pigpio
import spidev
import atexit
import os
import json

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

sensorMeat = pi.spi_open(0, 1000000, 0)  # CE0 on main SPI
sensorBot = pi.spi_open(1, 1000000, 0)  # CE1 on main SPI
motorState = False

meatTemps = {
    0: 0
}
smokeTemps = {
    0: 0
}


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def MotorRunner(target=200, timeStat=time.time()):
    while True:
        timeStat = time.time()
        # Runs the motor
        index = 3
        myMotor.run(Adafruit_MotorHAT.FORWARD)
        # Reading thermocouple values
        c, d = pi.spi_read(sensorMeat, 2)
        e, f = pi.spi_read(sensorBot, 2)
        # Verifying the validity of all reads
        if c == 2 and e == 2:
            wordMeat = (d[0] << 8) | d[1]
            wordBot = (f[0] << 8) | f[1]
            if (wordMeat & 0x8006) == 0 and (wordBot & 0x8006) == 0:
                # Converting all information to fahrenheit
                t = 9*(wordMeat >> 3)/20.0 + 32.0
                nu = 9*(wordBot >> 3)/20.0 + 32.0
                # Adding values to the dictionaries
                # Establishing the change in temperature that needs to be corrected
                delta = t - target
                # Checking every ten seconds or so, accounting for long-term change
                if(abs(time.time() - timeStat - 10) < 1):
                    timeStat = time.time()
                    # Initializes the program to one of two stages: accelerated
                    # change, or slower change. This system runs off of a negative
                    # feedback loop. The fans either pulse at a high speed, or a
                    # low speed
                    if delta < -20:
                        print('Delta is smaller than -20')
                        if motorState is False:
                            motorState = True
                            myMotor.setSpeed(100)
                        else:
                            motorState = False
                            myMotor.setSpeed(0)
                    elif delta < 0:
                        print('Delta is smaller than 0 but not -20')
                        if motorState is False:
                            motorState = True
                            myMotor.setSpeed(60)
                        else:
                            motorState = False
                            myMotor.setSpeed(0)
            else:
                print("bad reading {:b}".format(word))
        time.sleep(1)
        index += 3
        # Dumps the values to a text file, which can later be interpreted by
        # JS on the index page
        # Don't read more than 4 times a second

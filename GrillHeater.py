#!/usr/bin/env python

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

from flask import Flask, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
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

sensorMeat = pi.spi_open(0, 1000000, 0) # CE0 on main SPI
sensorBot = pi.spi_open(1, 1000000, 0) # CE1 on main SPI

stop = time.time() + 600

@app.route('/index.html', methods=['GET', 'POST'])
def index():
    # return the html page i already made
    # form = FileForm()
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'], name="img01.jpg")
        # filename = photos.save(request.files['photo'], name="img01.jpg")
        # for right now, the default image title in test images is img01.jpg,
        # so change the filename that we got from user to reflect that when
        # moving into the directory
        os.system('python3 -m scripts.label_image \
                  --graph=tf_files/retrained_graph.pb  \
                  --image=img/img01.jpg')
        os.system('javac recipefinder.java')
        os.system('java recipefinder')

        recipebois = open('result.txt', 'r')

        linebois = []
        for l in recipebois:
            linebois.append(l.strip())

        result = linebois[0].split(' ')[0]
        os.remove("img/img01.jpg")

        response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/findByIngredients?ingredients=" + result + "&number=3&ranking=1", headers={  # noqa
            "X-Mashape-Key": "EaDmA6l14dmshEnLCpRh37Zhx1q6p1cW7lmjsnOWuSXg2dfb1c", # noqa
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com" # noqa
          }
        )

        one = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/" + str(response.json()[0]['id']) + "/information", headers={ # noqa
            "X-Mashape-Key": "EaDmA6l14dmshEnLCpRh37Zhx1q6p1cW7lmjsnOWuSXg2dfb1c", # noqa
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com" # noqa
          }
        )
        two = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/" + str(response.json()[1]['id']) + "/information", headers={ # noqa
            "X-Mashape-Key": "EaDmA6l14dmshEnLCpRh37Zhx1q6p1cW7lmjsnOWuSXg2dfb1c", # noqa
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com" # noqa
          }
        )
        three = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/" + str(response.json()[2]['id']) + "/information", headers={ # noqa
            "X-Mashape-Key": "EaDmA6l14dmshEnLCpRh37Zhx1q6p1cW7lmjsnOWuSXg2dfb1c", # noqa
            "X-Mashape-Host": "spoonacular-recipe-food-nutrition-v1.p.mashape.com" # noqa
          }
        )

        url1 = one.json()['spoonacularSourceUrl']  # ['sourceUrl'] if you want
        url2 = two.json()['spoonacularSourceUrl']  # to go directly to the
        url3 = three.json()['spoonacularSourceUrl']  # recipe

        title1 = response.json()[0]['title']
        title2 = response.json()[1]['title']
        title3 = response.json()[2]['title']

        return render_template('itemlist.html', title1=title1, title2=title2,
                               title3=title3, url1=url1, url2=url2, url3=url3)
    return render_template('index.html')

def runFan():
    while time.time() < stop:
       myMotor.run(Adafruit_MotorHAT.FORWARD)
       c, d = pi.spi_read(sensor, 2)
       e, f = pi.spi_read(sensorBot, 2)
       if c == 2 and e == 2:
          word = (d[0]<<8) | d[1]
          if (word & 0x8006) == 0:if (wordMeat & 0x8006) == 0 and (wordBot & 0x8006) == 0: # Bits 15, 2, and 1 should be zero.
             t = 9*(wordMeat >> 3)/20.0 + 32.0
             u = 9*(wordBot >> 3)/20.0 + 32.0
             yeet = "{:.2f}".format(t)
             speed = int(t) * 3 - 20
             myMotor.setSpeed(speed)
             print(yeet + ' ' + + "{:.2f}".format(u) + ' '+ str(speed))
          else:
             print("bad reading {:b}".format(word))
       time.sleep(0.25) # Don't try to read more often than 4 times a second.

pi.spi_close(sensor)

pi.stop()

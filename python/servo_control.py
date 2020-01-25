# -*- coding: utf-8 -*-
#
# K9 Forward Sensors Controller
#
# authored by Richard Hopkins December 2017 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program turns K9's radar crisps into rotating LIDAR
# sensors that can detect what is in front of the robot dog.
#
# This data is supplemented by a stationary mouth sensor that permanently
# detects what is front of the dog at ground level (thanks to the wonderful
# Paul Booth for that particular idea!)
#
# The information from all the sensors is stored in a Redis database
# in the Pi, so that the Python Motorcontroller can transmit the current state
# to the browser via Node-RED
#
import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

sys.path.append('/home/pi/Adafruit_Python_PCA9685/Adafruit_PCA9685') # persistent directory for Adafruit driver
print "Importing servo driver library..."
import Adafruit_PCA9685 # enable control of devices ear servos via Adafruit library
print "Importing ADC driver library..."
import Adafruit_ADS1x15
# Create ADC object
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
# Create and intialise servo driver
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)
pwm.set_pwm(4, 0, 315)
pwm.set_pwm(5, 0, 315)

leftmin=65000
rightmin=65000
leftmax=0
rightmax=0
hz = 260

while (hz<370.0):
    pwm.set_pwm(4, 0, int(hz))
    pwm.set_pwm(5, 0, int(hz))
    
    left_direction = adc.read_adc(0,gain=GAIN)
    right_direction = adc.read_adc(1,gain=GAIN)

    if (left_direction<leftmin) :
        leftmin=left_direction
        print("Left min:"+str(leftmin))
    if (right_direction<rightmin) :
        rightmin=right_direction
        print("Right min:"+str(rightmin))
    if (left_direction>leftmax) :
        leftmax=left_direction
        print("Left max:"+str(leftmax))
    if (right_direction>rightmax) :
        rightmax=right_direction
        print("Right max:"+str(rightmax))
    hz = hz + 0.1
    print str(hz)
    # print("Left:"+str(left_direction)+"v Right: "+str(right_direction)+"v")

pwm.set_pwm(4, 0, 315)
pwm.set_pwm(5, 0, 315)


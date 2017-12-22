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
pwm.set_pwm(0, 4, 0)
pwm.set_pwm(0, 5, 0)

while True:
    left_direction = adc.read_adc(1,gain=GAIN)
    right_direction = adc.read_adc(2,gain=GAIN)
    print("Left:"+str(left_direction)+"v Right: "+str(right_direction)+"v")

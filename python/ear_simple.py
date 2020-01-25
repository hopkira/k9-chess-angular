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

# Create and intialise servo driver
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

min_pwm = 140
mid_pwm = 370
max_pwm = 600
left_pwm_channel = 4
right_pwm_channel = 5

pwm.set_pwm(left_pwm_channel,0,mid_pwm)
pwm.set_pwm(right_pwm_channel,0,mid_pwm)

time.sleep(10)

pwm.set_pwm(left_pwm_channel,0,max_pwm)
pwm.set_pwm(right_pwm_channel,0,min_pwm)

time.sleep(10)

pwm.set_pwm(left_pwm_channel,0,mid_pwm)
pwm.set_pwm(right_pwm_channel,0,mid_pwm)


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
pwm.set_pwm_freq(60)

min_pwm = 200
mid_pwm = 400
max_pwm = 600
min_pot = 0.78
mid_pot = 1.65
max_pot = 3.13
left_pwm_channel = 4
right_pwm_channel = 5

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

for forward_speed in my_range (-1,1,0.0001):
    if (forward_speed > 0) :
        percent = min(1,forward_speed)
    else:
        percent = 0
    left_pot_edge = mid_pot + (percent*(max_pot - mid_pot))
    right_pot_edge = mid_pot - (percent*(mid_pot-min_pot))
    left_pwm_edge = mid_pwm + (percent*(max_pwm - mid_pwm))
    right_pwm_edge = mid_pwm - (percent*(mid_pwm-min_pwm))
    left_direction = adc.read_adc(1,gain=GAIN)
    right_direction = adc.read_adc(2,gain=GAIN)
    print("Speed: "+str(forward_speed)+"m/s left: "+str(left_direction)+"v right: "+str(right_direction)+"v")
    if ((left_direction < mid_pot) & (right_direction > mid_pot)) :
        pwm.set_pwm(0, left_pwm_channel, max_pwm)
        pwm.set_pwm(0, right_pwm_channel, min_pwm)
        print("Flip to extremes")
    if ((left_direction > max_pot) & (right_direction < min_pot)) :
        pwm.set_pwm(0, left_pwm_channel, mid_pwm)
        pwm.set_pwm(0, right_pwm_channel, mid.pwm)
        print("Flip towards mid")

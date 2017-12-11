# -*- coding: utf-8 -*-
#
# K9 Ear Sensor Driver
#
# authored by Richard Hopkins December 2017 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program turns K9's radar crisps into rotating LIDAR
# sensors that can detect what is in front of the robot dog
# The information in the sensors is stored in a Redis database
# in the Pi, so that the controller can transmit the current state
# to the browser
#
import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

# sim is a program wide flag to allow the program to run off the Raspberry Pi
# this can be enabled by appending the word "test" to the command line
if ( len(sys.argv) > 1 ) :
   if ( sys.argv[1] == "test" ) :
      sim = True
      print "Executing ears in simulation mode" # let the user know they are in sim mode

print "Importing Redis library..."
import redis
# Connect to a local Redis server
r = redis.Redis(host='127.0.0.1',port=6379)

# If running for real initialise servo driver, LIDARs and ADC
if not sim :
    sys.path.append('/home/pi') # persistent import directory for K9 secrets
    sys.path.append('/home/pi/Adafruit_Python_PCA9685/Adafruit_PCA9685') # persistent directory for Adafruit driver
    print "Importing servo driver library..."
    import Adafruit_PCA9685 # enable control of devices ear servos via Adafruit library
    print "Importing LIDAR driver library..."
    import VL53L0X # enable control of LIDAR sesnsors
    print "Importing ADC driver library..."
    from ADCPi import ADCPi # import the ADC Plus Pi library
    # Create ADC object
    adc = ADCPi(0x68, 0x69, 12)
    # Create and intialise servo driver
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)

class SensorArray :
    def __init__(self) :
        """Resets the redis database state to zero ready for new readings
        """
        print "Resetting Redis state..."
        init_time = time.time()
        for ear in ['left','right']:
            for sensor in range (0, 14):
                r.set(str(ear)+"_"+str(sensor)+"_reading",str(0))
                r.set(str(ear)+"_"+str(sensor)+"_time",str(init_time))

class K9Ears :
    def __init__(self) :
        """Creates two LIDAR instances, one for each ear and a sensor array.
        """
        print "K9 object initialising..."
        # Create LIDAR sensor instances with different channels
        self.left_ear = LIDAR(name="left",adc=1)
        self.right_ear = LIDAR(name="right",adc=2)
        # Create a sensor array instance
        self.sensor_array = SensorArray()
        # Initialise the various measures that will control the ears
        # the pwm settings control the target directions of the ears
        self.min_pwm = 200
        self.mid_pwm = 400
        self.max_pwm = 600
        self.min_pot = 0.78
        self.mid_pot = 1.65
        self.max_pot = 3.13
        self.left_pwm_channel = 4
        self.right_pwm_channel = 5

    def getForwardSpeed() :
        # retrieve current actual robot speed from Redis
        self.left_speed=float(r.get("left"))
        self.right_speed=float(r.get("right"))
        # forward speed will be the average of the two
        # then convert into a percentage of maximum speed (100)
        return ((self.left_speed + self.right_speed)/200)

    def makeReading() :
        """Controls the movement of the ears based on robot speed
        """
        self.forward_speed = getForwardSpeed()
        # if the robot is moving forward, then work out what
        # the boundaries should be for the potentiometer and pwm
        # these boundaries should narrow the movement as the robot gets
        # faster
        if (self.forward_speed > 0) :
            self.percent = min(1,self.forward_speed)
        else:
            self.percent = 0
        self.left_pot_edge = self.mid_pot + (self.percent*(self.max_pot - self.mid_pot))
        self.right_pot_edge = self.mid_pot - (self.percent*(self.mid_pot-self.min_pot))
        self.left_pwm_edge = self.mid_pwm + (self.percent*(self.max_pwm - self.mid_pwm))
        self.right_pwm_edge = self.mid_pwm - (self.percent*(self.mid_pwm-self.min_pwm))
        # Make a reading with the left ear to determine distance and direction
        self.left_ear.makeReading()
        bucket = self.max_pot self.mid_pot (0 to 14) # NOT WORKING!!!
        self.left_ear.recordReading()
        # Make a reading with the right ear to determine distance and direction
        self.right_ear.makeReading()
        bucket = low to mid (0 to 14) # NOT WORKING!!!!
        self.right_ear.recordReading()
        # If both ears are outside the boundaries over which they are meant to move
        # then reverse their direction of travel
        if ((self.left_ear.direction < self.mid_pot) & (self.right_ear.direction > self.mid_pot)) {
            if not sim :
                pwm.set_pwm(0, left_pwm_channel, self.max_pwm)
                pwm.set_pwm(0, right_pwm_channel, self.min_pwm)
        }
        if ((self.left_ear.direction > self.max_pot) & (self.right_ear.direction < self.min_pot)) {
            if not sim :
                pwm.set_pwm(0, left_pwm_channel, self.mid_pwm)
                pwm.set_pwm(0, right_pwm_channel, self.mid.pwm)
        }

class LIDAR :
    def __init__(self, name, adc, direction) :
        """Initialise the VL530L0X that will be used by this LIDAR instance

        Arguments:
        name -- the name of the sensor e.g. left or right
        adc -- this value will determine which I2C bus and ADC channel is used
        when the sensor is queried
        """
        self.adc = adc
        self.name = name
        # initialise sensor via relevant I2C bus using TCA9548A multiplexer
        if not sim :
            self.sensor = VL53L0X.VL53L0X(TCA9548A_Num=self.adc,TCA9548A_Addr=0x70)
            # start sensor ranging
            self.sensor.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)
        print str(self.name) + " LIDAR instantiated."

    def recordReading() :
        r.set(self.name+"_"+str(bucket)+"_reading",str(self.distance))
        r.set(self.name+"_"+str(bucket)+"_time",str(time.time()))

    def makeReading() :
        """Make a distance reading and update the sensors internal state

        Gets the latest distance reading from the LIDAR sensor
        and the direction from the associated ADC channel

        Arguments: none
        """
        self.time=time
        # get distance from LIDAR sensor
        if not sim :
            self.distance = self.sensor.get_distance()
            self.direction = adc.read_voltage(self.adc)
        else :
            self.distance = random.uniform(0,1200)
            self.direction = random.uniform(0,5)
        print str(self.name) + " reads: " + self.distance + " at an angle of" + self.direction

try :
    k9ears = K9Ears()
    while True
        k9ears.makeReading()
except KeyboardInterrupt :
    k9ears.left_ear.sensor.stop_ranging()
    k9ears.right_ear.sensor.stop_ranging()

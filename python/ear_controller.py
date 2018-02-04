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
import memory  # imports K9's memory capability

sim = False

# sim is a program wide flag to allow the program to run off the Raspberry Pi
# this can be enabled by appending the word "test" to the command line
if ( len(sys.argv) > 1 ) :
   if ( sys.argv[1] == "test" ) :
      sim = True
      print "Executing ears in simulation mode" # let the user know they are in sim mode

# GPIO for left LIDAR shutdown pin
mouth_LIDAR_shutdown = 16
# GPIO for right LIDAR shutdown pin
right_LIDAR_shutdown = 20
left_LIDAR_shutdown = 21

focus = 0.5

# If running for real initialise servo driver, LIDARs and ADC
if not sim :
    sys.path.append('/home/pi') # persistent import directory for K9 secrets
    sys.path.append('/home/pi/Adafruit_Python_PCA9685/Adafruit_PCA9685') # persistent directory for Adafruit driver
    print "Importing RPi GPIO and shutting down LIDAR..."
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    # Setup GPIO for shutdown pins on each VL53L0X
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(left_LIDAR_shutdown, GPIO.OUT)
    GPIO.setup(right_LIDAR_shutdown, GPIO.OUT)
    GPIO.setup(mouth_LIDAR_shutdown, GPIO.OUT)
    # Set all shutdown pins low to turn off each VL53L0X
    GPIO.output(left_LIDAR_shutdown, GPIO.LOW)
    GPIO.output(right_LIDAR_shutdown, GPIO.LOW)
    GPIO.output(mouth_LIDAR_shutdown, GPIO.LOW)
    # Keep all low for 500 ms or so to make sure they reset
    time.sleep(0.50)
    print "Importing servo driver library..."
    import Adafruit_PCA9685 # enable control of devices ear servos via Adafruit library
    print "Importing LIDAR driver library..."
    import VL53L0X # enable control of LIDAR sesnsors
    print "Importing ADC driver library..."
    import Adafruit_ADS1x15
    # Create ADC object
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 1
    # Create and intialise servo driver
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)
    pwm.set_pwm(4,0,125)
    pwm.set_pwm(5,0,615)


class K9ForwardSensors :
    def __init__(self) :
        """Creates two LIDAR instances, one for each ear and a sensor array.
        """
        print "K9 object initialising..."
        # Create LIDAR sensor instances with different channels
        self.left_ear = LIDAR(name="ear_left",adc=0,gpio=left_LIDAR_shutdown,address=0x30)
        self.right_ear = LIDAR(name="ear_right",adc=1,gpio=right_LIDAR_shutdown,address=0x31)
        #self.mouth = LIDAR(name="mouth",adc=99,gpio=mouth_LIDAR_shutdown,address=0x32)
        # Initialise the various measures that will control the ears
        # the pwm settings control the target directions of the ears
        self.min_pwm = 140
        self.mid_pwm = 370
        self.max_pwm = 600
        self.max_l_pot = 16776
        self.mid_r_pot = 10932
        self.mid_l_pot = 12963
        self.min_r_pot = 4906
        self.left_pwm_channel = 4
        self.right_pwm_channel = 5

    def getForwardSpeed(self) :
        # retrieve current actual robot speed from Redis
        self.left_speed=float(memory.retrieveState("left:speed"))
        self.right_speed=float(memory.retrieveState("right:speed"))
        # forward speed will be the average of the two
        # then convert into a percentage of maximum speed (100)
        return ((self.left_speed + self.right_speed)/200)

    def makeReading(self) :
        """Controls the movement of the ears based on robot speed
        """
        # make reading from mouth sensor
        #self.mouth.makeReading()
        #self.mouth.recordReading()
        #make reading from ear sensors
        self.forward_speed = self.getForwardSpeed()
        # if the robot is moving forward, then work out what
        # the boundaries should be for the potentiometer and pwm
        # these boundaries should narrow the movement as the robot gets
        # faster
        if (self.forward_speed > 0) :
            self.percent = min(1,self.forward_speed)
        else:
            self.percent = 0
        self.left_pot_tgt = self.mid_l_pot + (focus*self.percent*(self.max_l_pot - self.mid_l_pot))
        self.right_pot_tgt = self.mid_r_pot - (focus*self.percent*(self.mid_r_pot-self.min_r_pot))
        self.left_pwm_tgt = self.mid_pwm + (focus*self.percent*(self.max_pwm - self.mid_pwm))
        self.right_pwm_tgt = self.mid_pwm - (focus*self.percent*(self.mid_pwm - self.min_pwm))
        #print ("LT:"+str(self.left_pot_tgt)+" RT:"+str(self.right_pot_tgt)+" pLT:"+str(self.left_pwm_tgt)+" pRT:"+str(self.right_pwm_tgt))
        # Make a reading with the left ear to determine distance and direction
        self.left_ear.makeReading()
        self.left_ear.recordReading()
        # Make a reading with the right ear to determine distance and direction
        self.right_ear.makeReading()
        self.right_ear.recordReading()
        #print ("LA:"+str(self.left_ear.direction)+" RA:"+str(self.right_ear.direction))
        # If both ears are outside the boundaries over which they are meant to move
        # then reverse their direction of travel
        if ((self.left_ear.direction < self.left_pot_tgt) or (self.right_ear.direction > self.right_pot_tgt)) :
            if not sim :
                pwm.set_pwm(self.left_pwm_channel,0, self.max_pwm)
                pwm.set_pwm(self.right_pwm_channel,0, self.min_pwm)
                #print("Flip L in towards: " + str(self.max_pwm) + ", R in towards: " + str(self.min_pwm))
        if ((self.left_ear.direction > self.max_l_pot) or (self.right_ear.direction < self.min_r_pot)) :
            if not sim :
                pwm.set_pwm(self.left_pwm_channel,0, int(self.left_pwm_tgt))
                pwm.set_pwm(self.right_pwm_channel,0, int(self.right_pwm_tgt))
                #print("Flip L out towards: " + str(self.left_pwm_tgt) + ", R out towards: " + str(self.right_pwm_tgt))


class LIDAR :
    def __init__(self, name, adc, gpio, address) :
        """Initialise the VL530L0X that will be used by this LIDAR instance

        Arguments:
        name -- the name of the sensor e.g. left or right
        adc -- this value will determine which ADC channel is used
        gpio -- the GPIO pin that controls the LIDAR shutdown
        address -- the i2c address of the LIDAR itself
        when the sensor is queried (also translates to I2C address)
        """
        self.adc = adc
        self.name = name
        self.gpio = gpio
        self.address = address
        # initialise sensor via I2C and GPIO shutdown pin
        if not sim :
            self.sensor = VL53L0X.VL53L0X(address=self.address)
            GPIO.output(self.gpio, GPIO.HIGH)
            time.sleep(0.50)
            # start sensor ranging
            self.sensor.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)
        print str(self.name) + " LIDAR instantiated at " + str(self.address) + " measured by ADC " + str(self.adc) + " and controlled by GPIO " + str(self.gpio)

    def recordReading(self) :
        memory.storeSensorReading(self.name,self.distance,self.direction)
        print("dist_"+str(self.name)+": "+str(self.distance)+"mm at bearing: "+str(self.direction))

    def makeReading(self) :
        """Make a distance reading and update the sensors internal state

        Gets the latest distance reading from the LIDAR sensor
        and the direction from the associated ADC channel

        Arguments: none
        """
        self.time=time
        # get distance from LIDAR sensor
        if not sim :
            self.distance = self.sensor.get_distance()
            #self.distance = random.uniform(0,1200) # TEMPORARY FOR TESTING
            if (self.adc == 99) :
                self.direction = 99
            else :
                self.direction = adc.read_adc(self.adc,gain=GAIN)
        else :
            self.distance = random.uniform(0,1200)
            self.direction = random.uniform(0,5)
        # print str(self.name) + " reads: " + str(self.distance) + " at an angle of " + str(self.direction)

try :
    k9sensors = K9ForwardSensors()
    max_time = 0
    while True :
        k9sensors.makeReading()

except KeyboardInterrupt :
    if not sim :
        k9sensors.left_ear.sensor.stop_ranging()
        k9sensors.right_ear.sensor.stop_ranging()
        #k9sensors.mouth.sensor.stop_ranging()
        GPIO.output(left_LIDAR_shutdown, GPIO.LOW)
        GPIO.output(right_LIDAR_shutdown, GPIO.LOW)
        GPIO.output(mouth_LIDAR_shutdown, GPIO.LOW)

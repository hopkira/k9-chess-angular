# -*- coding: utf-8 -*-
#
# K9's Movement Subsystem - Autonomous Motor Driver
#
# authored by Richard Hopkins February 2018 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program provides K9 with a stack of instructions for his movement

import time
import math

print "Importing Redis library..."
import redis
# Connect to a local Redis server
print "Connecting to local redis host"
r = redis.Redis(host='127.0.0.1',port=6379)

sim=False

if __name__ == '__main__' :
    import sys     # allows for command line to be interpreted
    if ( len(sys.argv) > 1 ) :
        if ( sys.argv[1] == "test" ) :
            sim = True
            print "Simulating without RoboClaw" # let the user know they are in sim mode

CLICK2METRES = 0.00611 # converts clicks to metres
WALKINGSPEED = 1.4 # top speed of robot in metres per second
TOPSPEED = int(WALKINGSPEED/CLICK2METRES) # calculate and store max velocity
ACCELERATION = int(2*TOPSPEED) # accelerate to top speed in 0.5s
TURNING_CIRCLE = int(1.1938/CLICK2METRES) # clicks in a full spin
HALF_WHEEL_GAP = 0.095 # half the distance between the wheels

if not sim:
    from roboclaw import Roboclaw
    rc = Roboclaw("/dev/roboclaw",115200)
    rc.Open()
    address = 0x80

if sim:
    import turtle
    turtle.radians()

def calc_click_vel(clicks):
    '''Calculates velocity for motors given a signed click distance
    '''
    modifier = 1
    if (clicks<0):
        modifier = -1
    click_vel = math.sqrt(abs(float(2*clicks*ACCELERATION)))
    if (click_vel > TOPSPEED) :
        click_vel = TOPSPEED
    return click_vel*modifier

def forward(distance):
    '''Moves K9 forward by 'distance' metres
    '''
    # calculate an even number of clicks
    clicks = 2*int(distance/CLICK2METRES/2)
    click_vel = calc_click_vel(clicks)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(click_vel),distance1=int(clicks/2),speed2=int(click_vel),distance2=int(clicks/2),buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(0),distance1=int(clicks/2),speed2=int(0),distance2=int(clicks/2),buffer=int(0))
    if sim:
        print "Moving in straight line..."
        print "Speed=" + str(click_vel) +" Distance="+ str(clicks) + "\n"
        turtle.forward(clicks)

fd = fwd = forward

def backward(distance):
    '''Moves K9 backward by 'distance' metres
    '''
    forward(-1*distance)

back = bk = backward

def left(angle):
    '''Moves K9 right by 'angle' radians
    '''
    fraction = angle/2*math.pi
    clicks = 2*int(TURNING_CIRCLE*fraction/2)
    click_vel = calc_click_vel(clicks)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(-click_vel),distance1=int(clicks/2),speed2=int(click_vel),distance2=int(clicks/2),buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(0),distance1=int(clicks/2),speed2=int(0),distance2=int(clicks/2),buffer=int(0))
    if sim:
        print "Spinning..."
        print "Speed=" + str(click_vel) +" Distance="+ str(clicks) + "\n"
        turtle.left(angle)

lt = left

def right(angle):
    '''Moves K9 left by 'angle' radians
    '''
    left(-1*angle)

rt = right

def circle(radius,extent):
    '''Moves K9 in a circle or arc

    Arguments:
    radius -- radius in metres
    extent -- signed size of arc in radians e.g. -3.141 will move K9 in a
              a 180 semi-circle to the right

    '''
    distance1 = int(extent*(radius-HALF_WHEEL_GAP)/CLICK2METRES)
    distance2 = int(extent*(radius+HALF_WHEEL_GAP)/CLICK2METRES)
    click_vel1 = calc_click_vel(distance1)
    click_vel2 = calc_click_vel(distance2)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(-click_vel1),distance1=int(distance1/2),speed2=int(click_vel2),distance2=int(distance2/2),buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(0),distance1=int(distance1/2),speed2=int(0),distance2=int(distance2/2),buffer=int(0))
    if sim:
        print "Moving in circle..."
        print "M1 Speed=" + str(click_vel1) +" Distance="+ str(distance1)
        print "M2 Speed=" + str(click_vel2) +" Distance="+ str(distance2) + "\n"
        if (extent < 0) :
            radius = radius * -1
            extent = extent * -1
        turtle.circle(radius/CLICK2METRES,extent)

def finished():
    '''Checks to see if last robot movement has been completed
    '''
    if not sim:
        buffers = rc.ReadBuffers(address);
        if (buffers[1]==0x80 or buffers[2]==0x80):
            return False
    return True

# if executed from the command line then execute a test sequence
if __name__ == '__main__' :
    forward(6.7)
    while not finished():
        pass
    left(math.pi)
    while not finished():
        pass
    fd(1.0)
    while not finished():
        pass
    backward(1)
    while not finished():
        pass
    fwd(6)
    while not finished():
        pass
    circle(0.55,-math.pi/2)
    while not finished():
        pass
    circle(0.3,math.pi)
    while not finished():
        pass
    forward(.15)
    while not finished():
        pass
    circle(0.40,math.pi/2)
    while not finished():
        pass
    bk(0.350)
    while not finished():
        pass
    forward(0.35)
    while not finished():
        pass
    rt(2*math.pi)
    while not finished():
        pass
    time.sleep(10)

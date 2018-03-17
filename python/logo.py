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
WALKINGSPEED = 1 # top speed of robot in metres per second
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

def stop():
    '''Lock motors to stop motion
    '''
    if not sim:
        print "Stopping"
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=0,distance1=0,speed2=0,distance2=0,buffer=int(0))
        print "Stop done"

def waitForMove2Finish():
    ''' Waits until robot has finished move
    '''
    if not sim:
        buffers = (0,0,0)
        while (buffers[1]!=0x80 and buffers[2]!=0x80):
            buffers = rc.ReadBuffers(address);
            print "Waiting"
    stop()

def calc_turn_modifier(radius):
    turn_modifier = 1 - (0.9/(radius+1))
    return turn_modifier

def calc_click_vel(clicks,turn_mod):
    '''Calculates target velocity for motors

    Arguments:
    clicks -- a signed click distance
    turn_mod -- a modifier based on radius of turn

    '''
    sign_modifier = 1
    if (clicks<0):
        sign_modifier = -1
    click_vel = math.sqrt(abs(float(2*clicks*ACCELERATION*turn_mod)))
    if (click_vel > TOPSPEED*turn_mod) :
        click_vel = TOPSPEED*turn_mod
    return click_vel*sign_modifier

def forward(distance):
    '''Moves K9 forward by 'distance' metres
    '''
    # calculate an even number of clicks
    clicks = 2*int(distance/CLICK2METRES/2)
    click_vel = calc_click_vel(clicks=clicks,turn_mod=1)
    print "Clicks: " + str(clicks) + " Velocity: " + str(click_vel)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=int(click_vel),distance1=int(abs(clicks/2)),speed2=int(click_vel),distance2=int(abs(clicks/2)),buffer=1
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION),speed1=0,distance1=int(abs(clicks/2)),speed2=0,distance2=int(abs(clicks/2)),buffer=0
    if sim:
        print "Moving in straight line..."
        print "Speed=" + str(click_vel) + " Distance="+ str(clicks) + "\n"
        turtle.forward(clicks)
    waitForMove2Finish()

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
    turn_modifier = calc_turn_modifier(radius=0)
    click_vel = calc_click_vel(clicks=clicks,turn_mod=turn_modifier)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION*turn_modifier),speed1=int(-click_vel),distance1=int(abs(clicks/2)),speed2=int(click_vel),distance2=int(abs(clicks/2)),buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION*turn_modifier),speed1=int(0),distance1=int(abs(clicks/2)),speed2=int(0),distance2=int(abs(clicks/2)),buffer=int(0))
    if sim:
        print "Spinning..."
        print "Speed=" + str(click_vel) +" Distance="+ str(clicks) + "\n"
        turtle.left(angle)
    waitForMove2Finish()

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
    turn_mod1 = calc_turn_modifier(radius-HALF_WHEEL_GAP)
    turn_mod2 = calc_turn_modifier(radius+HALF_WHEEL_GAP)
    click_vel1 = calc_click_vel(clicks=distance1,turn_mod=turn_mod1)
    click_vel2 = calc_click_vel(clicks=distance2,turn_mod=turn_mod2)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION*turn_mod1),speed1=int(-click_vel1),distance1=int(abs(distance1/2)),speed2=int(click_vel2),distance2=int(abs(distance2/2)),buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,accel=int(ACCELERATION*turn_mod2),speed1=int(0),distance1=int(abs(distance1/2)),speed2=int(0),distance2=int(abs(distance2/2)),buffer=int(0))
    if sim:
        print "Moving in circle..."
        print "M1 Speed=" + str(click_vel1) +" Distance="+ str(distance1)
        print "M2 Speed=" + str(click_vel2) +" Distance="+ str(distance2) + "\n"
        if (extent < 0) :
            radius = radius * -1
            extent = extent * -1
        turtle.circle(radius/CLICK2METRES,extent)
    waitForMove2Finish()

def finished():
    '''Checks to see if last robot movement has been completed
    '''
    if not sim:
        buffers = rc.ReadBuffers(address);
        if (buffers[1]==0x80 and buffers[2]==0x80):
            return True
    return False

# if executed from the command line then execute a test sequence
if __name__ == '__main__' :
    forward(6.7)
    left(math.pi)
    fd(1.0)
    backward(1)
    fwd(6)
    circle(0.55,-math.pi/2)
    circle(0.3,math.pi)
    forward(.15)
    circle(0.40,math.pi/2)
    bk(0.350)
    forward(0.35)
    rt(2*math.pi)
    time.sleep(10)

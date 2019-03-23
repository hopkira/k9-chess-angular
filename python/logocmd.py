# -*- coding: utf-8 -*-
#
# K9's Movement Subsystem - Autonomous Motor Driver
#
# authored by Richard Hopkins March 2019
#
# Licensed under The Unlicense, so free for public domain use
#
# This program provides K9 with a stack of instructions for his movement

import time
import math
import sys
import argparse

sim = False

try:
    if __name__ == '__main__':
        if (len(sys.argv) > 1):
            verb = sys.argv[1]
            object = float(sys.argv[2])
            if (verb == "circle" and len(sys.argv) > 2):
                object2 = float(sys.argv[3])
                if (len(sys.argv) > 3):
                    if (sys.argv[4] == "test"):
                        sim = True
                        print "Test mode active"
            if (len(sys.argv) > 2):
                if (sys.argv[3] == "test"):
                    sim = True
                    print "Test mode active"
except IndexError:
    print "Please use valid arguments"

# Wheel circumference is 0.44m, with 36 clicks per turn
# Each click is 0.012
CLICK2METRES = 0.012  # converts clicks to metres
WALKINGSPEED = 1.4  # top speed of robot in metres per second
TOPSPEED = int(WALKINGSPEED/CLICK2METRES)  # calculate and store max velocity
ACCELERATION = int(2*TOPSPEED)  # accelerate to top speed in 0.5s
TURNING_CIRCLE = int(0.6/CLICK2METRES)  # clicks in a full spin
HALF_WHEEL_GAP = 0.095  # half the distance between the wheels
M1_QPPS = 740  # max speed of wheel in clicks per second
M2_QPPS = 700
M1_P = 20000  # Proportional element of feedback for PID controller
M2_P = 20000
M1_I = 2000  # Integral element of feedback for PID controller
M2_I = 2000
M1_D = 0  # Derived element of feedback for PID controller
M2_D = 0

if not sim:
    #  Initialise the roboclaw motorcontroller
    print "Initialising roboclaw driver..."
    from roboclaw import Roboclaw
    rc = Roboclaw("/dev/roboclaw", 115200)
    rc.Open()
    rc_address = 0x80
    # Get roboclaw version to test if is attached
    version = rc.ReadVersion(rc_address)
    if version[0] is False:
        print "Roboclaw get version failed"
        sys.exit()
    else:
        print repr(version[1])
        # Set PID variables to those required by K9
        rc.SetM1VelocityPID(rc_address, M1_P, M1_I, M1_D, M1_QPPS)
        rc.SetM2VelocityPID(rc_address, M2_P, M2_I, M2_D, M2_QPPS)
        # Zero the motor encoders
        rc.ResetEncoders(rc_address)
        print "PID variables set on roboclaw"


def stop():
    '''Lock motors to stop motion
    '''
    print "Stopping"
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION),
                                  speed1=0,
                                  distance1=0,
                                  speed2=0,
                                  distance2=0,
                                  buffer=int(0))
    print "Stop done"


def waitForMove2Finish():
    ''' Waits until robot has finished move
    '''
    print "Wating for move to finish..."
    if not sim:
        buffers = (0, 0, 0)
        while (buffers[1] != 0x80 and buffers[2] != 0x80):
            buffers = rc.ReadBuffers(address)
            time.sleep(0.05)
    stop()


def calc_turn_modifier(radius):
    '''Calculates a velocity modifier; based on the radius
    of the turn.  As the radius tends to zero (i.e. spinning on the spot),
    then modifier will reduce velocity to 10% of normal.
    As the radius increases, the allowed maximum speed will increase.

    Arguments:
    radius -- the radius of the turn being asked for in metres
    '''
    radius = abs(radius)
    turn_modifier = 1 - (0.9/(radius+1))
    print "Turn modifier is: " + str(turn_modifier)
    return turn_modifier


def calc_click_vel(clicks, turn_mod):
    '''Calculates target velocity for motors

    Arguments:
    clicks -- a signed click distance
    turn_mod -- a modifier based on radius of turn

    '''
    sign_modifier = 1
    if (clicks < 0):
        sign_modifier = -1
    click_vel = math.sqrt(abs(float(2*clicks*ACCELERATION*turn_mod)))
    if (click_vel > TOPSPEED*turn_mod):
        click_vel = TOPSPEED*turn_mod
    print "Calculated target velocity: " + str(click_vel*sign_modifier)
    return click_vel*sign_modifier


def forward(distance):
    '''Moves K9 forward by 'distance' metres

    Arguments:
    distance -- the distance to move in metres
    '''
    # calculate an even number of clicks
    clicks = 2*int(distance/CLICK2METRES/2)
    click_vel = calc_click_vel(clicks=clicks, turn_mod=1)
    print "Clicks: " + str(clicks) + " Velocity: " + str(click_vel)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION),
                                  speed1=int(click_vel),
                                  distance1=int(abs(clicks/2)),
                                  speed2=int(click_vel),
                                  distance2=int(abs(clicks/2)),
                                  buffer=1)
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION),
                                  speed1=0,
                                  distance1=int(abs(clicks/2)),
                                  speed2=0,
                                  distance2=int(abs(clicks/2)),
                                  buffer=0)
    waitForMove2Finish()


fd = fwd = forwards = forward


def backward(distance):
    '''Moves K9 backward by 'distance' metres
    '''
    forward(-1*distance)


back = bk = backwards = backward


def left(angle):
    '''Moves K9 right by 'angle' radians
    '''
    fraction = angle/2*math.pi
    clicks = 2*int(TURNING_CIRCLE*fraction/2)
    turn_modifier = calc_turn_modifier(radius=0)
    click_vel = calc_click_vel(clicks=clicks, turn_mod=turn_modifier)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION*turn_modifier),
                                  speed1=int(-click_vel),
                                  distance1=int(abs(clicks/2)),
                                  speed2=int(click_vel),
                                  distance2=int(abs(clicks/2)),
                                  buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION*turn_modifier),
                                  speed1=int(0),
                                  distance1=int(abs(clicks/2)),
                                  speed2=int(0),
                                  distance2=int(abs(clicks/2)),
                                  buffer=int(0))
    print "Spinning..."
    print "Speed=" + str(click_vel) + " Distance=" + str(clicks) + "\n"
    waitForMove2Finish()


lt = left


def right(angle):
    '''Moves K9 left by 'angle' radians
    '''
    left(-1*angle)


rt = right


def circle(radius, extent):
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
    click_vel1 = calc_click_vel(clicks=distance1, turn_mod=turn_mod1)
    click_vel2 = calc_click_vel(clicks=distance2, turn_mod=turn_mod2)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION*turn_mod1),
                                  speed1=int(-click_vel1),
                                  distance1=int(abs(distance1/2)),
                                  speed2=int(click_vel2),
                                  distance2=int(abs(distance2/2)),
                                  buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=address,
                                  accel=int(ACCELERATION*turn_mod2),
                                  speed1=int(0),
                                  distance1=int(abs(distance1/2)),
                                  speed2=int(0),
                                  distance2=int(abs(distance2/2)),
                                  buffer=int(0))
    print "Moving in circle..."
    print "M1 Speed=" + str(click_vel1) + " Distance=" + str(distance1)
    print "M2 Speed=" + str(click_vel2) + " Distance=" + str(distance2) + "\n"
    waitForMove2Finish()


def finished():
    '''Checks to see if last robot movement has been completed
    '''
    if not sim:
        buffers = rc.ReadBuffers(address)
        if (buffers[1] == 0x80 and buffers[2] == 0x80):
            return True
    return False


# if executed from the command line then execute arguments as functions
if __name__ == '__main__':
    if (verb == "circle"):
        locals()[verb](object, object2)
    else:
        locals()[verb](object)

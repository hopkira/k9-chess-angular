# -*- coding: utf-8 -*-
#
# K9's Movement Subsystem - Autonomous Motor Driver
#
# authored by Richard Hopkins January 2020
#
# Licensed under The Unlicense, so free for public domain use
#
# This program provides K9 with a stack of instructions for his movement

import time
import math
import sys
import argparse

sim = False

# Wheel circumference is 0.436m, with 200 clicks per turn
# Each click is 0.002179m (assumes each wheel is 0.139m)
CLICK2METRES = 0.002179  # converts clicks to metres
WALKINGSPEED = 1.4  # top speed of robot in metres per second
TOPSPEED = int(WALKINGSPEED/CLICK2METRES)  # calculate and store max velocity
ACCELERATION = int(TOPSPEED/5)  # accelerate to top speed in 5s
HALF_WHEEL_GAP = 0.1011
TURNING_CIRCLE = 2*math.pi*HALF_WHEEL_GAP/CLICK2METRES  # clicks in a full spin
#print("Turning circle:" + str(TURNING_CIRCLE))
M1_QPPS = 1987   # max speed of wheel in clicks per second
M2_QPPS = 1837
M1_P = 10.644  # Proportional element of feedback for PID controller
M2_P = 9.768
M1_I = 2.206  # Integral element of feedback for PID controller
M2_I = 2.294
M1_D = 0.0  # Derived element of feedback for PID controller
M2_D = 0.0

def main():
    global sim
    parser = argparse.ArgumentParser(description='Moves robot using logo commands.')
    parser.add_argument('command',
                        choices=['arc','fd','bk','lt','rt','stop'],
                        help='movement command')
    parser.add_argument('parameter',
                        type=float,
                        default=0.0,
                        nargs='?',
                        help='distance in metres or angle in radians')
    parser.add_argument('radius',
                        type=float,
                        default=0.0,
                        nargs='?',
                        help='radius of arc in metres (arc  only)')
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help='execute in simulation mode')
    args = parser.parse_args()
    sim = args.test
    verb = args.command
    object1 = args.parameter
    object2 = args.radius
    if sim:
        print("Test mode active")
    else:
        init_rc()
    if (verb == "arc"):
        globals()[verb](object1, object2)
    else:
        globals()[verb](object1)

def stop():
    '''Lock motors to stop motion
    '''
    global rc
    print("Stopping")
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=int(ACCELERATION),
                                  speed1=0,
                                  distance1=0,
                                  speed2=0,
                                  distance2=0,
                                  buffer=int(0))
    print("Stop done")


def waitForMove2Finish():
    ''' Waits until robot has finished move
    '''
    if not sim:
        while(motors_moving() or buffer_full()):
            time.sleep(0.1)
    print("Move finished")

def motors_moving():
    ''' Detects that motors are moving
    '''
    global rc
    m1_speed = rc.ReadSpeedM1(rc_address)
    m2_speed = rc.ReadSpeedM2(rc_address)
    return ((m1_speed[1] != 0) or (m2_speed[1] != 0))

def buffer_full():
    ''' Detects if moves have finished
    '''
    global rc
    buffers = rc.ReadBuffers(rc_address)
    return ((buffers[1] != 0x80) or (buffers[2] != 0x80))


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
    print("Turn modifier is: " + str(turn_modifier))
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
    print("Calculated target velocity: " + str(click_vel*sign_modifier))
    return click_vel*sign_modifier

def calc_accel(velocity,distance):
    '''Calculates desired constant acceleration
    
    Arguments:
    velocity -- the desired change in velocity
    distance -- the distance to change the velocity over
    '''
    accel = int(abs(velocity*velocity/(2*distance)))
    return accel

def forward(distance):
    '''Moves K9 forward by 'distance' metres

    Arguments:
    distance -- the distance to move in metres
    '''
    global rc
    clicks = int(round(distance/CLICK2METRES))
    click_vel = calc_click_vel(clicks=clicks, turn_mod=1)
    accel = calc_accel(click_vel, clicks/2)
    print("Clicks: " + str(clicks) + " Velocity: " + str(click_vel))
    if not sim:                       
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=accel,
                                  speed1=int(round(click_vel)),
                                  distance1=int(abs(clicks/2)),
                                  speed2=int(round(click_vel)),
                                  distance2=int(abs(clicks/2)),
                                  buffer=1)
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=accel,
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
    global rc
    fraction = angle/(2*math.pi)
    clicks = TURNING_CIRCLE*fraction
    turn_modifier = calc_turn_modifier(radius=0)
    click_vel = calc_click_vel(clicks=clicks, turn_mod=turn_modifier)
    accel = int(abs(click_vel*click_vel/(2*clicks/2)))
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=accel,
                                  speed1=int(round(-click_vel)),
                                  distance1=abs(int(round(clicks/2))),
                                  speed2=int(round(click_vel)),
                                  distance2=abs(int(round(clicks/2))),
                                  buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=accel,
                                  speed1=int(0),
                                  distance1=abs(int(round(clicks/2))),
                                  speed2=int(0),
                                  distance2=abs(int(round(clicks/2))),
                                  buffer=int(0))
    print("Spinning...")
    print("Speed=" + str(click_vel) + " Distance=" + str(clicks) + "\n")
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
    global rc
    distance1 = int(extent*(radius-HALF_WHEEL_GAP)/CLICK2METRES)
    distance2 = int(extent*(radius+HALF_WHEEL_GAP)/CLICK2METRES)
    turn_mod1 = calc_turn_modifier(radius-HALF_WHEEL_GAP)
    turn_mod2 = calc_turn_modifier(radius+HALF_WHEEL_GAP)
    click_vel1 = calc_click_vel(clicks=distance1, turn_mod=turn_mod1)
    click_vel2 = calc_click_vel(clicks=distance2, turn_mod=turn_mod2)
    if not sim:
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=int(ACCELERATION*turn_mod1),
                                  speed1=int(-click_vel1),
                                  distance1=int(abs(distance1/2)),
                                  speed2=int(click_vel2),
                                  distance2=int(abs(distance2/2)),
                                  buffer=int(1))
        rc.SpeedAccelDistanceM1M2(address=rc_address,
                                  accel=int(ACCELERATION),
                                  speed1=int(0),
                                  distance1=int(abs(distance1/2)),
                                  speed2=int(0),
                                  distance2=int(abs(distance2/2)),
                                  buffer=int(0))
    print("Moving in circle...")
    print("M1 Speed=" + str(click_vel1) + " Distance=" + str(distance1))
    print("M2 Speed=" + str(click_vel2) + " Distance=" + str(distance2) + "\n")
    waitForMove2Finish()

arc = circle

def init_rc():
    global rc
    global rc_address
    #  Initialise the roboclaw motorcontroller
    print("Initialising roboclaw driver...")
    from roboclaw import Roboclaw
    rc_address = 0x80
    rc = Roboclaw("/dev/roboclaw", 115200)
    rc.Open()
    # Get roboclaw version to test if is attached
    version = rc.ReadVersion(rc_address)
    if version[0] is False:
        print("Roboclaw get version failed")
        sys.exit()
    else:
        print(repr(version[1]))

    # Set motor controller variables to those required by K9
    rc.SetM1VelocityPID(rc_address, M1_P, M1_I, M1_D, M1_QPPS)
    rc.SetM2VelocityPID(rc_address, M2_P, M2_I, M2_D, M2_QPPS)
    rc.SetMainVoltages(rc_address,232,290) # 23.2V min, 29V max
    rc.SetPinFunctions(rc_address,2,0,0)
    # Zero the motor encoders
    rc.ResetEncoders(rc_address)

    # Print Motor PID Settings
    m1pid = rc.ReadM1VelocityPID(rc_address)
    m2pid = rc.ReadM2VelocityPID(rc_address)
    print("M1 P: " + str(m1pid[1]) + ", I:" + str(m1pid[2]) + ", D:" + str(m1pid[3]))
    print("M2 P: " + str(m2pid[1]) + ", I:" + str(m2pid[2]) + ", D:" + str(m2pid[3]))
    # Print Min and Max Main Battery Settings
    minmaxv = rc.ReadMinMaxMainVoltages(rc_address) # get min max volts
    print ("Min Main Battery: " + str(int(minmaxv[1])/10) + "V")
    print ("Max Main Battery: " + str(int(minmaxv[2])/10) + "V")
    # Print S3, S4 and S5 Modes
    S3mode=['Default','E-Stop (latching)','E-Stop','Voltage Clamp','Undefined']
    S4mode=['Disabled','E-Stop (latching)','E-Stop','Voltage Clamp','M1 Home']
    S5mode=['Disabled','E-Stop (latching)','E-Stop','Voltage Clamp','M2 Home']
    pinfunc = rc.ReadPinFunctions(rc_address)
    print ("S3 pin: " + S3mode[pinfunc[1]])
    print ("S4 pin: " + S4mode[pinfunc[2]])
    print ("S5 pin: " + S5mode[pinfunc[3]])
    print("Roboclaw motor controller initialised...")


# if executed from the command line then execute arguments as functions
if __name__ == '__main__':
    main()
else:
    init_rc()

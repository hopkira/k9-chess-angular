# -*- coding: utf-8 -*-
#
# Ultrasonic Data Collection using Encoders
#
# authored by Richard Hopkins January 2020
#
# Licensed under The Unlicense, so free for public domain use
#
# This program moves K9 in a circle and collects ultrasonic transmitter
# data at each point in its revolution
# it can take parameters for different behaviours and distances

import math
import argparse
import serial
import time
import logo

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

print("Initialising roboclaw driver...")
from roboclaw import Roboclaw
rc_address = 0x80
rc = Roboclaw("/dev/roboclaw", 115200)
rc.Open()

# Set motor controller variables to those required by K9
rc.SetM1VelocityPID(rc_address, M1_P, M1_I, M1_D, M1_QPPS)
rc.SetM2VelocityPID(rc_address, M2_P, M2_I, M2_D, M2_QPPS)
rc.SetMainVoltages(rc_address,232,290) # 23.2V min, 29V max
rc.SetPinFunctions(rc_address,2,0,0)
# Zero the motor encoders
rc.ResetEncoders(rc_address)

def waitForMove2Finish():
    ''' Waits until robot has finished move
    '''
    while(motors_moving() or buffer_full()):
        print(rc.ReadEncM1)
        # read encoder value and work out angle
        sine = (1 + math.sin(angle)) / 2
        cosine = (1 + math.cos(angle)) / 2
        distance = args.distance/3
        #sensors.reset_input_buffer()
        events = 0
        while (events < args.readings):
            #message = sensors.readline()   # read a '\n' terminated line
            message = "dummy"
            output_file.write("{input:[" +
                              message +
                              "],output: [" +
                              str(sine) + "," +
                              str(cosine) + "," +
                              str(distance) + "]},\n")

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


def main():
    parser = argparse.ArgumentParser(description='Collects ultrasonic data.')
    parser.add_argument('-f', '--output-file',
                        default='output',
                        help='name of output CSV file')
    parser.add_argument('-d', '--distance',
                        type=float,
                        default=1.0,
                        help='distance to ultrasonic transmitter')
    parser.add_argument('-c', '--clockwise',
                        action='store_true',
                        help='turn robot clockwise')
    args = parser.parse_args()
    #sensors = serial.Serial('/dev/ttyESPFollow', 115200, timeout=1)
    new_filename = args.output_file + '.csv'
    output_file = open(new_filename, "wt")
    my_input = raw_input("Press Enter to begin data collection...")

    fraction = 1
    clicks = TURNING_CIRCLE*fraction
    turn_modifier = calc_turn_modifier(radius=0)
    click_vel = calc_click_vel(clicks=clicks, turn_mod=turn_modifier)
    accel = int(abs(click_vel*click_vel/(2*clicks/2)))
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

if __name__ == "__main__":
    main()

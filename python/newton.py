# -*- coding: utf-8 -*-
#
# Turn on the spot
#
# authored by Richard Hopkins March 2019
#
# Licensed under The Unlicense, so free for public domain use
#
# This program moves K9 in a circle

import math
import time
from roboclaw import Roboclaw
rc = Roboclaw("/dev/roboclaw", 115200)
rc.Open()
rc_address = 0x80
m1_qpps = 1762
m2_qpps = 1050
acceleration = 250
speed = 500
distance = 5000
# Get roboclaw version to test if is attached
version = rc.ReadVersion(rc_address)
# Set PID variables to those required by K9
rc.SetM1VelocityPID(rc_address, 8.55, 2.21, 0, m1_qpps)
rc.SetM2VelocityPID(rc_address, 8.96, 2.82, 0, m2_qpps)
# Zero the motor encoders
rc.ResetEncoders(rc_address)


def displayspeed():
    enc1 = rc.ReadEncM1(rc_address)
    enc2 = rc.ReadEncM2(rc_address)
    speed1 = rc.ReadSpeedM1(rc_address)
    speed2 = rc.ReadSpeedM2(rc_address)

    print("Encoder1:"),
    if(enc1[0] == 1):
        print enc1[1],
        print format(enc1[2],'02x'),
    else:
        print "failed",
    print "Encoder2:",
    if(enc2[0] == 1):
        print enc2[1],
        print format(enc2[2],'02x'),
    else:
        print "failed ",
    print "Speed1:",
    if(speed1[0]):
        print speed1[1],
    else:
        print "failed",
    print("Speed2:"),
    if(speed2[0]):
        print speed2[1]
    else:
        print "failed "


rc.SpeedAccelDistanceM1M2(address=rc_address,
                          accel=int(acceleration),
                          speed1=int(speed),
                          distance1=int(distance),
                          speed2=int(speed),
                          distance2=int(distance),
                          buffer=int(1))
rc.SpeedAccelDistanceM1M2(address=rc_address,
                          accel=int(acceleration),
                          speed1=int(0),
                          distance1=int(distance),
                          speed2=int(0),
                          distance2=int(distance),
                          buffer=int(0))

buffers = (0, 0, 0)
while(buffers[1] != 0x80 and buffers[2] != 0x80):
    displayspeed()
    buffers = rc.ReadBuffers(rc_address)
    time.sleep(0.1)

print '=== commands completed ==='

count = 0
while (count < 200):
    displayspeed()
    time.sleep(0.1)
    count += 1

print '=== experiment finished ==='

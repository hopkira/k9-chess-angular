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
from roboclaw import Roboclaw
rc = Roboclaw("/dev/roboclaw", 115200)
rc.Open()
rc_address = 0x80
m1_qpps = 740
m2_qpps = 700
acceleration = 6
speed = 12
distance = 12
# Get roboclaw version to test if is attached
version = rc.ReadVersion(rc_address)
# Set PID variables to those required by K9
rc.SetM1VelocityPID(rc_address, 20000, 2000, 0, m1_qpps)
rc.SetM2VelocityPID(rc_address, 20000, 2000, 0, m2_qpps)
# Zero the motor encoders
rc.ResetEncoders(rc_address)
rc.SpeedAccelDistanceM1M2(address=rc_address,
                          accel=int(acceleration),
                          speed1=int(-speed),
                          distance1=int(distance),
                          speed2=int(speed),
                          distance2=int(distance),
                          buffer=int(1))
rc.SpeedAccelDistanceM1M2(address=rc_address,
                          accel=acceleration,
                          speed1=int(0),
                          distance1=int(distance),
                          speed2=int(0),
                          distance2=int(distance),
                          buffer=int(0))

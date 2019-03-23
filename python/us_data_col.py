# -*- coding: utf-8 -*-
#
# Ultrasonic Data Collection
#
# authored by Richard Hopkins March 2019
#
# Licensed under The Unlicense, so free for public domain use
#
# This program moves K9 in a circle and collects ultrasonic transmitter
# data at each point in its revolution
# it can take parameters for different behaviours and distances

import time
import math
import sys
import argparse
import serial
import random
# import logocmd

# sensors = serial.Serial('/dev/ttyESPFollow', 115200, timeout=1)
sensors = serial.Serial('/dev/ttys9', 115200, timeout=1)
sensors.reset_input_buffer()
sensor_reading = sensors.readline()   # read a '\n' terminated line
print 'Timed out'


def main():
    parser = argparse.ArgumentParser(description='Collects ultrasonic data.')
    parser.add_argument('-f', '--output-file',
                        default='output',
                        help='name of output CSV file')
    parser.add_argument('-d', '--distance',
                        type=float,
                        default=1.0,
                        help='distance to ultrasonic transmitter')
    parser.add_argument('-m', '--motors',
                        action='store_true',
                        help='collect data with motors running')
    parser.add_argument('-s', '--steps',
                        type=int,
                        default=6,
                        help='number of data collection points')
    parser.add_argument('-c', '--clockwise',
                        action='store_true',
                        help='turn robot clockwise')
    args = parser.parse_args()
    new_filename = args.output_file + '.csv'
    output_file = open(new_filename, "wt")
    output_file.write("distance," + str(args.distance) + '\n')
    output_file.write("motors," + str(args.motors) + '\n')
    output_file.write("steps," + str(args.steps) + '\n')
    step = 0
    while (step < args.steps):
        front_left = random.uniform(0, 1)
        front_right = random.uniform(0, 1)
        right = random.uniform(0, 1)
        left = random.uniform(0, 1)
        back = random.uniform(0, 1)
        fraction = float(step) / float(args.steps)
        if (args.clockwise is False):
            angle = 2 * math.pi * fraction
        else:
            angle = 2 * math.pi * (1 - fraction)
        sine = (1 + math.sin(angle)) / 2
        cosine = (1 + math.cos(angle)) / 2
        output_file.write("{input:[" +
                          str(front_left) + "," +
                          str(front_right) + "," +
                          str(left) + "," +
                          str(right) + "," +
                          str(back) + "],output: [" +
                          str(sine) + "," +
                          str(cosine) + "," +
                          str(args.distance) + "]},\n")
        step += 1


if __name__ == "__main__":
    main()

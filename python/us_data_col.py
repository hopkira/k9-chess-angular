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

import math
import argparse
import serial
import time
import logo

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
    parser.add_argument('-r', '--readings',
                        type=int,
                        default=100,
                        help='number of readings at each point')
    args = parser.parse_args()
    #sensors = serial.Serial('/dev/ttyESPFollow', 115200, timeout=1)
    new_filename = args.output_file + '.csv'
    output_file = open(new_filename, "wt")
    output_file.write("distance," + str(args.distance) + '\n')
    output_file.write("motors," + str(args.motors) + '\n')
    output_file.write("steps," + str(args.steps) + '\n')
    output_file.write("total readings," +
                      str(args.steps * args.readings) +
                      '\n')
    my_input = raw_input("Press Enter to begin data collection...")
    print("I got here")
    step = 1
    turn_angle = 1 / float(args.steps)
    while (step <= args.steps):
        fraction = float(step) / float(args.steps)
        if (args.clockwise is False):
            angle = 2 * math.pi * fraction
            logo.left(turn_angle)
        else:
            angle = 2 * math.pi * (1 - fraction)
            logo.right(turn_angle)
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
            events += 1
        step += 1


if __name__ == "__main__":
    main()
    

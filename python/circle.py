# -*- coding: utf-8 -*-
#
# Turn on the spot
#
# authored by Richard Hopkins March 2019
#
# Licensed under The Unlicense, so free for public domain use
#
# This program moves K9 in a circle

import logocmd as logo
import math
import argparse


parser = argparse.ArgumentParser(description='Makes dog spin on the spot.')
parser.add_argument('-s', '--steps',
                    type=int,
                    default=6,
                    help='number of elements to spin')
args = parser.parse_args()
i = 0
while (i < args.steps):
    input("Press enter to make move " + str(i) + " of " + str(args.steps))
    logo.right(2 * math.pi / float(args.steps))

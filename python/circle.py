import logocmd as logo
import math


num = 6
i = 0
while (i < num):
    input("Press enter to make move " + str(i) + " of " + str(num))
    logo.right(2 * math.pi / num)

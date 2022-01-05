# ===========================================================================
# Simple routine to make K9's eye ligths change
# ===========================================================================
# Import the PCA9685 module.

import time
import board
import busio
import adafruit_pca9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

# 3%, 30%, 100%

for brightness in range(0, 65535, 5):
    pca.channels[0].duty_cycle = brightness
    time.sleep(0.05)

time.sleep(1.0)

for brightness in range(0, 65535, 5):
    pca.channels[0].duty_cycle = 65535-brightness
    time.sleep(0.05)

pca.channels[0].duty_cycle = 2000

time.sleep(1.0)

pca.channels[0].duty_cycle = 20000

time.sleep(1.0)

pca.channels[0].duty_cycle = 65535
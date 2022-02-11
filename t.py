import board
import adafruit_scd4x
import time

def get_scd():
    i2c = board.I2C()
    i2c.writeto(0x70,b'\x01')
    scd = adafruit_scd4x.SCD4X(i2c)
    scd.start_periodic_measurement()
    while not scd.data_ready:
        print('Waiting on data ...')
        time.sleep(1)
    print(scd.CO2)
    return scd
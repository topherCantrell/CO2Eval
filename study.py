import board
import time

import adafruit_scd4x
import adafruit_scd30
import adafruit_lps2x
import adafruit_sht31d
import adafruit_mcp9808
import adafruit_dht

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)

import serial

uart = serial.Serial('/dev/ttyS0',baudrate=19200)

i2c = board.I2C()

def log(msg):
    with open('/media/pi/616F-8050/root.txt','a') as f:
        f.write(msg+'\n')

# I2C bus multiplexer
def set_i2c_bus(bus_num): # 0 (bottom), 1 (middle), or 2 (top)
    #i2c.writeto(0x70,b'\x01') # Bottom
    # i2c.writeto(0x70,b'\x02') # Middle
    # i2c.writeto(0x70,b'\x04') # Top
    i = 1<<bus_num
    i2c.writeto(0x70,bytes([i]))
    time.sleep(0.5) # Just in case

# UART multiplexer
def set_uart(num):
    if num:
        GPIO.output(4,0)
    else:
        GPIO.output(4,1)
    time.sleep(0.5) # Just in case
    uart.reset_input_buffer()
    uart.reset_output_buffer()
    time.sleep(0.5) # Just in case

set_i2c_bus(0) # Bottom
scd4xB = adafruit_scd4x.SCD4X(i2c)
scd4xB.bus_num = 0
scd30B = adafruit_scd30.SCD30(i2c)
scd30B.bus_num = 0
#
set_i2c_bus(2) # Top
scd4xT = adafruit_scd4x.SCD4X(i2c)
print(dir(scd4xT))
scd4xT.bus_num = 2
scd30T = adafruit_scd30.SCD30(i2c)
scd30T.bus_num = 2
#
set_i2c_bus(1) # Middle
lps = adafruit_lps2x.LPS22(i2c)
sht = adafruit_sht31d.SHT31D(i2c)
mcp = adafruit_mcp9808.MCP9808(i2c)
#
dht = adafruit_dht.DHT11(board.D17, use_pulseio=False)

def get_scd4x_info(sensor):
    set_i2c_bus(sensor.bus_num)
    # altitude
    # ambient_pressure
    # temperature_offset
    # REMEMBER TO PERSIST_SETTINGS IF YOU CHANGE
    return {
        'altitude' : sensor.altitude,        
        'temperature_offset' : sensor.temperature_offset,
    }

print(get_scd4x_info(scd4xB))


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

# UART multiplexer
def set_uart(num):
    if num:
        GPIO.output(4,0)
    else:
        GPIO.output(4,1)

def test_T6115(m):
    uart.write(b'\xFF\xFE\x02\x02\x03')
    resp = uart.read(5)
    print('T6615 '+m+' CO2:',resp[3]*256+resp[4])

def test_scd40(m):
    # SCD41
    # Adafruit code: https://github.com/adafruit/Adafruit_CircuitPython_SCD4X
    # Adafruit guide: https://learn.adafruit.com/adafruit-scd-40-and-scd-41
    # Part datasheet: https://cdn.sparkfun.com/assets/d/4/9/a/d/Sensirion_CO2_Sensors_SCD4x_Datasheet.pdf
    # sudo python3 -m pip install adafruit-circuitpython-scd4x    
    scd4x = adafruit_scd4x.SCD4X(i2c)
    #print('SCD40 '+m+' serial:', scd4x.serial_number)
    scd4x.start_periodic_measurement()
    while not scd4x.data_ready:        
        time.sleep(1)    
    print('SCD40 '+m+' CO2:',scd4x.CO2)
    print('SCD40 '+m+' temperature:', scd4x.temperature)
    print('SCD40 '+m+' humidity:', scd4x.relative_humidity)

def test_scd30(m):
    # SCD30
    # Adafruit code: https://github.com/adafruit/Adafruit_CircuitPython_SCD30
    # Adafruit guide: https://learn.adafruit.com/adafruit-scd30 
    # Part datasheet: 
    # sudo python3 -m pip install adafruit-circuitpython-scd30    
    scd30 = adafruit_scd30.SCD30(i2c)
    while not scd30.data_available:        
        time.sleep(1)     
    print('SCD30 '+m+' CO2:',scd30.CO2)
    print('SCD30 '+m+' temperature:',scd30.temperature)
    print('SCD30 '+m+' humidity:',scd30.relative_humidity)

def test_lps22():
    # LPS22
    # https://learn.adafruit.com/adafruit-lps25-pressure-sensor
    # sudo python3 -m pip install adafruit-circuitpython-lps2x
    lps = adafruit_lps2x.LPS22(i2c)
    print('LPS22 pressure:', lps.pressure)
    print('LSP22 temperature:',lps.temperature)

def test_sht31():
    # SHT31
    # https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout
    # sudo python3 -m pip install adafruit-circuitpython-sht31d    
    sht = adafruit_sht31d.SHT31D(i2c)
    print('SHT31 humidity:', sht.relative_humidity)
    print('SHT31 temperature:', sht.temperature)

def test_mcp9808():
    # MCP9808
    # https://learn.adafruit.com/adafruit-mcp9808-precision-i2c-temperature-sensor-guide
    # sudo python3 -m pip install adafruit-circuitpython-mcp9808    
    mcp = adafruit_mcp9808.MCP9808(i2c)
    print('MCP temperature:', mcp.temperature)

def test_DHT11():
    # DHT11
    # https://learn.adafruit.com/dht 
    # sudo python3 -m pip install adafruit-circuitpython-dht
    # sudo apt install libgpiod2    
    dht = adafruit_dht.DHT11(board.D17, use_pulseio=False)
    print('DHT11 temperature:', dht.temperature)
    print('DHT11 humidity:', dht.humidity)

set_uart(0)
test_T6115('B')

set_uart(1)
test_T6115('T')

set_i2c_bus(0)
test_scd40('B')
test_scd30('B')

set_i2c_bus(2)
test_scd40('T')
test_scd30('T')

set_i2c_bus(1)
test_lps22()
test_sht31()
test_mcp9808()
test_DHT11()


import board
import time

import adafruit_scd4x
import adafruit_scd30
import adafruit_lps2x
import adafruit_sht31d
import adafruit_mcp9808
# import adafruit_dht

import T6615

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


# Configure BOTTOM SDC40
set_i2c_bus(0) # Bottom
scd4 = adafruit_scd4x.SCD4X(i2c)
#scd4.factory_reset()
#scd4.reinit()
scd4.persist_settings()
print('SCD40 B serial number:',scd4.serial_number)
print('SCD40 B altitude:',scd4.altitude)
print('SCD40 B temperature_offset:',scd4.temperature_offset)
print('SCD40 B self_calibration_enabled:',scd4.self_calibration_enabled)

# Configure TOP SCD40
set_i2c_bus(2) # Bottom
scd4 = adafruit_scd4x.SCD4X(i2c)
#scd4.factory_reset()
#scd4.reinit()
scd4.persist_settings()
print('SCD40 T serial number:',scd4.serial_number)
print('SCD40 T altitude:',scd4.altitude)
print('SCD40 T temperature_offset:',scd4.temperature_offset)
print('SCD40 T self_calibration_enabled:',scd4.self_calibration_enabled)

# Configure BOTTOM SCD30
set_i2c_bus(0) # Bottom
scd3 = adafruit_scd30.SCD30(i2c)
#scd3.self_calibration_enabled = True
#scd3.reset()
print('SCD30 B measurement_interval:',scd3.measurement_interval)
print('SCD30 B altitude:',scd3.altitude)
print('SCD30 B ambient_pressure:',scd3.ambient_pressure)
print('SCD30 B temperature_offset:',scd3.temperature_offset)
print('SCD30 B forced_recalibration_reference:',scd3.forced_recalibration_reference)
print('SCD30 B self_calibration_enabled:',scd3.self_calibration_enabled)
#
#scd3.self_calibration_enabled = True

# Configure TOP SCD30
set_i2c_bus(2) # TOP
scd3 = adafruit_scd30.SCD30(i2c)
#scd3.self_calibration_enabled = True
#scd3.reset()
print('SCD30 T measurement_interval:',scd3.measurement_interval)
print('SCD30 T altitude:',scd3.altitude)
print('SCD30 T ambient_pressure:',scd3.ambient_pressure)
print('SCD30 T temperature_offset:',scd3.temperature_offset)
print('SCD30 T forced_recalibration_reference:',scd3.forced_recalibration_reference)
print('SCD30 T self_calibration_enabled:',scd3.self_calibration_enabled)
#
#scd3.self_calibration_enabled = True

# Configure LPSS
set_i2c_bus(1) # MIDDLE
lps22 = adafruit_lps2x.LPS22(i2c)
print('LPS22 data_rate:',lps22.data_rate)

# Configure SHT31D
set_i2c_bus(1) # MIDDLE
sht31 = adafruit_sht31d.SHT31D(i2c)
print('SHT31 serial_number:',sht31.serial_number)
print('SHT31 status:',sht31.status)
print('SHT31 art:',sht31.art)
print('SHT31 clock_stretching:',sht31.clock_stretching)
print('SHT31 frequency:',sht31.frequency)
print('SHT31 heater:',sht31.heater)
print('SHT31 mode:',sht31.mode)

# Configure MCP9808
set_i2c_bus(1) # MIDDLE
mcp = adafruit_mcp9808.MCP9808(i2c)
print('MCP9808 critical_temperature:',mcp.critical_temperature)
print('MCP9808 lower_temperature:',mcp.lower_temperature)
print('MCP9808 upper_temperature:',mcp.upper_temperature)
print('MCP9808 resolution:',mcp.resolution)

# Configure DHT11
pass

# Configure BOTTOM T6615
set_uart(0)
co2 = T6615.T6615(uart,0xFE)
#co2.enable_idle(False)
#co2.set_reference_ppm(440)
#co2.do_single_point_calibration()
#print('T6615 B status:',co2.get_status())
#print('T6615 B single_point_calibration:', co2.get_single_point_calibration())
#print('T6615 B CO2:',co2.get_CO2())

set_uart(0)
print('T6615 B status:',co2.get_status())
print('T6615 B serial_number:', co2.get_serial_number())
print('T6615 B compile_subvol:', co2.get_compile_subvol())
print('T6615 B compile_date:', co2.get_compile_date())
print('T6615 B elevation:', co2.get_elevation())
print('T6615 B single_point_calibration:', co2.get_single_point_calibration())
#print(co2.reset_abc_logic())
#co2.set_abc_logic_enabled(False)

# Configure TOP T6615
set_uart(1)
co2 = T6615.T6615(uart,0xFE)
#co2.enable_idle(False)
print('T6615 T status:',co2.get_status())
print('T6615 T serial_number:', co2.get_serial_number())
print('T6615 T compile_subvol:', co2.get_compile_subvol())
print('T6615 T compile_date:', co2.get_compile_date())
print('T6615 T elevation:', co2.get_elevation())
print('T6615 T single_point_calibration:', co2.get_single_point_calibration())
#print('T6615 T self_calibration_enabled:', co2.get_abc_logic_enabled())
#print(co2.reset_abc_logic())
#co2.set_abc_logic_enabled(False)

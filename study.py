import board
import time
import datetime
import json

import aio_creds.py as CREDS

from Adafruit_IO import Client, Feed, Data 
aio = Client(username=CREDS.username, key=CREDS.key)

import SENSOR_SETTINGS as SETS

import adafruit_scd4x
import adafruit_scd30
import adafruit_lps2x
import adafruit_sht31d
import adafruit_mcp9808
import adafruit_dht
import T6615

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)

import serial

uart = serial.Serial('/dev/ttyS0',baudrate=19200,timeout=2)

i2c = board.I2C()

def log(msg):
    with open('/media/pi/616F-8050/root.txt','a') as f:
        f.write(msg+'\n')

# I2C bus multiplexer
def select_i2c_bus(bus): # 0 (bottom), 1 (middle), or 2 (top)    
    if bus=='TOP':
        v = b'\0x4'
    elif bus=='MIDDLE':
        v = b'\x02'
    elif bus=='BOTTOM':
        v = b'\x01'
    else:
        raise ValueError('Unknown bus name')    
    i2c.writeto(0x70,v)
    time.sleep(0.5) # Just in case

# UART multiplexer
def select_uart(num):
    if num:
        GPIO.output(4,0)
    else:
        GPIO.output(4,1)
    time.sleep(0.5) # Just in case
    uart.reset_input_buffer()
    uart.reset_output_buffer()
    time.sleep(0.5) # Just in case

def get_SCD40_info(scd4):
    select_i2c_bus(scd4.bus_name)
    return {
        'serial_number' : scd4.serial_number,
        'altitude' : scd4.altitude,        
        'temperature_offset' : scd4.temperature_offset,
        'self_calibration_enabled' : scd4.self_calibration_enabled,
    }

def get_SCD40_readings(scd4):
    select_i2c_bus(scd4.bus_name)
    while not scd4.data_ready:
        time.sleep(0.5)
    return {
        'co2':scd4.CO2,
        'temperature':scd4.temperature,
        'humidity':scd4.relative_humidity,
    }

def get_SCD30_info(scd3):
    select_i2c_bus(scd3.bus_name)
    return {
        'measurement_interval':scd3.measurement_interval,
        'altitude':scd3.altitude,
        'ambient_pressure':scd3.ambient_pressure,
        'temperature_offset':scd3.temperature_offset,
        'forced_recalibration_reference':scd3.forced_recalibration_reference,
        'self_calibration_enabled':scd3.self_calibration_enabled,
    }

def get_SCD30_readings(scd3):
    select_i2c_bus(scd3.bus_name)
    while not scd3.data_available:
        time.sleep(0.5)
    return {
        'co2':scd3.CO2,
        'temperature':scd3.temperature,
        'humidity':scd3.relative_humidity,
    }

def get_LPS22_info(lps):
    select_i2c_bus(lps.bus_name)
    return {
        'data_rate' : lps.data_rate,
    }

def get_LPS22_readings(lps):
    select_i2c_bus(lps.bus_name)
    return {
        'pressure' : lps.pressure,
        'temperature' : lps.temperature,
    }
    
def get_SHT31_info(sht):
    select_i2c_bus(sht.bus_name)
    return {
        'serial_number':sht.serial_number,
        'status':sht.status,
        'art':sht.art,
        'clock_stretching':sht.clock_stretching,
        'frequency':sht.frequency,
        'heater':sht.heater,
        'mode':sht.mode,
    }

def get_SHT31_readings(sht):
    select_i2c_bus(sht.bus_name)
    return {
        'temperature':sht.temperature,
        'humidity':sht.relative_humidity
    }

def get_MCP_info(mcp):
    select_i2c_bus(mcp.bus_name)
    return {
       'critical_temperature':mcp.critical_temperature,
        'lower_temperature':mcp.lower_temperature,
        'upper_temperature':mcp.upper_temperature,
        'resolution':mcp.resolution,
    }

def get_MCP_readings(mcp):
    select_i2c_bus(mcp.bus_name)
    return {
       'temperature':mcp.temperature,        
    }

def get_TEL_info(tel):
    select_uart(tel.uart_num)
    for _ in range(3):
        try:
            return {
                'status': tel.get_status(),
                'serial_number': tel.get_serial_number(),
                'compile_subvol': tel.get_compile_subvol(),
                'compile_date': tel.get_compile_date(),
                'elevation': tel.get_elevation(),
                'single_point_calibration': tel.get_single_point_calibration(),       
            }
        except Exception:
            print('RETRYING TELAIRE')
            time.sleep(0.5)


def get_TEL_readings(tel):
    select_uart(tel.uart_num)
    for _ in range(3):
        try:
            return {
                'co2': tel.get_CO2(),                
            }
        except Exception:
            print('RETRYING TELAIRE')
            time.sleep(0.5)

def get_DHT11_readings(dht):
    for _ in range(3):
        try:
            if dht.temperature is None or dht.humidity is None:
                continue
            return {
                'temperature': dht.temperature,
                'humidity': dht.humidity,                
            }
        except Exception:
            #print('RETRYING DHT')
            time.sleep(1)

def verify_settings(cur,exp):
    for key,value in exp.items():
        if cur[key] != value:
            raise ValueError('Not correct')

print('Connecting to sensors ...')
telA = T6615.T6615(uart,0xFE)
telA.uart_num = 0
telB = T6615.T6615(uart,0xFE)
telB.uart_num = 1

select_i2c_bus('BOTTOM')
co4B = adafruit_scd4x.SCD4X(i2c)
co4B.bus_name = 'BOTTOM'
co4B.stop_periodic_measurement()
co3B = adafruit_scd30.SCD30(i2c)
co3B.bus_name = 'BOTTOM'
co3B.self_calibration_enabled = True

select_i2c_bus('TOP')
co4T = adafruit_scd4x.SCD4X(i2c)
co4T.bus_name = 'TOP'
co4T.stop_periodic_measurement()
co3T = adafruit_scd30.SCD30(i2c)
co3T.bus_name = 'TOP'
co3T.self_calibration_enabled = True

select_i2c_bus('MIDDLE')
lps = adafruit_lps2x.LPS22(i2c)
lps.bus_name = 'MIDDLE'
sht = adafruit_sht31d.SHT31D(i2c)
sht.bus_name = 'MIDDLE'
mcp = adafruit_mcp9808.MCP9808(i2c)
mcp.bus_name = 'MIDDLE'
#
dht = adafruit_dht.DHT11(board.D17, use_pulseio=False)

# Verify sensors are configured correctly
print('Verifying sensor configuration ...')
info = get_SCD40_info(co4B)
verify_settings(info,SETS.CO4B)
info = get_SCD40_info(co4T)
verify_settings(info,SETS.CO4T)
info = get_SCD30_info(co3B)
verify_settings(info,SETS.CO3B)
info = get_SCD30_info(co3T)
verify_settings(info,SETS.CO3T)
info = get_LPS22_info(lps)
verify_settings(info,SETS.LPS)
info = get_SHT31_info(sht)
verify_settings(info,SETS.SHT)
info = get_MCP_info(mcp)
verify_settings(info,SETS.MCP)
info = get_TEL_info(telA)
verify_settings(info,SETS.TELA)
info = get_TEL_info(telB)
verify_settings(info,SETS.TELB)

# Sensor loop
print('Sensor loop ...')
select_i2c_bus(co4B.bus_name)
co4B.start_periodic_measurement()
select_i2c_bus(co4T.bus_name)
co4T.start_periodic_measurement()

while True:

    now = datetime.datetime.now()
    
    data = {
        'time':str(now),
        'telA':get_TEL_readings(telA),
        'telB':get_TEL_readings(telB),
        'co4B':get_SCD40_readings(co4B),
        'co4T':get_SCD40_readings(co4T),
        'co3B':get_SCD30_readings(co3B),
        'co3T':get_SCD30_readings(co3T),
        'sht31':get_SHT31_readings(sht),
        'lps22':get_LPS22_readings(lps),
        'mcp9808':get_MCP_readings(mcp),
        'dht11':get_DHT11_readings(dht),
    }

    try:
        print('Sending to adafruit.io')      
        if data['dht11']:         
            aio.send('sensor-study.dht11-dot-humidity',     data['dht11']['humidity']) 
            aio.send('sensor-study.dht11-dot-temperature',  data['dht11']['temperature'])
        else:
            print('Skipping DHT11')
            
        aio.send('sensor-study.lps22-dot-pressure',     data['lps22']['pressure'])
        aio.send('sensor-study.lps22-dot-temperature',  data['lps22']['temperature'])

        aio.send('sensor-study.mcp9808-dot-temperature',data['mcp9808']['temperature'])

        aio.send('sensor-study.scd30b-dot-co2',         data['co3B']['co2'])
        aio.send('sensor-study.scd30b-dot-temperature', data['co3B']['temperature'])
        aio.send('sensor-study.scd30b-dot-humidity',    data['co3B']['humidity'])

        aio.send('sensor-study.scd30t-dot-co2',         data['co3T']['co2'])
        aio.send('sensor-study.scd30t-dot-temperature', data['co3T']['temperature'])
        aio.send('sensor-study.scd30t-dot-humidity',    data['co3T']['humidity'])

        aio.send('sensor-study.scd40b-dot-co2',         data['co4B']['co2'])
        aio.send('sensor-study.scd40b-dot-temperature', data['co4B']['temperature'])
        aio.send('sensor-study.scd40b-dot-humidity',    data['co4B']['humidity'])

        aio.send('sensor-study.scd40t-dot-co2',         data['co4T']['co2'])
        aio.send('sensor-study.scd40t-dot-temperature', data['co4T']['temperature'])
        aio.send('sensor-study.scd40t-dot-humidity',    data['co4T']['humidity'])

        aio.send('sensor-study.sht31-dot-humidity',     data['sht31']['humidity'])
        aio.send('sensor-study.sht31-dot-temperature',  data['sht31']['temperature'])

        aio.send('sensor-study.telaireb-dot-co2',       data['telB']['co2'])
        aio.send('sensor-study.telairet-dot-co2',       data['telA']['co2'])
        
    except Exception:
        print('Error sending to adafruit.io')
        raise
    
    print(json.dumps(data))
    log(json.dumps(data))

    time.sleep(15*60) # Wait 15 minutes




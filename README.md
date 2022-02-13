# CO2Eval
Comparing 3 types of CO2 sensors (two instances of each) -- plus a handful
of temperature, humidity, and pressure sensors.

I am hoping to examine how CO2 sensors compare to each other and how they are affected by drift over time (without auto calibration).

## The live data is live
https://io.adafruit.com/topher_cantrell/dashboards/sensor-study

## Journal

My notes as the study progresses:

[journal.md](journal.md)

## Sensors

TODO: pictures of the hardware, sensor datasheets, etc

### Bit Bang
- DHT11

### UART0
- Telaire T6615

### UART1
- Telaire T6615

### I2C Bus 0
- Sensirion SCD30 i61
- Sensirion SCD40 i62
- SHT31 i44
- LPS22  i5D

### I2C Bus 1
- Sensirion SCD30 i61
- Sensirion SCD40 i62
- MCP9808 i30

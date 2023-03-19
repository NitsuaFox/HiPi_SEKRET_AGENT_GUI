import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(3,2)

# Create the ADS object
ads = ADS.ADS1115(i2c)

# Create an analog input channel on pin A0
chan = AnalogIn(ads, ADS.P0)

# Calibration values for the soil sensor
min_voltage = 2.44
max_voltage = 0.98

while True:
    # Read the analog value
    value = chan.value
    print('Raw ADC value: ', value)

    # Convert the analog value to voltage
    voltage = chan.voltage
    print('Voltage: ', voltage)

    # Convert voltage to percentage
    moisture_percent = (max_voltage - voltage) / (max_voltage - min_voltage) * 100
    moisture_percent = max(min(moisture_percent, 100), 0)
    print('Moisture level: {:.2f}%'.format(moisture_percent))

    # Wait for half a second before reading again
    time.sleep(0.5)

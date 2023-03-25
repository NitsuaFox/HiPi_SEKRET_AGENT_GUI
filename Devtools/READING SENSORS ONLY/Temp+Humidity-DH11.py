# Import the required libraries
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

# Set the sensor type and GPIO pin number
sensor = Adafruit_DHT.DHT22
pin = 17


# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    # Try to get the temperature and humidity values from the sensor
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Check if the values are valid (not None)
    if humidity is not None and temperature is not None:
        # Print the values
        print('Temperature: {:.1f}°C'.format(temperature))
        print('Humidity: {:.1f}%'.format(humidity))
    else:
        # Print an error message
        print('Failed to get temperature and humidity data.')

    # Wait for 2 seconds before reading again
    time.sleep(2)

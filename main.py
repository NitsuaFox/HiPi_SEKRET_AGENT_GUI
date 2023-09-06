# "HERBIE" HiPi v1.0
import threading
import time
import Adafruit_DHT
import RPi.GPIO as GPIO # Used for Reading/Writing GPIOS on Raspberry Pi Zero 2 W
import configparser

#Sensor Class - This class is used to enable multi-threading for all sensors. 
class Sensor: 
    def __init__(self):
        self.sensor_data = {'value': None}

    def read_data(self):
        pass

    def start_reading(self):
        sensor_thread = threading.Thread(target=self.read_data)
        sensor_thread.daemon = True
        sensor_thread.start()

#Soil Sensor Config for checking the soil of the plant.
class SoilMoistureSensor(Sensor):
    def read_data(self):
        while True:
            # Replace this with your own sensor reading code
            self.sensor_data['soil_value'] = 50
            time.sleep(1)

#DHT22 Sensor Config for Temp/Humid Readouts.
class TemperatureHumiditySensor(Sensor):
    SENSOR_TYPE = Adafruit_DHT.DHT22  # Change to Adafruit_DHT.DHT11 if using DHT11 sensor
    PIN = 27  # Replace with the GPIO pin number you have connected the DHT sensor to

    def read_data(self):
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(self.SENSOR_TYPE, self.PIN)
            if humidity is not None and temperature is not None:
                self.sensor_data['temperature_value'] = temperature
                self.sensor_data['humidity_value'] = humidity
            time.sleep(1)

#Ultrasonic Sensor for Checking Water level
class UltrasonicSensor(Sensor):
    TRIGGER_PIN = 5
    ECHO_PIN = 6

    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIGGER_PIN, GPIO.OUT)
        GPIO.setup(self.ECHO_PIN, GPIO.IN)

    def read_data(self):
        while True:
            GPIO.output(self.TRIGGER_PIN, True)
            time.sleep(0.00001)
            GPIO.output(self.TRIGGER_PIN, False)

            start_time = time.time()
            stop_time = time.time()

            while GPIO.input(self.ECHO_PIN) == 0:
                start_time = time.time()

            while GPIO.input(self.ECHO_PIN) == 1:
                stop_time = time.time()

            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2
            
            #print("Distance:", distance)  # Debugging print statement

            water_level = 100 - ((distance - 2) * (100 / (20 - 2))) # Assuming 2 cm is 100% and 20 cm is 0%
            water_level = max(0, min(100, water_level)) # Clamping water_level between 0 and 100
            water_level = int(round(water_level))  # Round and convert to integer

            self.sensor_data['water_value'] = water_level
            print("Water Level:", water_level)  # Debugging print statement
            time.sleep(1)

#Initialisation Class - Starts Main Menu that asks user questions, and sets up the inital config and passes the input  to 'GrowBoxRoutine' Class
class Initialisation:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        if not self.config.has_section('settings'):
            self.config.add_section('settings')
        
        self.target_temp = self.config.getint('settings', 'target_temp', fallback=0)
        self.light_cycle_mode = self.config.getint('settings', 'light_cycle_mode', fallback=0)

    def start_menu(self):
        print("1. Continue with current config")
        print("2. Update config")

        choice = input("Enter your choice (1 or 2): ")

        if choice == "2":
            # Update target temp
            self.target_temp = input("Input Target Temperature in Celsius: ")
            self.config.set('settings', 'target_temp', self.target_temp)
            print("Target Temperature set to: " + self.target_temp + " C")

            # Update light cycle mode
            print("Please select an initial start light cycle mode:")
            print("1. 12/12")
            print("2. 20/4")
            print("3. 18/6")
            print("4. Always On")

            while True:
                self.light_cycle_mode = input("Enter your choice (1-4): ")
                if self.light_cycle_mode in ["1", "2", "3", "4"]:
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 4.")
            self.config.set('settings', 'light_cycle_mode', self.light_cycle_mode)
            
            # Save the updated config to the file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

        # Convert data types and update instance variables
        self.target_temp = int(self.target_temp)
        self.light_cycle_mode = int(self.light_cycle_mode)

        # Move on to GrowBoxRoutine class
        GrowBoxRoutine(self.target_temp, self.light_cycle_mode)

# This is the main brains that creates the perfect climate based on 
# what the user has entered in the initalisation class, and by reading the sensors and working out
# best time to water the plant, what fan speed to run to try and cool things down.

class GrowBoxRoutine:
    def __init__(self, target_temp, light_cycle_mode):
        self.target_temp = target_temp
        self.light_cycle_mode = light_cycle_mode

        # Run the main routine
        self.run()

    def run(self):
        # Your code goes here
        print("Running the GrowBoxRoutine with the following settings:")
        print("Target Temperature:", self.target_temp, "C")
        print("Initial light cycle mode:", self.light_cycle_mode)

# Instantiate the Initialisation class and call the start_menu() function
init = Initialisation()
init.start_menu()

# Create instances of each sensor class
soil_moisture_sensor = SoilMoistureSensor()
temperature_humidity_sensor = TemperatureHumiditySensor()
ultrasonic_sensor = UltrasonicSensor()

# Start reading data for each sensor
soil_moisture_sensor.start_reading()
temperature_humidity_sensor.start_reading()
ultrasonic_sensor.start_reading()

# Your main program goes here
while True:
    # Access the sensor data from each instance
    print("Soil Moisture:", soil_moisture_sensor.sensor_data['soil_value'])
    print("Temperature:", temperature_humidity_sensor.sensor_data.get('temperature_value', 'N/A'))
    print("Humidity:", temperature_humidity_sensor.sensor_data.get('humidity_value', 'N/A'))
    print("Water Level:", ultrasonic_sensor.sensor_data['water_value'], "%")
    time.sleep(1)

# "HERBIE" HiPi v1.0

import threading
import time

class Sensor:

    def __init__(self):
        self.sensor_data = {}

    def read_data(self):
        pass

    def start_reading(self):
        sensor_thread = threading.Thread(target=self.read_data)
        sensor_thread.daemon = True
        sensor_thread.start()

class SoilMoistureSensor(Sensor):
    def read_data(self):
        while True:
            # Replace this with your own sensor reading code
            self.sensor_data['value'] = 50
            time.sleep(1)

class TemperatureSensor(Sensor):
    def read_data(self):
        while True:
            # Replace this with your own sensor reading code
            self.sensor_data['value'] = 25
            time.sleep(1)

class HumiditySensor(Sensor):
    def read_data(self):
        while True:
            # Replace this with your own sensor reading code
            self.sensor_data['value'] = 60
            time.sleep(1)

class UltrasonicSensor(Sensor):
    def read_data(self):
        while True:
            # Replace this with your own sensor reading code
            self.sensor_data['value'] = 10
            time.sleep(1)

class Initialisation:
    def __init__(self):
        self.target_temp = 0
        self.light_cycle_mode = 0

    def start_menu(self):
        # Ask for target temp
        self.target_temp = input("Input Target Temperature in Celsius: ")
        print("Target Temperature set to: " + self.target_temp + " C")

        # Ask for initial start light cycle mode
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

        if self.light_cycle_mode == "1":
            print("Initial light cycle mode set to 12/12.")
        elif self.light_cycle_mode == "2":
            print("Initial light cycle mode set to 20/4.")
        elif self.light_cycle_mode == "3":
            print("Initial light cycle mode set to 18/6.")
        else:
            print("Initial light cycle mode set to Always On.")

        # Convert data types and update instance variables
        self.target_temp = int(self.target_temp)
        self.light_cycle_mode = int(self.light_cycle_mode)

        # Move on to GrowBoxRoutine class
        GrowBoxRoutine(self.target_temp, self.light_cycle_mode)

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
temperature_sensor = TemperatureSensor()
humidity_sensor = HumiditySensor()
ultrasonic_sensor = UltrasonicSensor()

# Start reading data for each sensor
soil_moisture_sensor.start_reading()
temperature_sensor.start_reading()
humidity_sensor.start_reading()
ultrasonic_sensor.start_reading()

# Your main program goes here
while True:
    # Access the sensor data from each instance
    print("Soil Moisture:", soil_moisture_sensor.sensor_data['value'])
    print("Temperature:", temperature_sensor.sensor_data['value'])
    print("Humidity:", humidity_sensor.sensor_data['value'])
    print("Distance:", ultrasonic_sensor.sensor_data['value'])
    time.sleep(1)
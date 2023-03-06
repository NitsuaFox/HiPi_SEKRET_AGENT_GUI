#"HERBIE" Backend system for HiPi Growbox

# Include Libraries
from getch import getch
import time
import RPi.GPIO as GPIO
import configparser
import Adafruit_DHT
import threading
import time
import logging

# GPIO PINS
TRIGGER_PIN = 6 # Trigger for Ultrasonic Sensor
ECHO_PIN = 5 # Echo for Ultrasonic Sensor
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16
DHT22_PIN = 17
RELAY_WATERPUMP = 26

# GPIO SETUP MODE
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# GPIO SETUP
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)
GPIO.setup(DHT22_PIN, GPIO.IN, GPIO.PUD_DOWN)
#GPIO.setup(RELAY_WATERPUMP, GPIO.OUT)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log")  # Output to file
    ]
)

class SensorReturns:
    def __init__(self):
        self.distance_cm = 0
        self.humidity = 0
        self.temperature = 0

    def get_distance(self):
        # Send a 10us pulse to the trigger pin to start the measurement
        GPIO.output(TRIGGER_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIGGER_PIN, False)

        # Wait for the pulse to be returned
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()

        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start

        # Calculate the distance in centimeters
        self.distance_cm = round(pulse_duration * 17150, 2)

        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.05)

    def get_dht22_data(self):
        logging.info(f"Talking to DHT22....")
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN)
        if humidity is not None and temperature is not None:
            self.humidity = round(humidity, 1)
            self.temperature = round(temperature, 1)

    def get_sensor_data(self):
        while True:
            logging.info(f"Retrieving sensor data at {time.time()}...")
            self.get_distance()
            self.get_dht22_data()
            time.sleep(0.5)

sensor_returns = SensorReturns()

class SensorThread(threading.Thread):
    def __init__(self):
        super(SensorThread, self).__init__()
        self.daemon = True

    def run(self):
        logging.info("SensorThread is running")
        sensor_returns.get_sensor_data()

sensor_thread = SensorThread()


class Menu:
    def __init__(self):
        self.stop = False
    
    def print_main_menu(self):
        print("1. Print Current Sensor Data")
        print("2. Config")
    
    def print_sensor_returns_menu(self):
        print("1. Turn Sensor Returns On")
        print("2. Turn Sensor Returns Off")
        print("b. Back")


    def run(self):
        while not self.stop:
            self.print_main_menu()
            choice = input("Enter choice: ")
            if choice == "1":
                while True:
                    print(f"\r Sensor Data: Distance: {sensor_returns.distance_cm} cm, Humidity: {sensor_returns.humidity} %, Temperature: {sensor_returns.temperature} C")
                    print("Press 'x' to go back")
                    if getch() == 'x':
                        break
            elif choice == "2":
                while True:
                    self.print_sensor_returns_menu()
                    sensor_returns_choice = input("Enter choice: ")
                    if sensor_returns_choice == "1":
                        # Turn on sensor returns
                        break
                    elif sensor_returns_choice == "2":
                        # Turn off sensor returns
                        break
                    elif sensor_returns_choice.lower() == "b":
                        break
                    else:
                        print("Invalid choice")
            elif choice.lower() == "stop":
                self.stop = True
                break
            else:
                print("Invalid choice")


if __name__ == '__main__':
# Start the sensor thread
    sensor_thread.start()
    menu = Menu()
    menu.run()

# Cleanup GPIO
GPIO.cleanup()
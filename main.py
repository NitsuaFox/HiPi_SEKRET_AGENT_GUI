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

FAN_SPEED = 0

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
            logging.info(f"get_sensor_data -running {time.time()}...")
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

class FanController:
    def __init__(self, fan_pwm_pin, sensor_returns):
        self.fan_pwm_pin = fan_pwm_pin
        self.sensor_returns = sensor_returns
        self.pwm = GPIO.PWM(fan_pwm_pin, 100)
        self.pwm.start(0)

    def update_fan_speed(self):
        global FAN_SPEED
        temperature = self.sensor_returns.temperature
        # Example temperature thresholds
        if temperature >= 25:
            logging.info("FAN1-MAX%")
            # Fan speed should be 100%
            FAN_SPEED = 100
        elif temperature >= 23:
            # Fan speed should be 75%
            logging.info("FAN1-75%")
            FAN_SPEED = 75
        elif temperature >= 20:
            # Fan speed should be 50%
            logging.info("FAN1-50%")
            FAN_SPEED = 50
        else:
            # Fan speed should be 0%
            logging.info("FAN1-OFF%")
            FAN_SPEED = 0
        self.pwm.ChangeDutyCycle(FAN_SPEED)

    def run_fan_speed_test(self):
        # Run fan speed test
        pass

    def set_fan_speed(self):
        global FAN_SPEED
        while True:
            # Prompt user for new fan speed
            new_fan_speed_str = input("Enter new fan speed (0-100, or x to cancel): ")
            if new_fan_speed_str.lower() == "x":
                break
            try:
                new_fan_speed = float(new_fan_speed_str)
                if new_fan_speed < 0 or new_fan_speed > 100:
                    raise ValueError("Fan speed must be between 0 and 100")
                FAN_SPEED = new_fan_speed
                fan_controller.pwm.ChangeDutyCycle(FAN_SPEED)
                print(f"Fan speed set to {new_fan_speed}%")
            except ValueError as e:
                print(f"Invalid fan speed: {e}")

#############
#CONFIG MENU#
#############

class Menu:
    def __init__(self):
        self.stop = False

    def print_main_menu(self):
        print("   +++ HiPi Backend Menu +++")
        print("   =========================")
        print("1. Print Current Sensor Data")
        print("2. Sensor Setup")
        print("3. Climate Control Setup")
        print("4. Fan Control")

    def print_sensor_returns_menu(self):
        print("1. Turn Sensor Returns On")
        print("2. Turn Sensor Returns Off")

    def print_climate_setup_menu(self):
        print("1. Set Climate Target Temperature")
        print("2. Run Fan Speed Test")
        print("b. Back")

    def print_fan_control_menu(self):
        print("1. Set Fan Speed")
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
            elif choice == "3":
                while True:
                    self.print_climate_setup_menu()
                    climate_setup_choice = input("Enter choice: ")
                    if climate_setup_choice == "1":
                        fan_controller.set_climate_target_temperature()
                        break
                    elif climate_setup_choice == "2":
                        # Run fan speed test
                        break
                    elif climate_setup_choice.lower() == "b":
                        break
                    else:
                        print("Invalid choice")
            elif choice == "4":
                while True:
                    self.print_fan_control_menu()
                    fan_control_choice = input("Enter choice: ")
                    if fan_control_choice == "1":
                        fan_controller.set_fan_speed()
                        break
                    elif fan_control_choice.lower() == "b":
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

    # Create fan_controller
    fan_controller = FanController(FAN_PWM_PIN, sensor_returns)

    # Create Menu instance
    menu = Menu()
    menu.run()

    # Cleanup GPIO
    GPIO.cleanup()

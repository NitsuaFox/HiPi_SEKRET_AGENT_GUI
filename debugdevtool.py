#"HERBIE" Backend system for HiPi Growbox

# Include Libraries
from getch import getch
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import threading
import time
import logging
import configparser

#GLOBAL Settings
USERNAMEID = "Bobby" 
GROWBOXID = "MyHiPi"
FAN_SPEED = 0 # initiate at 0
TARGET_TEMP = 20 #default setting
#CONFIG_FILE = 'config.ini'
#DEADSPACE = 12

# GPIO PINS
TRIGGER_PIN = 6 # Trigger for Ultrasonic Sensor
ECHO_PIN = 5 # Echo for Ultrasonic Sensor
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16
DHT22_PIN = 17
RELAY_WATERPUMP = 26
SOIL_PIN = 23 #SOIL SENSOR

# GPIO SETUP MODE
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# GPIO SETUP
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)
GPIO.setup(DHT22_PIN, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(RELAY_WATERPUMP, GPIO.OUT)

# LOGGING SETUP
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log")  # Output to file
    ]
)

# CLASSES
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


        # Calculate the distance in centimeterss
        self.distance_cm = round(pulse_duration * 17150, 2)
        #logging.info("get_distance: I've calculated and stored the distance in self.distance_cm" )
        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.05)


    def get_dht22_data(self):
        #logging.info(f"Talking to DHT22....")
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN)
        if humidity is not None and temperature is not None:
            self.humidity = round(humidity, 1)
            self.temperature = round(temperature, 1)

    def get_sensor_data(self):
        while True:
            #logging.info(f"get_sensor_data -running {time.time()}...")
            self.get_distance()
            self.get_dht22_data()
            time.sleep(0.05)

sensor_returns = SensorReturns() ## WE NEED TO START THIS HERE.

class SensorThread(threading.Thread):
    def __init__(self):
        super(SensorThread, self).__init__()
        self.daemon = True

    def run(self):
        logging.info("SensorThread is running")
        sensor_returns.get_sensor_data()

sensor_thread = SensorThread() ## WE NEED TO START THIS HERE

class WateringSystem:
    def __init__(self, RELAY_WATERPUMP):
        self.RELAY_WATERPUMP = RELAY_WATERPUMP
        GPIO.setup(RELAY_WATERPUMP, GPIO.OUT)
        self.empty_range = 8.96 # This is the measurement of which it the water state just before the pump.
        

    def pump_on(self):
        GPIO.output(self.RELAY_WATERPUMP, GPIO.LOW)
        logging.info("Pump turned on")

    def pump_off(self):
        GPIO.output(self.RELAY_WATERPUMP, GPIO.HIGH)
        logging.info("Pump turned off")

    def test_pump(self):
            while True:
                # Check the distance measured by the sensor
                distance_cm = sensor_returns.distance_cm
                print("Inital Distance start of test_pump function test from distance_cm: " + str(distance_cm))

                if distance_cm < self.empty_range:
                    # Turn on the pump
                    self.pump_on()
                    logging.info("Pump started because water is above MINIMAL TANK LEVEL: " + str(distance_cm))

                    while True:
                        # Check the distance measured by the sensor
                        distance_cm = sensor_returns.distance_cm

                        if distance_cm > self.empty_range:
                            # Stop the pump
                            self.pump_off()
                            print("Pump disabled. FILL WATER TANK.")
                            logging.info("Pump STOPPED because distance is below or coming close to min level " + str(distance_cm))
                            break
                        time.sleep(0.001)
                else:
                    print("CHECKING WATER IN")

                # Wait for some time before checking again
                    time.sleep(1)
                    print("1...")
                    time.sleep(1)
                    print("2...")
                    time.sleep(1)
                    print("3...")
                    time.sleep(1)
                    print("4...")
                    time.sleep(1)
                    print("5...")
                    time.sleep(1)
                    print("6...")
                    time.sleep(1)
                    print("7...")
                    time.sleep(1)
                    print("8...")
                    time.sleep(1)
                    print("9...")
                    time.sleep(1)
                    print("10...")

class ClimateControl:
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
            # Fan speed should be 100%4
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
        print("We dont have a fan test yet bobby!")
        pass

    def set_fan_speed(self):
        global FAN_SPEED
        while True:
            # Prompt user for new fan speed
            new_fan_speed_str = input(USERNAMEID + " please enter new fan speed (0-100, or b to cancel): ")
            if new_fan_speed_str.lower() == "b":
                break
            try:
                new_fan_speed = float(new_fan_speed_str)
                if new_fan_speed < 0 or new_fan_speed > 100:
                    raise ValueError("Fan speed must be between 0 and 100")
                FAN_SPEED = new_fan_speed
                if FAN_SPEED == 0:
                    # Stop the fan
                    GPIO.output(self.fan_pwm_pin, GPIO.LOW)
                    print("Fan turned off")
                else:
                    # Set the fan speed
                    self.pwm.ChangeDutyCycle(FAN_SPEED)
                    print(f"Fan speed set to {new_fan_speed}%")
            except ValueError as e:
                print(f"Invalid fan speed: {e}")

    def fan_speed_test02(self):
        print("Fuck you jimmy")
        

    def fan_speed_test01(self):
        global FAN_SPEED
        while True:
            # Prompt user for new fan speed
            new_fan_speed_str = input(USERNAMEID + "Please any Key to Continue FAN Test 01 - or press b to cancel")
            if new_fan_speed_str.lower() == "b":
                break
            try:
                GPIO.output(self.fan_pwm_pin, GPIO.LOW)
                print("Fan at 0%")
                time.sleep(5)
                self.pwm.ChangeDutyCycle(20)
                print("Fan at 20%")
                time.sleep(5)
                self.pwm.ChangeDutyCycle(40)
                print("Fan at 40%")
                time.sleep(5)
                self.pwm.ChangeDutyCycle(60)
                print("Fan at 60%")
                time.sleep(5)
                self.pwm.ChangeDutyCycle(80)
                print("Fan at 80%")                    
                time.sleep(5)
                self.pwm.ChangeDutyCycle(100)
                print("Fan at 100%")
                time.sleep(5)
                print ("Fan Test 01 complete")
            except:
                print("Error occurred during fan speed test")
                break

    def set_climate_target_temperature(self):
        global TARGET_TEMP
        while True:
            try:
                # Prompt user for new target temperature
                print("The Current TARGET Temp is set at:",TARGET_TEMP,)
                new_target_temp = input(USERNAMEID + " please enter the target temperature for your growbox (in Celsius): ")
                TARGET_TEMP = float(new_target_temp)
                print(f"Target temperature set to {TARGET_TEMP} C")
                break
            except ValueError as e:
                print(f"Invalid temperature: {e}")
                break
            except KeyboardInterrupt:
                print("\nClimate control setup cancelled by user")
                break

    def run(self):
        # Run climate control loop
        while True:
            # Update fan speed based on temperature
            self.update_fan_speed()

            # Check if temperature is within target range
            temperature = self.sensor_returns.temperature
            if temperature >= TARGET_TEMP:
                logging.info("AC-OFF%")
                # Turn off AC or other cooling devices
            else:
                logging.info("AC-MAX%")
                # Turn on AC or other cooling devices

            # Sleep for some period of time before updating again
            time.sleep(10)



class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def get_value(self, section, key):
        return self.config.get(section, key)

    def set_value(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

        with open(self.config_file, 'w') as f:
            self.config.write(f)

#############
#SYSTEM MENU#
#############

class Menu:
    def __init__(self):
        self.stop = False

    def print_main_menu(self):
        print("   +++ HiPi Backend Menu +++")
        print("   =========================")
        print("0. Initiate HiPi Growbox")
        print("1. Print Current Sensor Data")
        print("2. Sensor Setup")
        print("3. Climate Control Setup")
        print("4. Watering System Setup")
        print("5. General")
        climate_target_temp = config_manager.get_value('ClimateControl', 'climate_target_temp')
        print(climate_target_temp)

    def print_sensor_returns_menu(self):
        print("1. [DEBUG] Turn Sensor Returns On")
        print("2. [DEBUG] Turn Sensor Returns Off")
        print("b. Back")

    def print_climate_setup_menu(self):
        print("1. Set Climate Target Temperature")
        print("2. [DEBUG] Run Fan Speed Test")
        print("3. [DEBUG] Fan Control")
        print("b. Back")

    def print_fan_control_menu(self):
        print("1. [DEBUG] Set Speed 1-100")
        print("b. Back")
        
    def print_watering_system_menu(self):
        print("1. Turn On Pump")
        print("2. Turn Off Pump")
        print("3. Run Pump Test")
        print("b. Back")

    def print_general_menu(self):
        print("1. Update Username")
        print("2. Update Device Name")
        print("b. Back")

    def run(self):
        while not self.stop:
            self.print_main_menu()
            choice = input("Enter choice: ")
            if choice == "0":
                while True:
                        print("Invalid choice")       
                break 
            
            elif choice == "1":
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
                        climate_control.set_climate_target_temperature()
                        break
                    elif climate_setup_choice == "2":
                        # Run fan speed test
                        break
                    elif climate_setup_choice == "3":
                        while True:
                            self.print_fan_control_menu()
                            fan_control_choice = input("Enter choice: ")
                            if fan_control_choice == "1":
                                climate_control.set_fan_speed()
                                break
                            elif fan_control_choice == "2":
                                climate_control.fan_speed_test02()
                                break
                            elif fan_control_choice.lower() == "b":
                                break
                            else:
                                print("Invalid choice")
                    elif climate_setup_choice.lower() == "b":
                        break
            elif choice == "4":
                while True:
                    self.print_watering_system_menu()
                    watering_system_choice = input("Enter choice: ")
                    if watering_system_choice == "1":
                        watering_system.pump_on()
                        break
                    elif watering_system_choice == "2":
                        watering_system.pump_off()
                        break
                    elif watering_system_choice == "3":
                        watering_system.test_pump()
                        break
                    elif watering_system_choice.lower() == "b":
                        break
                    else:
                        print("Invalid choice") 
                              
            elif choice == "5":
                while True:
                    self.print_general_menu()
                    general_choice = input("Enter choice: ")
                    if general_choice == "1":
                        # Update username
                        break
                    elif general_choice == "2":
                        # Update device name
                        break
                    elif general_choice.lower() == "b":
                        break
                    else:
                        print("Invalid choice")



if __name__ == '__main__':
    #Start Persistant Config Manager Class
    config_manager = ConfigManager('config.ini')

    # Start the sensor thread Class
    sensor_thread.start()

    # Initiate Climate Control Class
    climate_control = ClimateControl(FAN_PWM_PIN, sensor_returns)

    # Create Watering System Instance Class
    watering_system = WateringSystem(RELAY_WATERPUMP)
    watering_system.pump_off()

    # Create Menu instance Class
    menu = Menu()
    menu.run()

    # Cleanup GPIO
    GPIO.cleanup()

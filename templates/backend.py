# Include Libraries
import time
import RPi.GPIO as GPIO
import configparser
import Adafruit_DHT
import threading

# Define Friendly Sensor Names
DHT22_SENSOR = Adafruit_DHT.DHT22

#Define Global Varibles
TEMP_INT = 0
HUM_INT = 0

distance = 0
WATER_MAX = None
WATER_MIN = None

##### GPIO PINS

TRIGGER_PIN = 6 # Trigger for Ultrasonic Sensor
ECHO_PIN = 5 # Echo for Ultrasonic Sensor
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16
DHT22_PIN = 17
RELAY_WATERPUMP = 26

###### GPIO SETUP MODE
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

###### GPIO SETUP
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)
GPIO.setup(DHT22_PIN, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(RELAY_WATERPUMP, GPIO.OUT)


#######FAN CONFIG AND PID PERIMITERS
# Set PWM frequency
pwm = GPIO.PWM(FAN_PWM_PIN, 1000)
pwm.start(0)

# Get current fan speed
def get_fan_speed():
    t = time.time()
    count = 0
    while (time.time() - t) < 1:
        if GPIO.input(FAN_SPEED_PIN):
            count += 1
    return count * 60

# Set fan speed
def set_fan_speed(speed):
    duty_cycle = speed / 100.0 * 100
    pwm.ChangeDutyCycle(duty_cycle)

# PID constants
Kp = 100
Ki = 0.01
Kd = 0.01

# PID variables
integral = 0
prev_error = 0
temp_counter = 0

# Define a function to read data from the ultrasonic sensor
def ultrasonic_reader():
    global distance
    while True:
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
        distance_cm = pulse_duration * 17150

        # Update the global distance variable
        distance = round(distance_cm, 2)

        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.05)


# Define a function to read data from the DHT22 sensor
def dht22_reader():
    global HUM_INT, TEMP_INT
    while True:
        # Read the temperature and humidity from the sensor
        HUM_INT, TEMP_INT, = Adafruit_DHT.read_retry(DHT22_SENSOR, DHT22_PIN)

        # If the temperature or humidity is None, set it to 0
        if TEMP_INT is None:
            TEMP_INT = 0
        if HUM_INT is None:
            HUM_INT = 0

        # Round the temperature and humidity to one decimal place
        TEMP_INT = round(TEMP_INT, 1)
        HUM_INT = round(HUM_INT, 1)

        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.1)


# Define a function to run the main loop
def main_loop():
    global distance, TEMP_INT, HUM_INT
    while True:
        print("Main loop running.")
        ultrasonic_reader()
        print(f"Distance: {distance}")
        dht22_reader()
        print(f"Temperature: {TEMP_INT}, Humidity: {HUM_INT}")
        time.sleep(1)

if __name__ == '__main__':
    # Start the ultrasonic reader thread
    ultrasonic_thread = threading.Thread(target=ultrasonic_reader)
    ultrasonic_thread.daemon = True
    ultrasonic_thread.start()

    # Start the DHT22 reader thread
    dht22_thread = threading.Thread(target=dht22_reader)
    dht22_thread.daemon = True
    dht22_thread.start()

    # Start the main loop in a new thread
    main_thread = threading.Thread(target=main_loop)
    main_thread.daemon = True
    main_thread.start()

    ultrasonic_thread.join()
    dht22_thread.join()
    main_thread.join()

    # Cleanup GPIO
    GPIO.cleanup()

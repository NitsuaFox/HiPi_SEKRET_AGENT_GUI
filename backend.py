# Include Libraries
import time
import RPi.GPIO as GPIO
import configparser
import Adafruit_DHT
import threading

#Global Variables
TEMP_INT = 0 
HUM_INT = 0

# Define Friendly Sensor Names
DHT22_SENSOR = Adafruit_DHT.DHT22

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

# FAN CONFIG AND PID PERIMITERS
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


# DHT22 Temp and Humiditiy Sensor (Threaded)

def dht22_reader():
    global TEMP_INT, HUM_INT
    while True:
        # Read the temperature and humidity from the sensor
        HUM1, TEMP1, = Adafruit_DHT.read_retry(DHT22_SENSOR, DHT22_PIN)
        TEMP_INT = round(TEMP1, 2)
        HUM_INT = round(HUM1, 2)
        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.5)

#Ultrasonic Sensor for Water Level. (Threaded)

def get_distance():
    global distance_cm
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
        distance_cm = round(pulse_duration * 17150, 2)

        # Sleep for a short time to avoid spamming the sensor
        time.sleep(0.05)

# Main Backend Loop - Currently Pushing out Sensor Information to User.
def main_loop():
    global distance_cm, HUM_INT, TEMP_INT
    while True:
        print("Water Distance" ,distance_cm,"cm")
        print("Int. Humidity:" ,HUM_INT,"%")
        print("Int Temp:" ,TEMP_INT,"c" )
        time.sleep(0.5)

#Threads are defined here.

if __name__ == '__main__':
    # Start the ultrasonic reader thread
    ultrasonic_thread = threading.Thread(target=get_distance)
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

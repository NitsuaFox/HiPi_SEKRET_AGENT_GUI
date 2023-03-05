import time
import RPi.GPIO as GPIO 

GPIO.setmode(GPIO.BCM)


TRIGGER_PIN = 6
ECHO_PIN = 5

# Set water level parameters
WATER_MAX = 25  # maximum water level in centimeters
WATER_MIN = 15  # minimum water level in centimeters

GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
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

    # Return the distance
    return distance_cm



def set_water_max(max_level):
    global WATER_MAX
    WATER_MAX = max_level

def set_water_min(min_level):
    global WATER_MIN
    WATER_MIN = min_level

def read_water_level():
    distance = get_distance()
    if distance < WATER_MIN:
        return "Water Is GOOD"
    elif distance > WATER_MAX:
        return "Water Needs Adding NOW"
    else:
        return "Water Is Running Out"

while True:
    water_level = read_water_level()
    print("Water level: {}".format(water_level))
    time.sleep(1)
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

        return distance_cm

while True:
    distance_cm = get_distance()
    # Print the distance in centimeters
    print("Distance:", distance_cm, "cm")
    time.sleep(0.5)
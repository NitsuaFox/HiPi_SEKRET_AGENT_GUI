import time
import RPi.GPIO as GPIO 

TRIGGER_PIN = 5
ECHO_PIN = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    print("1")
    # Send a 10us pulse to the trigger pin to start the measurement
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)
    print("2")
    # Wait for the pulse to be returned
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    print("3")
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    print("Pulse Duration:", pulse_duration)  # Debugging print statement

    # Calculate the distance in centimeters
    distance_cm = round(pulse_duration * 17150, 2)
    return distance_cm

try:
    while True:
        distance_cm = get_distance()
        # Print the distance in centimeters
        print("Distance:", distance_cm, "cm")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Measurement stopped by the user")
    GPIO.cleanup()

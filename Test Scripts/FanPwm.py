import RPi.GPIO as GPIO
import time

# Pin constants
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)

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

try:
    while True:
        # Read fan speed
        fan_speed = get_fan_speed()

        # Get user input for fan speed
        speed = input("Enter fan speed (0-100): ")
        speed = int(speed)

        # Set fan speed
        set_fan_speed(speed)

        # Print fan speed
        print(f"Fan speed set to {speed}%")
        print(f"Current fan speed: {fan_speed} RPM")

except KeyboardInterrupt:
    # Clean up GPIO
    GPIO.cleanup()

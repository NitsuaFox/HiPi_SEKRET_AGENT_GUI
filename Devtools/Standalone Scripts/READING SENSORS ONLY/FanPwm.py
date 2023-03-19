import RPi.GPIO as GPIO
import time

# Set up GPIO pins
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
pwm = GPIO.PWM(FAN_PWM_PIN, 500)

# Set initial PWM speed
pwm.start(0)

try:
    while True:
        # Read raw data from speed pin
        speed = GPIO.input(FAN_SPEED_PIN)
        print(f"Speed: {speed}")

        # Set PWM duty cycle from user input and speed reading
        duty_cycle = int(input("Enter duty cycle (0-100): "))
        if duty_cycle == 0:
            pwm.stop()
        else:
            pwm.ChangeDutyCycle(duty_cycle)

except KeyboardInterrupt:
    pass

finally:
    # Clean up GPIO pins
    pwm.stop()
    GPIO.cleanup()

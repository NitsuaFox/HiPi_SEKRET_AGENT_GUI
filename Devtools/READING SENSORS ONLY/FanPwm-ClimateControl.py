import RPi.GPIO as GPIO
import time
import Adafruit_DHT

Sensor_DHT22 = Adafruit_DHT.DHT22

# Pin constants
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16
DHT22_PIN = 17

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)
GPIO.setup(DHT22_PIN, GPIO.IN, GPIO.PUD_DOWN)

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
    # Get target temperature and variance
    set_temp = float(input("Enter target temperature: "))
    temp_variance = float(input("Enter temperature variance: "))
    temp_range = float(input("Enter temperature range: "))
    print(f"Entered: target temperature {set_temp}°C, variance {temp_variance}°C, range {temp_range}°C")

    while True:
        # Read current temperature
        humidity, temp = Adafruit_DHT.read_retry(Sensor_DHT22, DHT22_PIN)

        # Calculate temperature difference
        temp_diff = temp - set_temp

        # Set fan speed based on temperature difference
        if temp_diff <= 0:
            set_fan_speed(0)
            print("Fan speed set to 0% (temperature below target)")
        elif temp_diff < temp_variance:
            set_fan_speed(50)
            print(f"Fan speed set to 50% (temperature difference: {temp_diff})")
        elif temp_diff > temp_range:
            set_fan_speed(100)
            print(f"Fan speed set to 100% (temperature difference: {temp_diff})")
        else:
            fan_speed = 50 + (temp_diff - temp_variance) / (temp_range - temp_variance) * 50
            set_fan_speed(fan_speed)
            print(f"Fan speed set to {fan_speed}% (temperature difference: {temp_diff})")

        # Print current temperature
        print(f"Current temperature: {temp:.2f}°C")

        # Wait 1 second before updating again
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO
    GPIO.cleanup()

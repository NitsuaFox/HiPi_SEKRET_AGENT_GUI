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

# PID constants
Kp = 100
Ki = 0.01
Kd = 0.01

# PID variables
integral = 0
prev_error = 0
temp_counter = 0

try:
    # Get target temperature
    set_temp = float(input("Enter target temperature: "))
    print(f"Entered: {set_temp}%")

    while True:
        # Read current temperature
        humidity, temp = Adafruit_DHT.read_retry(Sensor_DHT22, DHT22_PIN)

        # Calculate error
        error = set_temp - temp

        # Calculate integral and derivative terms
        integral = integral + error
        derivative = error - prev_error

        # Calculate PID output
        pid_output = Kp * error + Ki * integral + Kd * derivative

        # Limit PID output to between 0 and 100
        pid_output = max(0, min(100, pid_output))

        # Set fan speed based on temperature difference
        temp_diff = temp - set_temp
        if temp_diff <= 0:
            set_fan_speed(0)
            print("Fan speed set to 0% (temperature below target)")
            temp_counter = 0
        elif temp_diff > 2:
            set_fan_speed(100)
            print("Fan speed set to 100% (temperature too high)")
            temp_counter = 0
        else:
            if temp_counter >= 5:
                set_fan_speed(pid_output + 20)
                print(f"Fan speed increased to {pid_output+20}% (temperature not decreasing)")
            else:
                set_fan_speed(pid_output)
                print(f"Fan speed set to {pid_output}%")
            temp_counter += 1

        # Print current temperature
        print(f"Current temperature: {temp:.2f}°C")

        # Update previous error
        prev_error = error

        # Wait 1 second before updating again
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO
    GPIO.cleanup()

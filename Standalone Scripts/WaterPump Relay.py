import RPi.GPIO as GPIO
import time

RELAY_PIN1 = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN1, GPIO.OUT)

def turn_pump_on():
    GPIO.output(RELAY_PIN1, GPIO.HIGH)

def turn_pump_off():
    GPIO.output(RELAY_PIN1, GPIO.LOW)

try:
    while True:
        choice = input("Enter 1 to turn the pump on, 0 to turn it off, or q to quit: ")
        if choice == '1':
            turn_pump_on()
            print("Pump turned on")
        elif choice == '0':
            turn_pump_off()
            print("Pump turned off")
        elif choice == 'q':
            break
        else:
            print("Invalid input, try again.")
        time.sleep(1)

finally:
    GPIO.cleanup()

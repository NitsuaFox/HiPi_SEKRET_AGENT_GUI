#HiPi V0.1 | sensor magic for HiPi via Python and sensors, We then pass that data to HTML/JavaScript to produce the SecretAgent Frontend

#Include Libraries
from flask import Flask, render_template, jsonify, request
import time
import RPi.GPIO as GPIO
import configparser
import Adafruit_DHT
import threading

#Define Friendly Sensor Names
DHT22_SENSOR = Adafruit_DHT.DHT22

#Define Data Variables
TEMP_INT = 50 
HUM_INT = 0
WATER_MAX = None
WATER_MIN = None

################################################### GPIO PINS <
#GPIOS ULTRASONIC
TRIGGER_PIN = 6 # Trigger for Ultrasonic Sensor
ECHO_PIN = 5 # Echo for Ultrasonic Sensor

#GPIOS FAN1
FAN_PWM_PIN = 12
FAN_SPEED_PIN = 16

#GPIOS DHT22
DHT22_PIN = 17

#GPIOS 5V RELAY (4 CHANNEL)
RELAY_WATERPUMP = 26


################################################### GPIO PINS >

################################################### GPIO SETUP <
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)
GPIO.setup(FAN_SPEED_PIN, GPIO.IN)
GPIO.setup(DHT22_PIN, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(RELAY_WATERPUMP, GPIO.OUT)

################################################### GPIO SETUP >

############################################## FAN CONFIG <
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

############################################## FAN CONFIG >
FLASK_PORT = 8080
################################################### FLASK GLOBAL CONFIG <
# Start Web Server Flask APP.
app = Flask(__name__)

#Loads Config.ini I think
@app.before_first_request
def load_config():
    global config
    config = configparser.ConfigParser()
    try:
        config.read('/home/pi/Python/config.ini')
    except Exception as e:
        print(f"Error reading config.ini file: {e}")
        config = None
    if config:
        global WATER_MAX
        WATER_MAX = int(config['water_level']['max'])
        global WATER_MIN
        WATER_MIN = int(config['water_level']['min'])
    else:
        WATER_MAX = None
        WATER_MIN = None
################################################### FLASK GLOBAL CONFIG >

################################################### DHT22 SENSOR FUNC <
def Get_DHT22_Data():
    global TEMP_INT, HUM_INT
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN)
    if humidity is not None and temperature is not None:
        TEMP_INT = round(temperature, 1)
        HUM_INT = round(humidity, 1)

################################################## DHT22 SENSOR FUNC >

################################################### ULTRASONIC SENSOR FUNC <
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

def read_water_level():
    distance = get_distance()
    if distance < WATER_MIN:
        return "WATER MAX"
    elif distance > WATER_MAX:
        return "WATER MIN - PUMP LOCKED"
    else:
        percent = ((distance - WATER_MIN) / (WATER_MAX - WATER_MIN)) * 100
        percent = round(percent)
        return f"{percent}%"


################################################### ULTRASONIC SENSOR >


################################################### WATERING SYSTEM functions <

def pump_fail_safe(distance, WATER_MAX, WATER_MIN):
    # Check if the water level is too low
    if distance > WATER_MAX:
        GPIO.output(RELAY_WATERPUMP, GPIO.HIGH)
        print("Water level is too low, turning off pump.")
    # Check if the water level is normal
    elif distance > WATER_MIN:
        GPIO.output(RELAY_WATERPUMP, GPIO.LOW)
        print("Water level is too low, turning  on pump.")
    else:
        GPIO.output(RELAY_WATERPUMP, GPIO.HIGH)
        print("Water level is too high, turning off pump.")



################################################### WATERING SYSTEM functions >

################################################### FLASK STUFF <
@app.route('/')
def home():
    return render_template('home.html', config=config)


@app.route('/water_config')
def water_config():
    return render_template('water-config.html', config=config)

#This is where we send the variables and sensor data for the JAVASCRIPT
@app.route('/data')
def get_data():
    Get_DHT22_Data()  # Update the temperature and humidity variables
    distance = get_distance()
    return jsonify({
        'water_level': read_water_level(),
        'distance': round(distance, 2),
        'max_level': WATER_MAX,
        'min_level': WATER_MIN,
        'temp_int': TEMP_INT,
        'hum_int': HUM_INT,
    })

#This the update-config we run on a submit button, it writes back to the config.ini
#this is so we are able to have persistant data for the grow box.
@app.route('/update-config', methods=['POST'])
def update_config():
    global WATER_MAX, WATER_MIN
    
    max_level = request.form['max-level']
    min_level = request.form['min-level']

    # update the values in the object
    config.set('water_level', 'max', str(max_level))
    config.set('water_level', 'min', str(min_level))
    
    WATER_MAX = int(max_level)
    WATER_MIN = int(min_level)

    # write the changes to the file
    with open('/home/pi/Python/config.ini', 'w') as configfile:
        config.write(configfile)

    # print the updated values for debugging
    print(f"New max_level: {config['water_level']['max']}")
    print(f"New min_level: {config['water_level']['min']}")

    return 'Config updated successfully'

# Define a function to run the main loop
def main_loop():
    while True:
        print("Main loop running.")
        Get_DHT22_Data()  # Update the temperature and humidity variables
        distance = get_distance()
        #if WATER_MAX is not None and WATER_MIN is not None:
        #    pump_fail_safe(distance, WATER_MAX, WATER_MIN)
        #time.sleep(0.1)

if __name__ == '__main__':
    # Start the main loop in a new thread
    main_thread = threading.Thread(target=main_loop)
    main_thread.daemon = True
    main_thread.start()

    ultrasonic_thread = threading.Thread(target=get_distance)
    ultrasonic_thread.daemon = True
    ultrasonic_thread.start()

    pump_thread = threading.Thread(target=pump_fail_safe)
    pump_thread.daemon = True
    pump_thread.start()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=str(FLASK_PORT))
    print('Flask app is running.')

    # Wait for threads to finish
    ultrasonic_thread.join()
    pump_fail_safe.join()
    
    # Cleanup GPIO
    GPIO.cleanup()
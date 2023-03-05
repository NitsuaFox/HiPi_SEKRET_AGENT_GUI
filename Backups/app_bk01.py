# HiPi V0.1 | Provides Controls for HiPi via Python and sensors, We then pass that data to HTML/JavaScript to produce the SecretAgent Frontend

from flask import Flask, render_template, jsonify, request
import time
import RPi.GPIO as GPIO
import configparser

GPIO.setmode(GPIO.BCM)

TRIGGER_PIN = 6
ECHO_PIN = 5

app = Flask(__name__)

@app.before_first_request
def load_config():
    global config
    config = configparser.ConfigParser()
    config.read('/home/pi/Python/config.ini')
    global WATER_MAX
    WATER_MAX = int(config['water_level']['max'])
    global WATER_MIN
    WATER_MIN = int(config['water_level']['min'])

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


@app.route('/')
def home():
    return render_template('home.html', config=config)


@app.route('/data')
def get_data():
    distance = get_distance()
    return jsonify({
        'water_level': read_water_level(),
        'distance': distance
    })


@app.route('/update-config', methods=['POST'])
def update_config():
    max_level = request.form['max-level']
    min_level = request.form['min-level']

    # create a new ConfigParser object
    config = configparser.ConfigParser()
    config.read('/home/pi/Python/config.ini')

    # update the values in the object
    config.set('water_level', 'max', str(max_level))
    config.set('water_level', 'min', str(min_level))

    # write the changes to the file
    path_to_config = '/home/pi/Python/config.ini' # path to the config file
    print(f"Writing to file: {path_to_config}")  # add this line
    with open(path_to_config, 'w') as configfile:
        config.write(configfile)

    # print the updated values for debugging
    print(f"New max_level: {config['water_level']['max']}")
    print(f"New min_level: {config['water_level']['min']}")

    return 'Config updated successfully'





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4400)
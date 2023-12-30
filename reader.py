import serial 

def init_arduino(port):
    # Initialize the Arduino connection
    # The baud rate should match the rate set in your Arduino program
    arduino = serial.Serial(port, 9600, timeout=1)
    print('Arduino initialized', arduino)
    return arduino

def read_sensor_data(arduino):
    sensor_values = {'electrode': None, 'light': None, 'soil': None, 'temperature': None, 'humidity': None}
    while None in sensor_values.values():
        data = arduino.readline().decode('utf-8').strip()
        for line in data.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                if key.strip() in sensor_values:
                    sensor_values[key.strip()] = int(float(value.strip()))
    return sensor_values
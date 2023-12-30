from pyo import *
import time
import random
import threading
import reader as asr

s = Server().boot()
s.amp = 0.1

global counter
counter = 0
arduino = asr.init_arduino('/dev/cu.usbmodem1301')


def read_value():
    sensor_data = asr.read_sensor_data(arduino)
    return sensor_data['electrode']

last_value = 100

# Create a PyoObject for frequency that you can update
freq_obj = Sig(value=100)

def read_value_thread():
    global last_value
    global counter
    counter += 1
    while True:
        current_value = read_value()
        if current_value != last_value and counter % 3 == 0:
            last_value = current_value
        else:
            current_value = current_value + random.randint(-2, 2)

        # Update the freq_obj's value to change the frequency of the sine waves
        freq_obj.setValue(current_value)
        print(f"ADC Value: {current_value}")

        time.sleep(0.33)

env = Adsr(attack=0.01, decay=0.2, sustain=0.5, release=0.5, mul=0.5).play()

def check_freq_change():
    diff = abs(freq_obj.get() - last_value)
    if diff > threshold:
        env.play()

# Use a Metro to regularly check the difference
threshold = 10
metro = Metro(time=0.1).play()
trig_func = TrigFunc(metro, function=check_freq_change)


# Sine waves and harmonizers with various sound variations
h1 = Sine(freq=freq_obj, mul=env).out()
h2 = Sine(freq=freq_obj * 3, phase=0.5, mul=1.0 / pow(3, 2) * env).out()
h3 = Sine(freq=freq_obj * 5, mul=1.0 / pow(5, 2) * env).out()

# Adding more harmonics for richness
h4 = Sine(freq=freq_obj * 7, phase=0.5, mul=1.0 / pow(7, 2) * env).out()
h5 = Sine(freq=freq_obj * 9, mul=1.0 / pow(9, 2) * env).out()
h6 = Sine(freq=freq_obj * 11, phase=0.5, mul=1.0 / pow(11, 2) * env).out()
h7 = Sine(freq=freq_obj * 13, mul=1.0 / pow(13, 2) * env).out()

# More melodic harmonizers
harmonizer1 = Harmonizer(h1, transpo=5).out()  # Perfect fourth
harmonizer2 = Harmonizer(h1, transpo=7).out()  # Perfect fifth

harmonizer2 = Harmonizer(h3, transpo=5).out()  # Perfect fourth
harmonizer3 = Harmonizer(h3, transpo=7).out()  # Perfect fifth

harmonizer4 = Harmonizer(h5, transpo=5).out()  # Perfect fourth
harmonizer5 = Harmonizer(h5, transpo=7).out()  # Perfect fifth

# Some FM synthesis for additional timbral variation
fm = FM(carrier=freq_obj, ratio=[.2498,.2503], index=10, mul=env).out()

# Displays the final waveform
sp = Scope(h1 + h2 + h3 + h4 + h5 + h6 + h7 + harmonizer1 + harmonizer2 + harmonizer3 + harmonizer4 + harmonizer5 + fm)


thread = threading.Thread(target=read_value_thread)
thread.start()

s.gui(locals())
from pyo import *
import time
import random
import threading

s = Server().boot()
s.amp = 0.1

def read_value():
    with open("value.txt", "r") as file:
        return int(file.read().strip())

last_value = 100
last_significant_change_time = time.time()

# Create a PyoObject for frequency that you can update
freq_obj = Sig(value=100)
mul_obj = Sig(0.5)

# Major scale frequencies (C4 to C5)
scale_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

def map_adc_to_scale(adc_value):
    index = int((adc_value - 100) / 100)  # Assuming adc_value ranges from 100 to 900
    index = min(max(index, 0), len(scale_frequencies) - 1)
    return scale_frequencies[index]

def read_value_thread():
    global last_value
    global last_significant_change_time
    while True:
        current_value = read_value()
        # TO REMOVE
        current_value = current_value + random.randint(-2, 2)
        last_value = freq_obj.get()


        mapped_value = map_adc_to_scale(current_value)

        # Update the freq_obj's value to change the frequency of the sine waves
        freq_obj.setValue(mapped_value)
        print(f"ADC Value: {current_value}, Mapped Frequency: {mapped_value}")

        time.sleep(0.33)

threshold = 25
# env = Adsr(attack=0.01, decay=0.2, sustain=0.5, release=0.5, mul=mul_obj).play()
env = Adsr(attack=0.25, decay=0.2, sustain=0.1, release=0.2, mul=mul_obj).play()


def check_freq_change():
    global last_significant_change_time
    diff = abs(freq_obj.get() - last_value)
    if diff > threshold:
        mul_obj.setValue(0.5)
        env.play()
        last_significant_change_time = time.time()
    elif time.time() - last_significant_change_time > 3:  # 3 seconds without significant change
        current_mul = mul_obj.value
        mul_obj.setValue(current_mul * 0.9)  # Decrease the amplitude by 10% every check


# Use a Metro to regularly check the difference
metro = Metro(time=0.1).play()
trig_func = TrigFunc(metro, function=check_freq_change)

h1 = Sine(freq=scale_frequencies, mul=env)

# Harmonizers with some melodic variation
harmonizer1 = Harmonizer(h1, transpo=5) # Perfect fourth
harmonizer2 = Harmonizer(h1, transpo=7)  # Perfect fifth

# Apply a chorus for a spacious sound
# chorus = Chorus(harmonizer1 + harmonizer2, depth=0.5, feedback=0.1, bal=0.5)

# Use a larger reverb for an ethereal feel
reverb = Freeverb(harmonizer1 + harmonizer2, size=0.9, damp=0.2, bal=0.5)

# A delay for cascading echoes
delay = Delay(reverb, delay=0.5, feedback=0.5, maxdelay=2).out()

# Apply a slow-moving low-pass filter for a sweeping effect
lfo = Sine(freq=0.1).range(250, 5000)
lpf = ButLP(delay, freq=lfo).out()

# Displays the final waveform
sp = Scope(lpf)


thread = threading.Thread(target=read_value_thread)
thread.start()

s.gui(locals())

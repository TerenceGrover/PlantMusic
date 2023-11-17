from pyo import *
import time
import random
import threading

# SERVER AND GLOBAL VARIABLES
s = Server().boot()
s.amp = 0.1
chorus_depth_melo = 0.2
chorus_depth_harmo = 0.7
reverb_size_melo = 0.2
reverb_size_harmo = 0.7
feedback = Sine(0.1, 0, 0.5, 0.5)
last_value = 100
last_significant_change_time = time.time()
melody_freq = Sig(value=100)
harmony_freq = Sig(value=100)
mul_obj = Sig(0.6)
major_scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
minor_scale = [261.63, 293.66, 311.13, 349.23, 392.00, 415.30, 466.16, 523.25]
threshold = 50
env = Adsr(attack=0.6, decay=0.2, sustain=0.3, release=0.5, mul=mul_obj).play()

# SENSOR READING FUNCTIONS


def read_value():
    with open("value.txt", "r") as file:
        return int(file.read().strip())


def read_light_sensor():
    # Replace with actual sensor reading logic
    return random.randint(90, 100)


def read_moisture_sensor():
    # Replace with actual sensor reading logic
    return random.randint(0, 100)


def read_temperature_sensor():
    # Replace with actual sensor reading logic
    return random.randint(0, 100)


def read_humidity_sensor():
    # Replace with actual sensor reading logic
    return random.randint(0, 100)

# MAPPING FUNCTIONS
def shift_octave(frequency, octave_change):
    return frequency * (2 ** octave_change)


def get_scale(light_value):
    return minor_scale if light_value < 50 else major_scale


def map_adc_to_scale(adc_value, scale):
    index = int((adc_value - 100) / 100)
    index = min(max(index, 0), len(scale) - 1)
    return scale[index]


def map_value(input_value, input_min, input_max, output_min, output_max):
    # Linear mapping from input range to output range
    return (input_value - input_min) / (input_max - input_min) * (output_max - output_min) + output_min


# MAIN THREAD
def read_value_thread():
    global last_value
    global last_significant_change_time
    global chorus_depth_melo
    global chorus_depth_harmo
    global reverb_size_melo
    global reverb_size_harmo
    light_value = read_light_sensor()
    scale = get_scale(light_value)
    counter = 0

    while True:
        current_value = read_value()
        # TO REMOVE
        current_value = current_value + random.randint(-2, 2)
        last_value = harmony_freq.get()

        if counter % random.randint(5, 10) == 0:
            mapped_value = map_adc_to_scale(current_value, scale)
        else:
            mapped_value = harmony_freq.get()

        # Update the freq_obj's value to change the frequency of the sine waves
        # Shift melody one octave higher
        melody_freq.setValue(shift_octave(mapped_value, 0))

        if counter % 25 == 0:
            harmony_freq.setValue(shift_octave(mapped_value, -1))

        chorus_depth_harmo = map_value(harmony_freq, 100, 900, 0.4, 1)
        chorus_depth_melo = map_value(melody_freq, 100, 900, 0.1, 0.6)
        reverb_size_harmo = map_value(harmony_freq, 100, 900, 0.6, 1)
        reverb_size_melo = map_value(melody_freq, 100, 900, 0.2, read_humidity_sensor()/100)
        print(f"ADC Value: {current_value}, Mapped Frequency: {mapped_value}")

        counter += 1

        time.sleep((current_value/1000) ** current_value /
                   light_value + random.uniform(0.05, 0.2))


# FREQ CHANGE FUNCTION
def check_freq_change():
    global last_significant_change_time
    diff = abs(harmony_freq.get() - last_value)
    if diff > threshold:
        mul_obj.setValue(0.9)
        env.play()
        last_significant_change_time = time.time()
    elif time.time() - last_significant_change_time > 3:  # 3 seconds without significant change
        current_mul = mul_obj.value
        # Decrease the amplitude by 10% every check
        mul_obj.setValue(current_mul * 0.9)


# MAIN LOGIC AND SYNTHESIS
# Use a Metro to regularly check the difference
metro = Metro(time=0.1).play()
trig_func = TrigFunc(metro, function=check_freq_change)
if read_humidity_sensor() < 50:
    melody_synth = SineLoop(freq=melody_freq, mul=env)
else:
    melody_synth = SuperSaw(freq=melody_freq, mul=env)
# Number of harmonics in the additive synthesizer
num_harmonics = 3

# Wave Creation
harmony_synth = [Sine(freq=harmony_freq * (i + 1), mul=env *
                      2/num_harmonics) for i in range(num_harmonics)]
additive_synth = sum(harmony_synth)

# EFFECTS
# A harmonizer to add a second voice
harmonizer_melo = Harmonizer(melody_synth, transpo=5)
harmonizer_harmo = Harmonizer(additive_synth)
# A chorus to fatten the overall sound
chorus_melo = Chorus(harmonizer_melo,
                     depth=chorus_depth_melo, bal=0.5)
chorus_harmo = Chorus(harmonizer_harmo,
                      depth=chorus_depth_harmo, bal=0.5)
# A reverb to add space
reverb_melo = Freeverb(chorus_melo, size=reverb_size_melo, damp=0.4, bal=0.5)
reverb_harmo = Freeverb(
    chorus_harmo, size=reverb_size_harmo, damp=0.2, bal=0.5)
# A delay for cascading echoes
delay_melo = SmoothDelay(reverb_melo, delay=0.5,
                         feedback=0.05, maxdelay=1).out()
delay_harmo = SmoothDelay(reverb_harmo, delay=0.6, feedback=0.3, maxdelay=2)
# A slow-moving low-pass filter for a sweeping effect
lfo = Sine(freq=0.2).range(1000, 5000)
lpf = ButLP(delay_harmo, freq=lfo).out()

# Display
sp = Scope(delay_melo + delay_harmo)

# THREAD START
thread = threading.Thread(target=read_value_thread)
thread.start()

# GUI
s.gui(locals())

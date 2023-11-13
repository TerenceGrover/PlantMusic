from pyo import *
import time
import random
import threading

s = Server().boot()
s.amp = 0.1
chorus_depth_melo = 0.2
chorus_depth_harmo = 0.7
reverb_size_melo = 0.2
reverb_size_harmo = 0.7
feedback = Sine(0.1, 0, 0.5, 0.5)


def read_value():
    with open("value.txt", "r") as file:
        return int(file.read().strip())


last_value = 100
last_significant_change_time = time.time()

# Create a PyoObject for frequency that you can update
melody_freq = Sig(value=100)
harmony_freq = Sig(value=100)
mul_obj = Sig(0.5)



def shift_octave(frequency, octave_change):
    return frequency * (2 ** octave_change)


major_scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
minor_scale = [261.63, 293.66, 311.13, 349.23, 392.00, 415.30, 466.16, 523.25]


def get_scale(light_value):
    return minor_scale if light_value < 50 else major_scale


def map_adc_to_scale(adc_value, scale):
    index = int((adc_value - 100) / 100)
    index = min(max(index, 0), len(scale) - 1)
    return scale[index]


def simulate_light_sensor():
    return random.randint(0, 100)


def map_value(input_value, input_min, input_max, output_min, output_max):
    # Linear mapping from input range to output range
    return (input_value - input_min) / (input_max - input_min) * (output_max - output_min) + output_min


def read_value_thread():
    global last_value
    global last_significant_change_time
    global chorus_depth_melo
    global chorus_depth_harmo
    global reverb_size_melo
    global reverb_size_harmo
    light_value = simulate_light_sensor()
    scale = get_scale(light_value)
    counter = 0

    while True:
        current_value = read_value()
        # TO REMOVE
        current_value = current_value + random.randint(-2, 2)
        last_value = harmony_freq.get()

        if counter % 3 == 0:
            mapped_value = map_adc_to_scale(current_value, scale)
        else:
            mapped_value = harmony_freq.get()

        # Update the freq_obj's value to change the frequency of the sine waves
        # Shift melody one octave higher
        melody_freq.setValue(shift_octave(mapped_value, 1))

        if counter % 10 == 0:
            harmony_freq.setValue(shift_octave(mapped_value, -1))

        chorus_depth_harmo = map_value(harmony_freq, 100, 900, 0.4, 1)
        chorus_depth_melo = map_value(melody_freq, 100, 900, 0.1, 0.6)
        reverb_size_harmo = map_value(harmony_freq, 100, 900, 0.4, 1)
        reverb_size_melo = map_value(melody_freq, 100, 900, 0.2, 0.7)
        print(f"ADC Value: {current_value}, Mapped Frequency: {mapped_value}")

        counter+=1

        time.sleep(current_value/1000 + random.uniform(0.05, 0.2))


threshold = 25
# env = Adsr(attack=0.01, decay=0.2, sustain=0.5, release=0.5, mul=mul_obj).play()
env = Adsr(attack=0.6, decay=0.2, sustain=0.3, release=0.5, mul=mul_obj).play()


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


# Use a Metro to regularly check the difference
metro = Metro(time=0.1).play()
trig_func = TrigFunc(metro, function=check_freq_change)

melody_synth = SuperSaw(freq=melody_freq, mul=env)

# Number of harmonics in the additive synthesizer
num_harmonics = 3
# Create an array of sine waves as harmonics
harmony_synth = [Sine(freq=harmony_freq * (i + 1), mul=env*1.2/num_harmonics) for i in range(num_harmonics)]
# Sum the harmonics to create the additive synthesis sound
additive_synth = sum(harmony_synth)

# Harmonizers with some melodic variation
harmonizer_melo = Harmonizer(melody_synth, transpo=5)  # Perfect fourth
harmonizer_harmo = Harmonizer(additive_synth)  # Perfect fifth

# Apply a chorus for a spacious sound
chorus_melo = Chorus(harmonizer_melo,
                     depth=chorus_depth_melo, bal=0.5)
chorus_harmo = Chorus(harmonizer_harmo,
                      depth=chorus_depth_harmo, bal=0.5)

# Use a larger reverb for an ethereal feel
reverb_melo = Freeverb(chorus_melo, size=reverb_size_melo, damp=0.4, bal=0.5)
reverb_harmo = Freeverb(
    chorus_harmo, size=reverb_size_harmo, damp=0.2, bal=0.5)

# A delay for cascading echoes
delay_melo = Delay(reverb_melo, delay=0.5, feedback=0.05, maxdelay=1).out()
delay_harmo = Delay(reverb_harmo, delay=0.6, feedback=0.3, maxdelay=2)

# Apply a slow-moving low-pass filter for a sweeping effect
lfo = Sine(freq=0.2).range(1000, 5000)
lpf = ButLP(delay_harmo, freq=lfo).out()

# Displays the final waveform
sp = Scope(delay_melo + delay_harmo)


thread = threading.Thread(target=read_value_thread)
thread.start()

s.gui(locals())
from pyo import *

s = Server().boot()

# Creates a noise source
n = Noise()

# Creates an LFO oscillating +/- 500 around 1000 (filter's frequency)
lfo1 = Sine(freq=0.1, mul=500, add=1000)
# Creates an LFO oscillating between 2 and 8 (filter's Q)
lfo2 = Sine(freq=0.4).range(2, 8)
# Creates a dynamic bandpass filter applied to the noise source
bp1 = ButBP(n, freq=lfo1, q=lfo2).out()

# The LFO object provides more waveforms than just a sine wave

# Creates a ramp oscillating +/- 1000 around 12000 (filter's frequency)
lfo3 = LFO(freq=0.25, type=1, mul=1000, add=1200)
# Creates a square oscillating between 4 and 12 (filter's Q)
lfo4 = LFO(freq=4, type=2).range(4, 12)
# Creates a second dynamic bandpass filter applied to the noise source
bp2 = ButBP(n, freq=lfo3, q=lfo4).out(1)

# Creates a ramp oscillating +/- 1000 around 12000 (filter's frequency)
lfo5 = LFO(freq=0.75, type=1, mul=200, add=700)
# Creates a square oscillating between 4 and 12 (filter's Q)
lfo6 = LFO(freq=10, type=2).range(10, 24)
# Creates a second dynamic bandpass filter applied to the noise source
bp2 = ButBP(n, freq=lfo5, q=lfo6).out()

s.gui(locals())
from pyo import *
from random import random

s = Server().boot()
s.start()

# First sound - dynamic spectrum.
spktrm = Sine(freq=1000, phase=5, mul=1).out()


s.gui(locals())
from pyo import *

s = Server().boot()
s.start()
lfo = Sine(.25, 0, .2, .1)
a = SineLoop(freq=[400,500], feedback=lfo, mul=.2).out()

s.gui(locals())

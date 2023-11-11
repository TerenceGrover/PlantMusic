import wx
import serial
import threading
import random
from wx.lib.plot import PlotCanvas, PolyLine, PlotGraphics
import numpy as np

class SerialThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.running = True
        self.ser = serial.Serial('/dev/cu.usbmodem11301', 9600, timeout=1)
        self.data = np.zeros(100)

    def run(self):
        while self.running:
            try:
                value = int(self.ser.readline().decode('utf-8').strip())
                self.data = np.roll(self.data, -1)
                self.data[-1] = value
                wx.CallAfter(self.callback, self.data)
            except ValueError:
                pass
        self.ser.close()

    def stop(self):
        self.running = False

class GraphFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Plant Data Real-Time", size=(600, 400))
        self.plotCanvas = PlotCanvas(self)
        self.plotCanvas.ySpec = (0, 300)
        # yspec setter
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.thread = SerialThread(self.update_graph)
        self.thread.start()

    def update_graph(self, data):
        line = PolyLine([(i, data[i]) for i in range(len(data))], colour="green" , width=4)
        gc = PlotGraphics([line], "Plant Data", "Time", "Value")
        self.plotCanvas.Draw(gc)



    def on_close(self, event):
        self.thread.stop()
        self.thread.join()
        self.Destroy()

if __name__ == "__main__":
    app = wx.App()
    frame = GraphFrame()
    frame.Show(True)
    app.MainLoop()

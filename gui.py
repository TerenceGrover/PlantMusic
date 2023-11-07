# potentiometer_gui.py
#This is to be replaced by Arduino readings
import tkinter as tk
from tkinter import Scale, Button

def on_value_change(value):
    with open("value.txt", "w") as file:
        file.write(value)

root = tk.Tk()
root.title("Virtual Potentiometer")
root.geometry("500x500")

potentiometer = Scale(root, length=250, from_=0, to=1024, orient=tk.HORIZONTAL, command=on_value_change)
potentiometer.pack(pady=100, padx=100)
potentiometer.set(400)


button = Button(root, text="Simulate Touch", command=lambda: potentiometer.set(700))
buttonReset = Button(root, text="Reset", command=lambda: potentiometer.set(400))

button.pack()
buttonReset.pack()

root.mainloop()

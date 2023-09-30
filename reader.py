# value_reader.py
import time
import random

def read_value():
    with open("value.txt", "r") as file:
        return int(file.read().strip())

last_value = None

while True:
    current_value = read_value()
    if current_value != last_value:
        print(f"ADC Value: {current_value}")
        last_value = current_value
    else :
        prev = current_value + random.randint(-2, 2)
        print(f"ADC Value: {prev}")
    time.sleep(0.33)

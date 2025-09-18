from gpiozero import Device, Button, LED
from gpiozero.pins.rpigpio import RPiGPIOFactory
Device.pin_factory = RPiGPIOFactory()  # <— key line

import os
from signal import pause
import time


BUTTON_PIN = 26

print("Lo script è stato caricato")

button = Button(BUTTON_PIN, pull_up=True)
os.system('raspi-gpio set 18 op')




def turn_on_screen():
    os.system('raspi-gpio set 18 dh')
    os.system('raspi-gpio set 19 a5')
    print("Ho premuto il pulsante")
    time.sleep(0.3)

def turn_off_screen():
    os.system('raspi-gpio set 18 dl')
    os.system('raspi-gpio set 19 op')
    os.system('raspi-gpio set 19 dl')   
    print("Ho premuto il pulsante")
    time.sleep(0.3)


turn_on_screen()

screen_on = True
while (True):
    # If you are having and issue with the button doing the opposite of what you want
    # IE Turns on when it should be off, change this line to:
    # input = not GPIO.input(26)
    input = not button.is_pressed
    if input != screen_on:
        screen_on = input
        if screen_on:
            turn_on_screen()
        else:
            turn_off_screen()
    time.sleep(0.3)

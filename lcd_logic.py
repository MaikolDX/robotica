#!/usr/bin/env python

from time import sleep
from threading import Thread
from rpi_lcd import LCD

reading = True
message = ""
message2 = ""

lcd = LCD()

def display_distance():
    while reading:
        lcd.text(message, 1)
        lcd.text(message2, 2)
        sleep(0.25)

def update_message(new_message, new_message2):
    global message
    global message2
    message = new_message
    message2 = new_message2

def start_lcd_thread():
    global reading
    reading = True
    display = Thread(target=display_distance, daemon=True)
    display.start()

def stop_lcd_thread():
    global reading
    reading = False
    lcd.clear()
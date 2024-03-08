#!/usr/bin/env python

from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

lcd = LCD()

def safe_exit(signum, frame):
    exit(1)

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    lcd.text("Hola,", 1)
    lcd.text("Bienvenido!", 2)

    pause()

except KeyboardInterrupt:
    pass

finally:
    lcd.clear()
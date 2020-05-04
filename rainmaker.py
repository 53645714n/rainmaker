import logging
import datetime
from gpiozero import button, led

#logging
logging.basicConfig(rainmaker.log, level=debug, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO
A = button(22)
B = button(23)
C = button(24)
D = button(25)
RedButton = button (26)
GreenButton = button (27)
RedLed = led(16)
GreenLed = (17)

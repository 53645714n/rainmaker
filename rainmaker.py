import logging
import datetime
from gpiozero import Button, LED

#logging
logging.basicConfig('rainmaker.log', level=DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO
A = button(22)
B = button(23)
C = button(24)
D = button(25)
RedButton = button (26)
GreenButton = button (27)
RedLed = led(16)
GreenLed = (17)

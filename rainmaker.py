import logging
import datetime
from gpiozero import Button, LED

#logging
logging.basicConfig(filename='rainmaker.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO
A = Button(22)
B = Button(23)
C = Button(24)
D = Button(25)
RedButton = Button (26)
GreenButton = Button (27)
RedLed = LED(16)
GreenLed = LED(17)

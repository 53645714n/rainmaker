import logging
from datetime import datetime, timedelta
#from gpiozero import Button, LED
import RPi.GPIO as GPIO

#logging
logging.basicConfig(filename='rainmaker.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO
GPIO.setmode(GPIO.BCM)
A = 22
GPIO.setup(A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
B = 23
GPIO.setup(B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
C = 24
GPIO.setup(C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
D = 25
GPIO.setup(D, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
RedButton = 26
GPIO.setup(RedButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GreenButton = 27
GPIO.setup(GreenButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
RedLed = 16
GreenLed = 17
PumpRelais = 0
GPIO.setup(RedLed,GPIO.OUT)
GPIO.setup(GreenLed,GPIO.OUT)
GPIO.setup(PumpRelais,GPIO.OUT)

''' the magic '''
#Turns pump on
def pump_on():
	TimeOn = datetime.now()
	logging.info('Pump turned on at %s', TimeOn)
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
#		print(TimeOn)
		if GPIO.input(B):
			logging.info('Pump turned off')
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break
		elif datetime.now() > TimeOff:
			logging.info('Pump turned off by timer')
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break

def input():
	global TimeOff
	while True:
		if GPIO.input(A):
			pump_on()
		elif GPIO.input(C):
			TimeOff = datetime.now() + timedelta(seconds = 10)
			logging.info('TimeOff set at: %s', TimeOff)
			pump_on()
		elif GPIO.input(D):
			TimeOff = datetime.now() + timedelta(minutes = 60)
			logging.info('TimeOff set at: %s', TimeOff)
			pump_on()

input()

#		else:
#			break
#def input():
#	if GPIO.input(A)
#	pump_on()

#def input():
#
#if __name__ == "__main__":
#	try:
#		pump_on()
#		main_loop()
#	except RuntimeError as error:
#		print(error.args[0])
#	except KeyboardInterrupt:
#		print("\nExiting application\n")
#		# exit the applications
#		GPIO.cleanup()

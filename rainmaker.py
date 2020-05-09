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
	GPIO.output(GreenLed,GPIO.HIGH)
	TimeOn = datetime.now()
#	logging.info('Pump turned on at %s', TimeOn)
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
#		print(TimeOn)
		if GPIO.input(B):
			logging.debug('Input B')
			logging.info('Pump turned off remotely, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Pump turned off locally, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break

def pump_on_timer():
	GPIO.output(GreenLed,GPIO.HIGH)
	TimeOn = datetime.now()
#	logging.info('Pump turned on at %s', TimeOn)
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
#		print(TimeOn)
		if GPIO.input(B):
			logging.debug('Input B')
			logging.info('Timer interrupted remotely, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer interrupted locally, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break
		elif datetime.now() > TimeOff:
			logging.info('Pump turned off by timer, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			input()
			break

def input():
	global TimeOff
	while True:
		GPIO.output(GreenLed,GPIO.LOW)
		if GPIO.input(A):
			logging.debug('Input A')
			logging.info('Pump turned on remotely')
			pump_on()
		elif GPIO.input(C):
			logging.debug('Input C')
			TimeOff = datetime.now() + timedelta(seconds = 10)
			logging.info('Pump turned on remotely, timeOff set at: %s', TimeOff)
			pump_on_timer()
		elif GPIO.input(D):
			logging.debug('Input D')
			TimeOff = datetime.now() + timedelta(minutes = 60)
			logging.info('Pump turned on remotely, timeOff set at: %s', TimeOff)
			pump_on_timer()
		elif GPIO.input(GreenButton):
			logging.debug('Input GreenButton')
			logging.info('Pump turned on locally')
			pump_on()

#input()

if __name__ == "__main__":
	try:
		input()
	except RuntimeError as error:
		print(error.args[0])
	except KeyboardInterrupt:
		print("\nExiting application\n")
		# exit the applications
		GPIO.cleanup()

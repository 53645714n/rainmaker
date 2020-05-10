import logging
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import threading
import time

#logging, logs all events to the file rainmaker.log
logging.basicConfig(filename='rainmaker.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO, use this section to change pin numbers if your wiring differs from mine
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
A = 22
B = 23
C = 24
D = 25
RedButton = 26
GreenButton = 27
RedLed = 16
GreenLed = 17
PumpRelais = 0
GPIO.setup(A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(D, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RedButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GreenButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RedLed,GPIO.OUT)
GPIO.setup(GreenLed,GPIO.OUT)
GPIO.setup(PumpRelais,GPIO.OUT)

def pump_on_led(): # The LED's for pump on indefinately, started as a thread in pump_on
	GPIO.output(RedLed,GPIO.HIGH)
	while True:
		GPIO.output(GreenLed,GPIO.LOW)
		time.sleep(0.5)
		GPIO.output(GreenLed,GPIO.HIGH)
		time.sleep(0.5)
		if stop_threads:
			break

def pump_on_timer_led(): # The LED's for pump on timer, started as a thread in pump_on_timer
	while True:
		GPIO.output(GreenLed,GPIO.LOW)
		GPIO.output(RedLed, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(GreenLed,GPIO.HIGH)
		GPIO.output(RedLed,GPIO.LOW)
		time.sleep(0.5)
		if stop_threads:
			break

def pump_on(): # Turns the pump on
	global stop_threads
	stop_threads = False
	t1 = threading.Thread(target = pump_on_led)
	t1.start()
	TimeOn = datetime.now()
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
		if GPIO.input(B):
			logging.debug('Input B')
			logging.info('Pump turned off remotely, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			input()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Pump turned off locally, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			input()
			break

def pump_on_timer(): # Turns on the pump and turns it off after a set time
	global stop_threads
	stop_threads = False
	t1 = threading.Thread(target = pump_on_timer_led)
	t1.start()
	TimeOn = datetime.now()
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
		if GPIO.input(B):
			logging.debug('Input B')
			logging.info('Timer interrupted remotely, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			input()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer interrupted locally, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			input()
			break
		elif datetime.now() > TimeOff:
			logging.info('Pump turned off by timer, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			input()
			break

def input():
	GPIO.output(GreenLed,GPIO.HIGH)
	GPIO.output(RedLed,GPIO.LOW)
	global TimeOff
	while True:
		if GPIO.input(A):
			logging.debug('Input A')
			logging.info('Pump turned on remotely')
			pump_on()
		elif GPIO.input(C):
			logging.debug('Input C')
			TimeOff = datetime.now() + timedelta(minutes = 30)
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

if __name__ == "__main__":
	try:
		logging.info('rainmaker started')
		input()
	except RuntimeError as error:
		print(error.args[0])
		logging.error(error.args[0])
		GPIO.input(RedLed,HIGH)
	except KeyboardInterrupt:
		print("\nExiting application\n")
		# exit the applications
		logging.info('rainmaker stopped')
		GPIO.cleanup()

import logging
from datetime import datetime, timedelta, time
import RPi.GPIO as GPIO
import threading
import time
import smbus
from lcd_i2c import lcd_string, lcd_init

#logging, logs all events to the file rainmaker.log
logging.basicConfig(filename='/home/pi/rainmaker.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO, use this section to change pin numbers if your wiring differs from mine
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
A = 21
B = 20
C = 19
D = 16
RedButton = 22
GreenButton = 24
RedLed = 23
GreenLed = 25
PumpRelais = 4
clk = 13
dt = 12
SW = 6
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(D, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RedButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GreenButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RedLed,GPIO.OUT)
GPIO.setup(GreenLed,GPIO.OUT)
GPIO.setup(PumpRelais,GPIO.OUT)

#LCD
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

lcd_init()

def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    if hours < 10:
        hours = '0%s' % int(hours)
    if minutes < 10:
        minutes = '0%s' % minutes
    if seconds < 10:
        seconds = '0%s' % seconds
    return '%s:%s' % (hours, minutes)

def pump_on_led(): # The LED's for pump on indefinately, started as a thread in pump_on
	GPIO.output(RedLed,GPIO.HIGH)
	while True:
		GPIO.output(GreenLed,GPIO.LOW)
		time.sleep(0.5)
		GPIO.output(GreenLed,GPIO.HIGH)
		time.sleep(0.5)
		if stop_threads:
			break

def timer_menu_led(stop_event): # The LED's for pump on indefinately, started as a thread in pump_on
	GPIO.output(GreenLed,GPIO.LOW)
	while not stop_event.is_set():
		GPIO.output(RedLed,GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(RedLed,GPIO.LOW)
		time.sleep(0.8)
	logging.debug('Stop timer_menu_led')

def pump_on_lcd(): # The LCD for pump on indefinately, started as a thread in pump_on
	while True:
		Pumptime = datetime.now() - TimeOn
		lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
		lcd_string("Pomp aan   "+str(format_timedelta(Pumptime)),LCD_LINE_2)
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

def pump_on_timer_lcd(): # The LCD for pump on timer, started as a thread in pump_on_timer
	while True:
		lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
		if datetime.now() < TimeOn:
			lcd_string("Pomp aan:  "+TimeOn.strftime('%H:%M'),LCD_LINE_2)
			time.sleep(2)
			lcd_string("Pomp uit:  "+TimeOff.strftime('%H:%M'),LCD_LINE_2)
			time.sleep(2)
			if stop_threads:
				break
		elif datetime.now() >= TimeOn:
			lcd_string("Pomp uit:  "+TimeOff.strftime('%H:%M'),LCD_LINE_2)
			time.sleep(0.5)
			if stop_threads:
				break


def pump_on(): # Turns the pump on
	logging.debug('pump_on started')
	global stop_threads
	stop_threads = False
	t1 = threading.Thread(target = pump_on_led)
	t1.start()
	t2 = threading.Thread(target = pump_on_lcd)
	t2.start()
	TimeOn = datetime.now()
	while True:
		GPIO.output(PumpRelais,GPIO.HIGH)
		if GPIO.input(B):
			logging.debug('Input B')
			logging.info('Pump turned off remotely, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			t2.join()
			input()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			OnTime = (datetime.now() - TimeOn)
			logging.info('Pump turned off locally, on-time: %s', OnTime)
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			t2.join()
			input()
			break

def pump_on_timer(): # Turns on the pump and turns it off after a set time
	logging.debug('pump_on_timer started, StartTime = %s, EndTime = %s', TimeOn, TimeOff)
	global stop_threads
	stop_threads = False
#	TimeOn = datetime.now()
#	global TimeOff
#	TimeOff = datetime.now() + timedelta(minutes=1) #For testing purposes
	t1 = threading.Thread(target = pump_on_timer_led)
	t1.start()
	t2 = threading.Thread(target = pump_on_timer_lcd)
	t2.start()
	while True:
		if TimeOn > datetime.now():
			if GPIO.input(B):
				logging.debug('Input B')
				logging.info('Timer interrupted remotely')
				stop_threads = True
				t1.join()
				t2.join()
				input()
				break
			elif GPIO.input(RedButton):
				logging.debug('Input RedButton')
				logging.info('Timer interrupted locally')
				stop_threads = True
				t1.join()
				t2.join()
				input()
				break
		elif TimeOn <= datetime.now():
			GPIO.output(PumpRelais,GPIO.HIGH)
			if GPIO.input(B):
				logging.debug('Input B')
				logging.info('Timer interrupted remotely, on-time: %s', (datetime.now() - TimeOn))
				GPIO.output(PumpRelais,GPIO.LOW)
				stop_threads = True
				t1.join()
				t2.join()
				input()
				break
			elif GPIO.input(RedButton):
				logging.debug('Input RedButton')
				logging.info('Timer interrupted locally, on-time: %s', (datetime.now() - TimeOn))
				GPIO.output(PumpRelais,GPIO.LOW)
				stop_threads = True
				t1.join()
				t2.join()
				input()
				break
			elif datetime.now() >= TimeOff:
				logging.info('Pump turned off by timer, on-time: %s', (datetime.now() - TimeOn))
				GPIO.output(PumpRelais,GPIO.LOW)
				stop_threads = True
				t1.join()
				t2.join()
				input()
				break

def timer_menu():
	logging.debug('Timer menu started')
	global stop
	stop = threading.Event()
	global t1
	t1 = threading.Thread(target = timer_menu_led, args=(stop,))
	t1.start()
	now = datetime.now()
	global TimeOn
	TimeOn = now + timedelta(minutes=-now.minute,seconds=-now.second,microseconds=-now.microsecond) + timedelta(minutes=(int(now.minute/15)*15)+15)
	clkLastState = GPIO.input(clk)
	lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
	lcd_string("Start time "+TimeOn.strftime("%H:%M"),LCD_LINE_2)
	while True:
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)
		if clkState != clkLastState:
			time.sleep(0.02)
			if dtState != clkState:
				TimeOn += timedelta(minutes=15)
			else:
				TimeOn -= timedelta(minutes=15)
			lcd_string("Start time "+TimeOn.strftime("%H:%M"),LCD_LINE_2)
			print ("Start time = "+TimeOn.strftime("%H:%M"))
			clkLastState = clkState
			time.sleep(0.02)
		elif GPIO.input(SW) == False:
			time.sleep(0.1)
			logging.debug('Input SW')
			logging.info('Start Time set at '+ TimeOn.strftime("%H:%M"))
			timer_menu_end()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer menu closed without setting a timer')
			stop.set()
			t1.join()
			input()
			break

def timer_menu_end():
	logging.debug('Timer menu end started')
	global TimeOff
	TimeOff = TimeOn + timedelta(minutes=30)
	clkLastState = GPIO.input(clk)
	lcd_string("Start time "+TimeOn.strftime("%H:%M"),LCD_LINE_1)
	lcd_string("End time   "+TimeOff.strftime("%H:%M"),LCD_LINE_2)
	while True:
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)
		if clkState != clkLastState:
			time.sleep(0.02)
			if dtState != clkState:
				TimeOff += timedelta(minutes=15)
			else:
				TimeOff -= timedelta(minutes=15)
			lcd_string("End time   "+TimeOff.strftime("%H:%M"),LCD_LINE_2)
			print ("End time = "+TimeOff.strftime("%H:%M"))
			clkLastState = clkState
			time.sleep(0.02)
		elif GPIO.input(SW) == False:
			time.sleep(0.1)
			logging.debug('Input SW')
			logging.info('End time set at '+ TimeOff.strftime("%H:%M"))
			stop.set()
			t1.join()
			pump_on_timer()
			break # Removed break to see if RAINMAKER wouldn't appear ater pushing button while nothing else was configured
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer menu closed without setting a timer')
			stop.set()
			t1.join()
			input()
			break

def input():
	logging.debug('Input started')
	GPIO.output(GreenLed,GPIO.HIGH)
	GPIO.output(RedLed,GPIO.LOW)
	global TimeOn
	global TimeOff
	lcd_string("Pomp standby..",LCD_LINE_2)
	while True:
		lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
		if GPIO.input(A):
			logging.debug('Input A')
			logging.info('Pump turned on remotely')
			TimeOn = datetime.now()
			pump_on()
			break
		elif GPIO.input(C):
			logging.debug('Input C')
			TimeOn = datetime.now()
			TimeOff = datetime.now() + timedelta(minutes = 60)
			logging.info('Pump turned on remotely, timeOff set at: %s', TimeOff)
			pump_on_timer()
			break
		elif GPIO.input(D):
			logging.debug('Input D')
			TimeOn = datetime.now()
			TimeOff = datetime.now() + timedelta(minutes = 120
			logging.info('Pump turned on remotely, timeOff set at: %s', TimeOff)
			pump_on_timer()
			break
		elif GPIO.input(SW) == False:
			logging.debug('Input SW(rotenc)')
			time.sleep(0.1)
			timer_menu()
			break
		elif GPIO.input(GreenButton):
			logging.debug('Input GreenButton')
			logging.info('Pump turned on locally')
			TimeOn = datetime.now()
			pump_on()
			break

if __name__ == "__main__":
	try:
		logging.info('rainmaker started')
		lcd_init()
		input()
#		pump_on_timer() # For LCD testing purposes
	except RuntimeError as error:
		print(error.args[0])
		logging.exception(error.args[0])
		GPIO.input(RedLed,HIGH)
	except KeyboardInterrupt:
		print("\nExiting application\n")
		# exit the applications
		logging.info('rainmaker stopped')
		GPIO.cleanup()

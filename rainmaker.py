import logging
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import threading
import time
#from lcd_i2c import lcd
import smbus

#logging, logs all events to the file rainmaker.log
logging.basicConfig(filename='/home/pi/rainmaker.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

#GPIO, use this section to change pin numbers if your wiring differs from mine
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
A = 9
B = 25
C = 11
D = 8
RedButton = 26
GreenButton = 27
RedLed = 16
GreenLed = 17
PumpRelais = 5
clk = 18
dt = 15
SW = 22
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
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line
# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(3) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def pump_on_led(): # The LED's for pump on indefinately, started as a thread in pump_on
	GPIO.output(RedLed,GPIO.HIGH)
	while True:
		GPIO.output(GreenLed,GPIO.LOW)
		time.sleep(0.5)
		GPIO.output(GreenLed,GPIO.HIGH)
		time.sleep(0.5)
		if stop_threads:
			break

def timer_menu_led(): # The LED's for pump on indefinately, started as a thread in pump_on
	GPIO.output(GreenLed,GPIO.LOW)
	while True:
		GPIO.output(RedLed,GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(RedLed,GPIO.LOW)
		time.sleep(0.8)
		if stop_threads:
			break


def pump_on_lcd(): # The LCD for pump on indefinately, started as a thread in pump_on
	lcd_string("Pomp staat aan.",LCD_LINE_2)
	while True:
		lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
		time.sleep(1)
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
		lcd_string("Pomp uit:  "+TimeOff.strftime('%H:%M'),LCD_LINE_2)
		time.sleep(0.5)
		if stop_threads:
			break


def pump_on(): # Turns the pump on
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
	global stop_threads
	stop_threads = False
	TimeOn = datetime.now()
	global TimeOff
#	TimeOff = datetime.now() + timedelta(minutes=1) #For testing purposes
	t1 = threading.Thread(target = pump_on_timer_led)
	t1.start()
	t2 = threading.Thread(target = pump_on_timer_lcd)
	t2.start()
	while True:
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
		elif datetime.now() > TimeOff:
			logging.info('Pump turned off by timer, on-time: %s', (datetime.now() - TimeOn))
			GPIO.output(PumpRelais,GPIO.LOW)
			stop_threads = True
			t1.join()
			t2.join()
			input()
			break

def timer_menu():
	global stop_threads
	stop_threads = False
	t1 = threading.Thread(target = timer_menu_led)
	t1.start()
	now = datetime.now()
	global StartTime
	StartTime = now + timedelta(minutes=-now.minute,seconds=-now.second) + timedelta(minutes=(int(now.minute/15)*15)+15)
	#StartTime = now + timedelta(minutes=-now.minute,seconds=-now.second)
	clkLastState = GPIO.input(clk)
	lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
	lcd_string("Start time "+StartTime.strftime("%H:%M"),LCD_LINE_2)
	while True:
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)
		if clkState != clkLastState:
			time.sleep(0.02)
			if dtState != clkState:
				StartTime += timedelta(minutes=15)
			else:
				StartTime -= timedelta(minutes=15)
			lcd_string("Start time "+StartTime.strftime("%H:%M"),LCD_LINE_2)
			print ("Start time = "+StartTime.strftime("%H:%M"))
			clkLastState = clkState
			time.sleep(0.02)
		elif GPIO.input(SW) == False:
			time.sleep(0.05)
			logging.debug('Input SW')
			logging.info('Start Time set at '+ StartTime.strftime("%H:%M"))
			timer_menu_end()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer menu closed without setting a timer')
			stop_threads = True
			t1.join()
			input()
			break

def timer_menu_end():
#	StartTime = datetime.now()
	global EndTime
	EndTime = StartTime + timedelta(minutes=30)
	clkLastState = GPIO.input(clk)
	lcd_string("Start time "+StartTime.strftime("%H:%M"),LCD_LINE_1)
	lcd_string("End time   "+EndTime.strftime("%H:%M"),LCD_LINE_2)
	while True:
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)
		if clkState != clkLastState:
			time.sleep(0.02)
			if dtState != clkState:
				EndTime += timedelta(minutes=15)
			else:
				EndTime -= timedelta(minutes=15)
			lcd_string("End time   "+EndTime.strftime("%H:%M"),LCD_LINE_2)
			print ("End time = "+EndTime.strftime("%H:%M"))
			clkLastState = clkState
			time.sleep(0.02)
		elif GPIO.input(SW) == False:
			time.sleep(0.05)
			logging.debug('Input SW')
#			timer_menu_end()
			logging.info('End time set at '+ EndTime.strftime("%H:%M"))
			stop_threads = True
			t1.join()
			break
		elif GPIO.input(RedButton):
			logging.debug('Input RedButton')
			logging.info('Timer menu closed without setting a timer')
			stop_threads = True
			t1.join()
			input()
			break

def input():
	GPIO.output(GreenLed,GPIO.HIGH)
	GPIO.output(RedLed,GPIO.LOW)
	global TimeOff
	lcd_string("Pomp standby..",LCD_LINE_2)
	while True:
		lcd_string("RAINMAKER  "+datetime.now().strftime('%H:%M'),LCD_LINE_1)
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
		elif GPIO.input(SW) == False:
			logging.debug('Input SW(rotenc)')
			timer_menu()
		elif GPIO.input(GreenButton):
			logging.debug('Input GreenButton')
			logging.info('Pump turned on locally')
			pump_on()

if __name__ == "__main__":
	try:
		logging.info('rainmaker started')
		lcd_init()
		input()
#		pump_on_timer() # For LCD testing purposes
	except RuntimeError as error:
		print(error.args[0])
		logging.error(error.args[0])
		GPIO.input(RedLed,HIGH)
	except KeyboardInterrupt:
		print("\nExiting application\n")
		# exit the applications
		logging.info('rainmaker stopped')
		GPIO.cleanup()

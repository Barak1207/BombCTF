# The wiring for the LCD is as follows:
# 0 : GND
# 2 : 5V
# 3 : Contrast (0-5V)
# 4 : RS (Register Select)
# 5 : R/W (Read Write)	   - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0			 - NOT USED
# 8 : Data Bit 1			 - NOT USED
# 9 : Data Bit 2			 - NOT USED
# 10: Data Bit 3			 - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 15: LCD Backlight GND
 


#import
import threading
import RPi.GPIO as GPIO
import time

 
# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
 
# Define some device constants
LCD_LINES = 4
LCD_WIDTH = 20	# Maximum characters per line

LCD_CHR = True
LCD_CMD = False


LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 #...
LCD_LINE_4 = 0xD4 #...
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
 

BYTE_LOCK = threading.Lock()

class LCD_timer_thread():

	__instance = None

	def __init__(self, time, line, delay=1):
		#Time should be in how many seconds to run 
		if not LCD_timer_thread.__instance:

			LCD_timer_thread.__instance = self

			self.running = True

			self.time = time
			self.line = line
			self.delay = delay

			self.lock = threading.Lock()
			#@(self)
			threading.Thread( target=self.__LCD_timer_text, args=() ).start()

		else:
			raise ValueError('Can\'t have two instances of LCD_timer_thread')

	def stop(self):
		#Break infinite loop if there is one, makes baddy thready go away.
		#Pretty much kills this shit class anyways		
		self.running = False

		m, s = divmod(self.time, 60)
		h, m = divmod(m, 60)
		#ms = divmod(s, 100)
		ti = "%02d:%02d:%02d" % (h, m, s)
		#print ti
		LCD_text((' '*((LCD_WIDTH-len(ti))/2)) + ti, self.line)
		#while self.__running:#To make sure scroll text loop doesn't do another iteration
		#	time.sleep(E_DELAY)
		time.sleep(.1)
		#LCD_text('', self.line)
		#print 'STOP!'
		LCD_timer_thread.__instance = None

	def is_running(self):
		return self.running

	def set_time(self, time):
		try:
			self.lock.acquire()
			self.time = time
		finally:
			self.lock.release()
	def get_time(self):
		t = -1
		try:
			self.lock.acquire()
			t = self.time
		finally:
			self.lock.release()
			return t

	def set_delay(self, delay):
		try:
			self.lock.acquire()
			self.delay = delay
		finally:
			self.lock.release()
	def get_delay(self):
		try:
			self.lock.acquire()
		finally:
			self.lock.release()		
			return self.delay

	def __LCD_timer_text(self):
		LCD_text('', self.line)
		while self.time >= 0 and self.running:
			try:
				self.lock.acquire()
				if self.time <= 10*60 and self.delay >= 1 and self.time % 2:
						LCD_text('', self.line)
				else:
					m, s = divmod(self.time, 60)
					h, m = divmod(m, 60)
					#ms = divmod(s, 100)
					ti = "%02d:%02d:%02d" % (h, m, s)
					#print ti
					LCD_text((' '*((LCD_WIDTH-len(ti))/2)) + ti, self.line)

			finally:
				self.time -= 1
				self.lock.release()
				time.sleep(self.delay)

		self.stop()
		






class LCD_thread():
	#Creates a thread in which to run an infinite scrolling text loop if text length > LCD_WIDTH
	#Just fucking prints the text (w/o a new thread) to LCD if length is shorter than LCD_WIDTH

	__instance = None

	def __init__(self, text, line):

		if not LCD_thread.__instance:

			LCD_thread.__instance = self

			self.delay = 0.15
			
			self.__line = line
			self.__len = len(text)

			
			self.__cont = True
			self.__running = True


			if self.__len > LCD_WIDTH:
				#Need to infinite scroll, new thread.
				threading.Thread( target=self.__LCD_scroll_text, args=(text, self.__line) ).start()

			else:
				#Just fucking print that shit up nigga
				LCD_text(text, self.__line, delay=self.delay)
		else:
			raise ValueError('Can\'t have two instances of LCD_thread')


	def stop(self):
			#Break infinite loop if there is one, makes baddy thready go away.
			#Pretty much kills this shit class anyways		
			self.__cont = False

			#while self.__running:#To make sure scroll text loop doesn't do another iteration
			#	time.sleep(E_DELAY)
			time.sleep(.1)
			LCD_text('', self.__line)

			LCD_thread.__instance = None


	def wrapper(func):
		def inner(self, *args, **kwargs): # inner function needs parameters

			return func(self,  *args, **kwargs) # call the wrapped function
			print 'here'
			self.__running = False
		return inner # return the inner function (don't call it)

	@wrapper
	def __LCD_scroll_text(self, text, line, scroll_delay=0.4):

		pause = 2 * scroll_delay

		LCD_text(text[0 : LCD_WIDTH], self.__line, delay=self.delay)

		while self.__cont:
			#Scroll left, <-text
			for i in range(0, (self.__len - LCD_WIDTH) + 1 ):

				if not self.__cont:
					#If need to stop, don't wait for next iteration of outer while loop
					return

				LCD_text(text[ i : i + LCD_WIDTH ], self.__line)
				time.sleep(scroll_delay)

			time.sleep(pause)

			#Scroll right, text->
			for i in range(0, (self.__len - LCD_WIDTH) + 1):

				if not self.__cont:
					##
					return

				LCD_text(text[ self.__len - LCD_WIDTH - i :  self.__len - i ], self.__line)
				time.sleep(scroll_delay)

			time.sleep(pause)

		return 







def init_LCD():

	#init GPIO for LCD
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)	   # Use BCM GPIO numbers
	GPIO.setup(LCD_E, GPIO.OUT)  # E
	GPIO.setup(LCD_RS, GPIO.OUT) # RS
	GPIO.setup(LCD_D4, GPIO.OUT) # DB4
	GPIO.setup(LCD_D5, GPIO.OUT) # DB5
	GPIO.setup(LCD_D6, GPIO.OUT) # DB6
	GPIO.setup(LCD_D7, GPIO.OUT) # DB7



  # Initialise display
	LCD_byte(0x33,LCD_CMD) # 110011 Initialise
	LCD_byte(0x32,LCD_CMD) # 110010 Initialise
	LCD_byte(0x06,LCD_CMD) # 000110 Cursor move direction
	LCD_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
	LCD_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
	LCD_byte(0x01,LCD_CMD) # 000001 Clear display
	time.sleep(E_DELAY)
 


def LCD_byte(bits, mode):
	# Send byte to data pins
	# bits = data
	# mode = True  for character, False for command
	GPIO.output(LCD_RS, mode) # RS
	# High bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x10==0x10:
		GPIO.output(LCD_D4, True)
	if bits&0x20==0x20:
		GPIO.output(LCD_D5, True)
	if bits&0x40==0x40:
		GPIO.output(LCD_D6, True)
	if bits&0x80==0x80:
		GPIO.output(LCD_D7, True)

	# Toggle 'Enable' pin
	LCD_toggle_enable()
	# Low bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x01==0x01:
		GPIO.output(LCD_D4, True)
	if bits&0x02==0x02:
		GPIO.output(LCD_D5, True)
	if bits&0x04==0x04:
		GPIO.output(LCD_D6, True)
	if bits&0x08==0x08:
		GPIO.output(LCD_D7, True)
	# Toggle 'Enable' pin
	LCD_toggle_enable()
 
def LCD_toggle_enable():
	# Toggle enable
	time.sleep(E_DELAY)
	GPIO.output(LCD_E, True)
	time.sleep(E_PULSE)
	GPIO.output(LCD_E, False)
	time.sleep(E_DELAY)


def LCD_clear():
	try:
		BYTE_LOCK.acquire()
		LCD_byte(0x01,LCD_CMD) # 000001 Clear display
		time.sleep(E_DELAY)
	finally:
		BYTE_LOCK.release()
		time.sleep(E_DELAY)


def LCD_text(text, line, delay=0):
	# Send text to display
	try:
		BYTE_LOCK.acquire()	
		text = text.ljust(LCD_WIDTH," ")
		LCD_byte(line, LCD_CMD)
		for i in range(LCD_WIDTH):
			LCD_byte(ord(text[i]), LCD_CHR)
			time.sleep(delay)
	finally:
		BYTE_LOCK.release()
		time.sleep(E_DELAY)

def LCD_text_long(text, delay=0):
	#Takes long text splits by number of lines of LCD and prints starting from line 1.
	#Splits text to number of lines in LCD, each split will be LCD_WIDTH in length.
	try:
		BYTE_LOCK.acquire()	
		lines = [LCD_LINE_1, LCD_LINE_2,LCD_LINE_3,LCD_LINE_4]
		for (cur_line, split) in zip(lines, [ text[i:i+LCD_WIDTH].strip() for i in range(0, LCD_LINES*LCD_WIDTH, LCD_WIDTH) ]):
			LCD_text(split, cur_line, delay)
	finally:
		BYTE_LOCK.release()
		time.sleep(E_DELAY)


def LCD_scroll_text(text, line, delay=0.3, infinite=False):
	pause = 0.5
	txt_len = len(text)
	try:
		BYTE_LOCK.acquire()	
		while True:
			#Scroll left, <-text
			for i in range(0, (txt_len - LCD_WIDTH) + 1 ):
				LCD_byte(line, LCD_CMD)
				LCD_text(text[ i : i + LCD_WIDTH ], line)
				time.sleep(delay)

			time.sleep(pause)

			#Scroll right, text->
			for i in range(0, (txt_len - LCD_WIDTH) + 1):
				LCD_byte(line, LCD_CMD)
				LCD_text(text[ txt_len - LCD_WIDTH - i :  txt_len - i ], line)
				time.sleep(delay)

			time.sleep(pause)

			if not infinite:
				break
	finally:
		BYTE_LOCK.release()
		time.sleep(E_DELAY)

def LCD_more_text(text, location, direction='f', delay=0):
	#location = begining of shown text.
	try:
		BYTE_LOCK.acquire()	
		#backwards
		if 'b' in direction.lower():

			if (location - (LCD_LINES*LCD_WIDTH)) >= 0:
				LCD_text_long(text[location - (LCD_LINES*LCD_WIDTH) : location ], delay)
			else:			
				LCD_text_long(text[0 : (LCD_LINES*LCD_WIDTH)], delay)
		else:
			#Don't display out of bound index
			if not (location >= len(text)):
				LCD_text_long(text[ location : location + (LCD_LINES*LCD_WIDTH)] , delay)			
			#else :
			#	LCD_text_long(text[location : location + (LCD_LINES*LCD_WIDTH) ], delay) #+ (LCD_LINES*LCD_WIDTH) : location + (2*LCD_LINES*LCD_WIDTH) ], delay)
		
	finally:
		BYTE_LOCK.release()
		time.sleep(E_DELAY)			

#sudo rm 'LCD_module_420.py' ; sudo rm 'LCD_module_420.pyc' ; sudo wget 'http://10.0.0.7/Ethan Raspberry/modern_beeper/LCD_module_420.py'




def __LCD_scroll_text(text, line, infinite=False, scroll_delay=0.3):

	pause = 2 * scroll_delay
	length = len(text)
	LCD_text(text[0 : LCD_WIDTH], line, delay=scroll_delay)

	while infinite:
		#Scroll left, <-text
		for i in range(0, (length - LCD_WIDTH) + 1 ):

			if not infinite:
				#If need to stop, don't wait for next iteration of outer while loop
				return

			LCD_text(text[ i : i + LCD_WIDTH ], line)
			time.sleep(scroll_delay)

		time.sleep(pause)

		#Scroll right, text->
		for i in range(0, (length - LCD_WIDTH) + 1):

			if not infinite:
				##
				return

			LCD_text(text[ length - LCD_WIDTH - i :  length - i ], line)
			time.sleep(scroll_delay)

		time.sleep(pause)

	return 

import morsepy
import LCD_module_420

from functools import partial
from threading import Thread
import socket
import SimpleHTTPServer
import SocketServer
import subprocess
import RPi.GPIO as GPIO
from time import sleep
from os import getcwd, chdir, system, stat

OMX_PAUSE_RESUME = 'p'#Button for media player
OMX_QUIT = 'q'


HOUR = 3600
MINUTE = 60
SECOND = 1

GREEN_LED = 20
RED_LED = 16

A_BUTTON = 10
B_BUTTON = 9
C_BUTTON = 11

ORANGE_WIRE = 26
BLUE_WIRE = 19
RED_WIRE = 13
GREEN_WIRE = 6

CWD = getcwd()
			#Turing  #DNS+HTTPS #UNIX Time #Fibonnaci(19)
PORT_KNOCKS = [1912, 	496, 		1970, 		4181] #last port will be used for the actual server

CORRECT_PIN_CODE = '13321311'#





class port_knocker:

	def __init__(self, ports):
		#Cockstructor
		self.ports = ports
		self.__port_knocker__(self.ports)

	def __open_and_wait_socket__(self, port):
			#Pretty ugly and shitty,used only for port knocker!
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('0.0.0.0', port))
			s.listen(1)
			conn, addr = s.accept()
			conn.close()
			s.close()
			return addr[0]


	def __port_knocker__(self, ports):
		
		knock_succesfull = False
		#Until order of ports is achieved you wanker
		while not knock_succesfull:
			knock_succesfull = True
			#Get address that accessed the first port in the series.
			old_addr = self.__open_and_wait_socket__(ports[0])
			for p in ports[1:]:
				new_addr = self.__open_and_wait_socket__(p)
				#Check that the same address keeps with the ports series, so you don't get fooled playa.
				if new_addr != old_addr:
					knock_succesfull = False
					break

				old_addr = new_addr




def init_GPIO():
	GPIO.setwarnings(False)

	GPIO.setmode(GPIO.BCM)		# Use BCM GPIO numbers

	GPIO.setup(GREEN_LED, GPIO.OUT)
	GPIO.output(GREEN_LED, False)

	GPIO.setup(RED_LED, GPIO.OUT)
	GPIO.output(RED_LED, False)

	GPIO.setup(A_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(C_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	GPIO.setup(B_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

	GPIO.setup(ORANGE_WIRE, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(BLUE_WIRE, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(RED_WIRE, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(GREEN_WIRE, GPIO.IN, pull_up_down = GPIO.PUD_UP)



def get_internal_IP():
	#DISGUSTING!
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('www.google.com', 80))
	ip =  s.getsockname()[0]
	s.close()
	return ip


#Please excuse this duplicate code, since RED_LED is used for morse thread, it needs to have an
#independent functions
def blink_RED_LED(iters=2, delay=.2):
	for i in xrange(0, iters):
		RED_LED_on()
		sleep(delay)
		RED_LED_off()
		sleep(delay)
def blink_GREEN_LED(iters=2, delay=.2):
	for i in xrange(0, iters):
		GREEN_LED_on()
		sleep(delay)
		GREEN_LED_off()
		sleep(delay)

def RED_LED_on():
	global RED_LED
	GPIO.output(RED_LED, True)
def RED_LED_off():
	global RED_LED
	GPIO.output(RED_LED, False)
def GREEN_LED_on():
	global GREEN_LED
	GPIO.output(GREEN_LED, True)
def GREEN_LED_off():
	global GREEN_LED
	GPIO.output(GREEN_LED, False)


def set_timer_and_lcd(lcd_thread, time, line, sound_proc, sound_file):
	if sound_proc:
		sound_proc.stdin.write(OMX_QUIT)

	if not lcd_thread:
		lcd_thread = LCD_module_420.LCD_timer_thread(time, line)
	else:
		lcd_thread.set_time(time)
		
	sound_proc = subprocess.Popen([r'omxplayer', '-b', '--loop', sound_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	sound_proc.stdin.write(OMX_PAUSE_RESUME)

	sleep(1)#For syncing
	sound_proc.stdin.write(OMX_PAUSE_RESUME)

	return lcd_thread, sound_proc




def button_pin_sequence(correct_pin, line=LCD_module_420.LCD_LINE_3):
	input_pin_code = ''
	new_char = ''
	CORR_PIN_LEN = len(correct_pin)
	#Add events to buttons.
	GPIO.add_event_detect(A_BUTTON, GPIO.RISING, bouncetime=200)
	GPIO.add_event_detect(B_BUTTON, GPIO.RISING, bouncetime=200)
	GPIO.add_event_detect(C_BUTTON, GPIO.RISING, bouncetime=200)

	LCD_module_420.LCD_text('PIN:  ', line)
	#This is very ugly and I'm sorry
	while input_pin_code != correct_pin:
		sleep(.1)		
		a, b, c = GPIO.event_detected(A_BUTTON), GPIO.event_detected(B_BUTTON), GPIO.event_detected(C_BUTTON)
		new_char =''
		#If any events detected, add the the assigned char to string
		if a:
			new_char = '1'
		elif b:
			new_char = '2'
		elif c:
			new_char = '3'

		if a or b or c:
			input_pin_code += new_char

			if len(input_pin_code) > CORR_PIN_LEN:
				#input is longer than correct pin, reset!
				#Flash red light
				Thread(target=blink_RED_LED).start()
				input_pin_code = ''
				new_char = ''
				LCD_module_420.LCD_text('PIN:  ', line)

			else:
				#Mask all string except for new char to ***, like you would see on a password field in a phone.
				LCD_module_420.LCD_text('PIN:  ' + '*'*(len(input_pin_code)-1) + new_char, line)

	LCD_module_420.LCD_text('PIN:  ' + '*'*CORR_PIN_LEN, line)
	GPIO.remove_event_detect(A_BUTTON)
	GPIO.remove_event_detect(B_BUTTON)
	GPIO.remove_event_detect(C_BUTTON)




try:
	#http_server = subprocess.Popen([r'python', '-m', 'SimpleHTTPServer', str(80)]) #Don't user, lighttd is the main server!


	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('0.0.0.0', 1337))
	s.listen(1)
	conn, addr = s.accept()
	conn.close()
	s.close()








	init_GPIO()
	LCD_module_420.init_LCD()
	LCD_module_420.LCD_clear()

	#system('python /home/pi/Barak/DisplayIP.py')
	LCD_module_420.LCD_text(get_internal_IP(), LCD_module_420.LCD_LINE_1)

	print 'Starting countdown.'
	#Returns a *NEW* (Becuase we sent None) lcd_thread and beep_process
	lcd_timer_thread, timer_sound_proc = set_timer_and_lcd(None, 2*HOUR, LCD_module_420.LCD_LINE_4, None, 'beep_two.mp3')

	#Get ready for morse
	GREEN_LED_on()
	sleep(2)
	GREEN_LED_off()

	print 'Stating morse challenge.'
	morse_thread = morsepy.transmit_morse('pkPNG', RED_LED_on, RED_LED_off, True)

	#Start port knocker challenge, last port for http server
	print 'Starting port knocker challenge.'
	port_knocker(PORT_KNOCKS[:-1])#BLOCKING

	#Start http server on last port on the list
	print 'Stating port knocker server.'
	port_knocker_server = subprocess.Popen([r'python', '-m', 'SimpleHTTPServer', str(PORT_KNOCKS[-1])], cwd=r'port_knocker', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	#Wait for player to access the final port, the http server.
	while 'GET' not in port_knocker_server.stdout.readline():#BLOCKING
		sleep(.5)

	print 'Success on port knocker!'
	#Stopping a thread with a different thread, risky move Barak...risky move.
	Thread(target=morse_thread.stop).start()
	Thread(target=blink_GREEN_LED).start()
	

	lcd_timer_thread, timer_sound_proc = set_timer_and_lcd(lcd_timer_thread, 1*HOUR, LCD_module_420.LCD_LINE_4, timer_sound_proc, 'beep_one.mp3')


	#Wait for player to access the correct file on the new http server.
	#while PORT_KNOCKER_SERVER_CLUE_FILE not in port_knocker_server.stdout.readline():#BLOCKING
	#	sleep(.5)

	print 'Starting PIN challenge.'
	button_pin_sequence(CORRECT_PIN_CODE, line=LCD_module_420.LCD_LINE_3)#BLOCKING

	#Flash green light
	Thread(target=blink_GREEN_LED).start()
	print 'Success on PIN challenge!'

	
	#ALL THIS GARBAGE IS JUST TO PRINT TO LCD IN A COOL WAY
	sleep(2)
	cool_phrase = '/wires_are_red.jpg'
	lock_hashes_len = len(cool_phrase)
	LCD_module_420.LCD_text('', LCD_module_420.LCD_LINE_3)
	sleep(1.5)
	LCD_module_420.LCD_text(' '+'*'*lock_hashes_len, LCD_module_420.LCD_LINE_3, delay=0.08)
	sleep(1.5)
	for i in xrange(1, lock_hashes_len+1):
		LCD_module_420.LCD_text(' '+cool_phrase[:i]+'*'*(lock_hashes_len-i), LCD_module_420.LCD_LINE_3, delay=0.0023)



	lcd_timer_thread, timer_sound_proc = set_timer_and_lcd(lcd_timer_thread, 10*MINUTE, LCD_module_420.LCD_LINE_4, timer_sound_proc, 'beep_half.mp3')


	print 'Starting cut the wire challenge.'
	#This is very ugly and I'm sorry
	GPIO.add_event_detect(ORANGE_WIRE, GPIO.RISING, bouncetime=50000)
	GPIO.add_event_detect(BLUE_WIRE, GPIO.RISING, bouncetime=50000)
	GPIO.add_event_detect(RED_WIRE, GPIO.RISING, bouncetime=50000)
	GPIO.add_event_detect(GREEN_WIRE, GPIO.RISING, bouncetime=50000)
	#Final challenegrt
	one_more_cut = False
	while True:
		sleep(.1)
		orange, blue, red, green = GPIO.event_detected(ORANGE_WIRE), GPIO.event_detected(BLUE_WIRE), GPIO.event_detected(RED_WIRE), GPIO.event_detected(GREEN_WIRE)

		if orange or green:
			if orange:
				print 'Orange cut!'
				GPIO.remove_event_detect(ORANGE_WIRE)
			elif green:
				print 'Green cut!'
				GPIO.remove_event_detect(GREEN_WIRE)

			if not one_more_cut:
				one_more_cut = True#Boolean to indicate that the two wires were cut.

				timer_sound_proc.stdin.write(OMX_PAUSE_RESUME)
				t = lcd_timer_thread.get_time()
				lcd_timer_thread.stop()
				sleep(2)
				LCD_module_420.LCD_text('...', LCD_module_420.LCD_LINE_3, delay=0.1)
				lcd_timer_thread, timer_sound_proc = set_timer_and_lcd(None, t, LCD_module_420.LCD_LINE_4, timer_sound_proc, 'bomb_alert.mp3')				
				lcd_timer_thread.set_delay(0.01)
			else:
				break;
				

		elif blue or red or lcd_timer_thread.get_time() <= 0:
			timer_sound_proc.stdin.write(OMX_QUIT)
			lcd_timer_thread.set_time(0)
			lcd_timer_thread.stop()

			sleep(2)
			sound_proc = subprocess.Popen([r'omxplayer', '-b','timer_explode.mp3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			LCD_module_420.LCD_text('', LCD_module_420.LCD_LINE_3)
			LCD_module_420.LCD_text('      Boom... you lose', LCD_module_420.LCD_LINE_3, delay=.2)
			for i in xrange(39, -1, -1):	
				LCD_module_420.LCD_text('', LCD_module_420.LCD_LINE_2)
				LCD_module_420.LCD_text('Shutdown in ' + str(i), LCD_module_420.LCD_LINE_2)
				sleep(1)
				system('init 0')

			if blue:
				print 'Blue cut!'
				GPIO.remove_event_detect(BLUE_WIRE)
			elif red:
				print 'Red cut!'
				GPIO.remove_event_detect(BLUE_WIRE)
			raise ValueError('BOOM!')

	GPIO.remove_event_detect(ORANGE_WIRE)
	GPIO.remove_event_detect(BLUE_WIRE)
	GPIO.remove_event_detect(RED_WIRE)
	GPIO.remove_event_detect(GREEN_WIRE)


	#print 'TIMEOUT'
	print 'Statring cut the wire challenge!'
	print 'Enjoy your well deserved Taylor Swift'


	timer_sound_proc.stdin.write(OMX_QUIT)
	lcd_timer_thread.stop()
	sleep(2)
	#timer_sound_proc = subprocess.Popen([r'omxplayer', '-b', 'explode.mp3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	timer_sound_proc = subprocess.Popen([r'omxplayer', '-b','Sparks_Fly.mp3'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#LCD_module_420.LCD_clear()
	LCD_module_420.LCD_text('', LCD_module_420.LCD_LINE_3)
	Thread(target=LCD_module_420.__LCD_scroll_text, args=('Flag{TaylorSwift:SparksFly}', LCD_module_420.LCD_LINE_3), kwargs={'infinite': True, 'scroll_delay': 0.27}).start()
	#LCD_module_420.__LCD_scroll_text('Flag{TaylorSwift:SparksFly}', LCD_module_420.LCD_LINE_3, infinite=True, scroll_delay=0.27)
	##sleep(20)
	#lcd_timer_thread.set_time(10)

	sleep(10)
	for i in xrange(59, -1, -1):	
		LCD_module_420.LCD_text('', LCD_module_420.LCD_LINE_2)
		LCD_module_420.LCD_text('Shutdown in ' + str(i), LCD_module_420.LCD_LINE_2)
		sleep(1)
	system('init 0')


except Exception, e:
	print e
finally:
	print 'Finally'
	#system('kill ' + str(port_knocker_server.pid))
	lcd_timer_thread.stop()
	morse_thread.stop()
	RED_LED_off()
	GREEN_LED_off()
	print 'CLEANUP ON AISLE 7'
	GPIO.cleanup()
	port_knocker_server.kill()


	print 'FINISHED!'



#rm cyber_hw_1.py; wget http://10.0.0.7:888/cyber_hw_1.py && sudo python cyber_hw_1.py

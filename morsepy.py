#from SendKeys import SendKeys as send_keys
from time import sleep
from sys import argv
#from win32api import GetKeyState as get_key_state
#from win32con import VK_CAPITAL, VK_NUMLOCK, VK_SCROLL
import threading

TIME_UNIT = 0.3

DOT = TIME_UNIT
DASH = 3*TIME_UNIT

INTER_ELEMENT_GAP = TIME_UNIT
SHORT_GAP = 3*TIME_UNIT
MEDIUM_GAP = 7*TIME_UNIT


INTERNATIONAL_MORSE_CODE = {
'A': [DOT, DASH],
'B': [DASH, DOT, DOT, DOT],
'C': [DASH, DOT, DASH, DOT],
'D': [DASH, DOT, DOT],
'E': [DOT],
'F': [DOT, DOT, DASH, DOT],
'G': [DASH, DASH, DOT],
'H': [DOT, DOT, DOT, DOT],
'I': [DOT, DOT],
'J': [DOT, DASH, DASH, DASH],
'K': [DASH, DOT, DASH],
'L': [DOT, DASH, DOT, DOT],
'M': [DASH, DASH],
'N': [DASH, DOT],
'O': [DASH, DASH, DASH],
'P': [DOT, DASH, DASH, DOT],
'Q': [DASH, DASH, DOT, DASH],
'R': [DOT, DASH, DOT],
'S': [DOT, DOT, DOT],
'T': [DASH],
'U': [DOT, DOT, DASH],
'V': [DOT, DOT, DOT, DASH],
'W': [DOT, DASH, DASH],
'X': [DASH, DOT, DOT, DASH],
'Y': [DASH, DOT, DASH, DASH],
'Z': [DASH, DASH, DOT, DOT],

'1': [DOT, DASH, DASH, DASH, DASH],
'2': [DOT, DOT, DASH, DASH, DASH],
'3': [DOT, DOT, DOT, DASH, DASH],
'4': [DOT, DOT, DOT, DOT, DASH],
'5': [DOT, DOT, DOT, DOT, DOT],
'6': [DASH, DOT, DOT, DOT, DOT],
'7': [DASH, DASH, DOT, DOT, DOT],
'8': [DASH, DASH, DASH, DOT, DOT],
'9': [DASH, DASH, DASH, DASH, DOT],
'0': [DASH, DASH, DASH, DASH, DASH]}


def is_caps_on():
	return get_key_state(VK_CAPITAL)

def is_num_on():
	return get_key_state(VK_NUMLOCK)

def is_scroll_on():
	return get_key_state(VK_SCROLL)

#def set_led_state(caps_state, num_state, scroll_state):
#	if caps_state ^ is_caps_on():
#		send_keys('{CAPSLOCK}')
#	if num_state ^ is_num_on():
#		send_keys('{NUMLOCK}')
#	if scroll_state ^ is_scroll_on():
#		send_keys('{SCROLLLOCK}')


class transmit_morse:

	def __init__(self, phrase, toggle_on, toggle_off, infinite):

		self.phrase = phrase
		self.toggle_on = toggle_on
		self.toggle_off = toggle_off
		self.infinite = infinite
		self.running = True

		self.thrd = threading.Thread( target=self.__transmit_morse__, args=() )
		self.thrd.start()

	def stop(self):
		self.running = False
		self.thrd.join()
#	def toggle_keyboard_led_transmittor(self):
#			send_keys('{CAPSLOCK}{NUMLOCK}{SCROLLLOCK}', pause=0)


	def __morse_letter__(self, letter):
		try:
			morse_list = INTERNATIONAL_MORSE_CODE[letter.upper()]
		except Exception, e:
			#Letter not in talbe
			return
		for t in morse_list:
			if not self.running:
					return

			self.toggle_on()
			sleep(t)
			self.toggle_off()
			sleep(INTER_ELEMENT_GAP)


	def __morse_word__(self, word):
		for c in word:
			if not self.running:
					return

			self.__morse_letter__(c)
			sleep(SHORT_GAP)


	def __transmit_morse__(self):
		words = self.phrase.split(' ')
		while True:
			for w in words:

				if not self.running:
					return
				self.__morse_word__(w)
				sleep(MEDIUM_GAP)
			if not self.infinite:
				return
			self.toggle_off()
			sleep(2*MEDIUM_GAP)

#rm -f morsepy.pyc  morsepy.py;wget http://10.0.0.7:888/morsepy.py 

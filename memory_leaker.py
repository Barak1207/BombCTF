from sys import argv
from string import lowercase as string_lowercase
from string import uppercase as string_uppercase
from random import choice, randint

RAND_MIN = 100
RAND_MAX = 600

SECRET = '***' + 'LOCK: ' + '958' + '***'#TOOK FROM MAIN FILE, DON'T FORGET TO UPDATE IF CHANGED PLEASE BARAK!
ITER = 9
RANDOM_INDEX = randint(ITER/4, ITER/3)

SPECIAL_CHARS = './?~;...........:"[]{..........................,}||~!@#     $%^....&*()_+'
RANDOM_PHRASES = ['dEfuSe', 'defuse ME', 'CyBer', 'Sponsored by Dr.Pepper!', 'win a free iPad today!!', '404', '200', '302', 'rediect', 'catz.png', 'Time is running low', 'MemLeak!', 'memLEAK', 'Warning','###', '....', '.php', 'smokeWeEd', '2016', 'garbage' , 'President Trump', '1912' , '#891723', 'reports', 'Kahana zadaq', 'microsoft', 'linux', 'HOT singlels in your area!', 'giellete fusion', 'I\'m loving it', 'Coca Cola', 'Viagra now!', '1=1;', 'www.google.com', 'lighttd','Taylor Swift', 'Mastic Five', 'Fast cash instant!!!']


#Hopefully the "player" realized that you can send fake content length, generating a so called memory leak


try:
	fake_content_len = min(RAND_MAX*ITER, int(argv[1])) #recieved by form
	content = ' '.join(argv[2:]).replace('\n', '\\n')
	real_content_len = len(content)
except Exception, e:
	fake_content_len = 0

final_string = content + '  '
for i in xrange(0, ITER+1):

	if i == RANDOM_INDEX:
		final_string += SECRET

	final_string += ''.join( choice(SPECIAL_CHARS) for x in range(randint(RAND_MIN, RAND_MAX)) )
	final_string += choice(RANDOM_PHRASES)
	final_string += ''.join( choice(SPECIAL_CHARS) for x in range(randint(RAND_MIN, RAND_MAX)) )

final_string += '...'


print final_string[ : real_content_len + max(0, fake_content_len - real_content_len) ]

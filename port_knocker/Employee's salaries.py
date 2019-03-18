import company
from os import system
from time import sleep


ONE_MONTH = 30*24*60*60

while(company.is_running):

	for employee in company.get_employees():
		system('employee.salary > /dev/null')

	print 'We\'re experiencing technical difficulties, salaries will be paid next month'
	sleep(ONE_MONTH)


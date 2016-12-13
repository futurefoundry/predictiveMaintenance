import time
import RPi.GPIO as GPIO
import os
import sys
#initialise a previous input variable to 0 (assume button not pressed last)
prev_input = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)
time.sleep (2)
print '\033[1;32;40mPress Button to Start Program.'

while True:
  #take a reading
  input = GPIO.input(4)
  #if the last reading was low and this one high
  if ((not prev_input) and input):
	print 'Launching Program. Please Wait...'
	os.system("lxterminal -e 'bash -c \"exec python /home/pi/adxl345-python/predictiveMaintenance.py; exec bash\"'")
	time.sleep(3)
	sys.exit()
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.01)

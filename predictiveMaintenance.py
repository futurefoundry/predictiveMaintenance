#import the adxl345 libraries

from ubidots import ApiClient
import adxl345
import RPi.GPIO as GPIO
import adxl345_2
import time
import subprocess
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
print ' '
print ('\033[1;32;40mStarting Predictive Maintenance Scheduler...')
print ' '
time.sleep(2)
buttonPin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPin,GPIO.IN)

#create ADXL345 objects

accel = adxl345.ADXL345()
accel2 = adxl345_2.ADXL345_2()
X_1=[]
Y_1=[]
Z_1=[]
X_2=[]
Y_2=[]
Z_2=[]
i=0
j=0

#Get vibration data from accelerometers

print ('Detecting Machine Vibrations...')
print ' '
while i<10000:
        axes_1 = accel.getAxes(True)
	axes_2 = accel2.getAxes(True)
        X_1.append(axes_1['x'])
        Y_1.append(axes_1['y'])
        Z_1.append(axes_1['z'])
	X_2.append(axes_2['x'])
        Y_2.append(axes_2['y'])
        Z_2.append(axes_2['z'])
        i=i+1

#Define FFT parameters

Fs = 1000.0;  # sampling rate
Ts = 1.0/Fs; # sampling interval
n = len(Y_1) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = frq[range(n/2)] #one side frequency range
frq = np.delete(frq, [0]) #deleting first erroneous element
print ('Computing FFT from vibration data...')
print ' '
time.sleep(2)

#FFT for first module

A = np.fft.fft(Y_1)
A /= np.sqrt(len(A)) # fft computing and normalization
A = A[range(n/2)]
A = np.delete(A, [0])
freqs_1 = np.fft.fftfreq(len(A))
max_1 = max(np.abs(A))
idx_1 = np.argmax(np.abs(A))
freq_1 = freqs_1[idx_1]
freq_in_Hertz_1 = freq_1 * Fs/2

#FFT for second module

B = np.fft.fft(Y_2)
B /= np.sqrt(len(B)) # fft computing and normalization
B = B[range(n/2)]
B = np.delete(B, [0])
freqs_2 = np.fft.fftfreq(len(B))
max_2 = max(np.abs(B))
idx_2 = np.argmax(np.abs(B))
freq_2 = freqs_2[idx_2]
freq_in_Hertz_2 = freq_2 * Fs/2
if max_1>4:
   m1_state=1
elif max_1<=4:
   m1_state=0
if max_2>4:
   m2_state=1
elif max_2<=4:
   m2_state=0

#Customize plot 1

fig1 = plt.figure(facecolor='white')
thismanager = plt.get_current_fig_manager()
thismanager.window.wm_geometry("683x768+0+0")
plt.gca().set_axis_bgcolor('black')
plt.grid(color='cyan')
plt.xlabel('Frequency (Hz)\nPress Button to open Ubidots IoT Cloud Server.')
plt.ylabel('Acceleration (G)')
plt.title('Frequency Response of Machine 1')
plt.locator_params(axis='x',nbins=10)
plt.locator_params(axis='y',nbins=5)
ax1 = fig1.add_subplot(111)

#Customize plot 2

fig2 = plt.figure(facecolor='white')
thismanager = plt.get_current_fig_manager()
thismanager.window.wm_geometry("683x768+683+0")
plt.gca().set_axis_bgcolor('black')
plt.grid(color='cyan')
plt.xlabel('Frequency (Hz)\nPress Button to open Ubidots IoT Cloud Server.')
plt.ylabel('Acceleration (G)')
plt.title('Frequency Response of Machine 2')
plt.locator_params(axis='x',nbins=10)
plt.locator_params(axis='y',nbins=5)
ax2 = fig2.add_subplot(111)
#pos1 = ax1.get_position() # get the original position 
#pos2 = [pos1.x0-0.07, pos1.y0, pos1.width*1.1, pos1.height] 
#ax1.set_position(pos2) # set a new position

#Upload to Ubidots

api = ApiClient("a5ea0f6d791efe4ef8e2d78132432818faa934c6")
M1_amplitude = api.get_variable("579b55e87625420b88d9f711")
M2_amplitude = api.get_variable("579b55ec7625420bb919e882")
M1_frequency = api.get_variable("579b56307625420ed333f19a")
M2_frequency = api.get_variable("579b563c7625420f2a45bc31")
M1_status = api.get_variable("57a99a087625424fdb21578d")
M2_status = api.get_variable("57a99a1476254250f61dc14e")
print 'Connected to Internet...'
print ' '
M1_amplitude.save_value({"value": max_1})
M2_amplitude.save_value({"value": max_2})
M1_frequency.save_value({"value": freq_in_Hertz_1})
M2_frequency.save_value({"value": freq_in_Hertz_2})
M1_status.save_value({"value": m1_state})
M2_status.save_value({"value": m2_state})
print 'Uploading Data to Cloud...'
print ' '

time.sleep(2)

#Plot data

print 'Plotting Data...'
print ' '
time.sleep(2)
ax1.plot(frq, abs(A), 'cyan')
ax2.plot(frq, abs(B), 'cyan')
fig1.canvas.draw()
fig2.canvas.draw()
plt.show(block=False)

prev_input = 0
flag = 0

while True:
  #take a reading
  input = GPIO.input(4)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
    if flag == 1:
      os.system("lxterminal -e 'bash -c \"exec python /home/pi/adxl345-python/launch.py; exec bash\"'")
      p.kill()
      sys.exit()
    elif flag == 0:
      p = subprocess.Popen(["chromium-browser"])
      flag = 1
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.01)

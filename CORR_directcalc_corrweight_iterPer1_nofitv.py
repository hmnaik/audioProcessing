###########################
#
# Initally USED:
# Python rewrite of multilateration technique by André Andersen in his [blog post](http://blog.andersen.im/2012/07/signal-emitter-positioning-using-multilateration).
# https://stackoverflow.com/questions/31098228/solving-system-using-linalg-with-constraints
# https://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html
#
# author: Mate Nagy
#
############################

import numpy as np
from numpy.linalg import *
import scipy.optimize as optimize
import json
import csv
from collections import defaultdict
import sys

## For the optimisation to work correctly it is good to choose the units of space and time that values are 
## in the similar order of magnitude. So here we use m (meters) for distance, and cs (centiseconds) for time.
## Speed of sound will be similar values as well (around 3.40 m/cs)
#speed of sound in medium
v0 = 3.40000	# 345000mm/s = 3.45 m/cs
vReal  = 3.40000	# fit between 310 m/s and 350 m/s for speed of sound
vStep =  0.0001
vHalfRange = 0.01	#0.3
numOfDimensions = 3
#nSensors = 20
region = 10	# 3000 mm = 3 m
sensorRegion = 1	# 2000 mm = 2 m

xmin = -4
xmax = 4
ymin = -8
ymax = 8
zmin = 0
zmax = 3.5	#3.5

# choose a random sensor location for testing
#emitterLocation = region * ( np.random.random_sample(numOfDimensions) - 0.5 )
#sensorLocations = [ sensorRegion * ( np.random.random_sample(numOfDimensions)-0.5 ) for n in range(nSensors) ]
#for i in range(nSensors):
#	# sensors are on the "ceiling", in one plane z=2*sensorRegion

#	sensorLocations[i][2] = 0.0000001 * sensorLocations[i][2] + 2.0 * sensorRegion

micLocation = defaultdict(dict)
# REad microphone positions
with open("micpos.csv", 'r') as file:
	csvreader = csv.reader(file)
	#header = next(csvreader)
	for row in csvreader:
		micLocation[row[0]] = [row[i] for i in range(1,4)]


# Read data from file
timing = defaultdict(dict)
tstart = defaultdict(dict)
corrfocal = defaultdict(dict)
loudestChannel = defaultdict(dict)

# if len(sys.argv) < 2:
# 	print("Give input file as argument")
# 	exit(-1)
# else:
# 	file = str(sys.argv[1])	# "updated_dataBase_11-15.csv"

file = "correlation.csv"


with open(file, 'r') as file:
	csvreader = csv.reader(file)
	header = next(csvreader)
	for row in csvreader:
		timestamp = row[2] + "-" + row[3] + "-" + row[4] + "_" + row[5] + "-" + row[6] + "-" + row[7]
		channel = row[1]
		timing[timestamp][channel] = row[11]	#time in sample
		corrfocal[timestamp][channel] = row[10]	#correlation value with the focal channel
		if int(row[11])== 0:
			tstart[timestamp] = row[9]
			loudestChannel[timestamp] = row[1]

print("#timestamp\tvStart(m/s)\tx(mm)\ty(mm)\tz(mm)\tt0(s)\tdt0(s)\tv(m/s)\tGoodnessOfFit/n\tnUsed\tLoudestChannel")

#### FIT function to be optimised (least squares for distance travell and the time diff)

def f(x):
	t0 = x[3]
	v2Fit = vReal**2	#x[4]	# v square
	# weight with the correlation value
	#y = signalCorr[c] * ( ((p[0,c]-x[0])**2 + (p[1,c]-x[1])**2 + (p[2,c]-x[2])**2 - v2Fit * (t[c] - t0)**2)**2 )
	y =  ( ((p[0,c]-x[0])**2 + (p[1,c]-x[1])**2 + (p[2,c]-x[2])**2 - v2Fit * (t[c] - t0)**2)**2 )
	for i in ijs:
		#y+= signalCorr[i] * ( ((p[0,i]-x[0])**2 + (p[1,i]-x[1])**2 + (p[2,i]-x[2])**2 - v2Fit * (t[i] - t0)**2)**2 )
		y+= ( ((p[0,i]-x[0])**2 + (p[1,i]-x[1])**2 + (p[2,i]-x[2])**2 - v2Fit * (t[i] - t0)**2)**2 )
	return y

def dist1(i,x):
	t0 = x[3]
	#vFit = x[4]
	y=np.sqrt( (p[0,i]-x[0])**2 + (p[1,i]-x[1])**2 + (p[2,i]-x[2])**2 )
	return y

for timestamp, value in timing.items():
	ts = float(tstart[timestamp])/1000.0	# convert to cs
	# RUN THE FITTING
	nSensors = 0
	sensorT = []
	sensorL = []
	signalC = []
	for channel, value2 in value.items():
		#print("timestamp: %s channel: %s value2: %s" %(timestamp, channel, value2))

		sensorT.append(value2)
		sensorL.append(micLocation[channel])
		signalC.append(corrfocal[timestamp][channel])
		nSensors += 1

	# IMPORTANT:
	sensorT=np.asfarray(sensorT,float)/1000.0	# convert from sample (100,000 sample = 1s) to cs
	sensorL=np.asfarray(sensorL,float)/1000.0	# convert from mm to m
	signalC=np.asfarray(signalC,float)
	signalCorr = [ corr for corr in signalC ]
	sensorTimes = [ time + ts for time in sensorT ]
	sensorLocations = [ sensorRegion * ( np.random.random_sample(numOfDimensions)-0.5 ) for n in range(nSensors) ]	#small perturbation, if needed

	for i in range(nSensors):
		for j in range(numOfDimensions):
			sensorLocations[i][j] = 0.0000001 * sensorLocations[i][j] + 1.0 * sensorL[i][j]
	##print(sensorTimes)
	##print(sensorLocations)
	##print(nSensors)
	
	p = np.matrix( sensorLocations ).T

	#Time from emitter to each sensor
	#sensorTimes = [ np.sqrt( np.dot(location-emitterLocation,location-emitterLocation) ) / v0 for location in sensorLocations ]

	c = np.argmin(sensorTimes)
	cTime = sensorTimes[c]

	#sensors delta time relative to sensor c
	t = sensorDeltaTimes = [ sensorTime - cTime for sensorTime in sensorTimes ]
	#print("t: %s" % t)

	ijs = list(range(nSensors))
	del ijs[c]

	#print("closest: %s" % c)
	#print("location: %s" % p[:,c])

	#print("Emitter location: %s , time: %s, v: %s" % (emitterLocation, -cTime, v0))


	# vary v
	v = vReal - vHalfRange/100.0
	#for v in range(vReal - vHalfRange, vReal + vHalfRange, vStep):
	GoF_toStop = 100
	GoF = GoF_toStop * 10
	minSen_toStop = 10	#21 if all should be used
	line = ""
	while v <= vReal + vHalfRange/100.0 and GoF > GoF_toStop and len(ijs) > minSen_toStop:


		cons = []
		cons.append({'type': 'ineq', 'fun':  lambda x: -x[3]})

		bnds = ((xmin,xmax),(ymin,ymax),(zmin,zmax),(-10.0*region/v0,0),)
		x_start = [0.1,0.1,0.1,-0.1]

		res = optimize.minimize(f, x_start, method='SLSQP', tol=1e-10, bounds=bnds, constraints=cons)
		#res = optimize.minimize(f, x_start, bounds=bnds)

		xbest = res['x']

		#print("v, %s, Calculated position of emitter: %s , Function: %s" % (v, xbest, f(xbest)))

		#print("%s\t%s" % (xbest[0]*1000.0, xbest[0]*1000.0) )
		line = "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.8f\t%.8f\tFIXED\t%s\t%s\t%s" % (timestamp, \
		   v*100.0, \
		   xbest[0]*1000.0, xbest[1]*1000.0, xbest[2]*1000.0, \
		   (xbest[3]+cTime)/100.0, (xbest[3])/100.0, \
		   f(xbest)/len(ijs), len(ijs),\
		   loudestChannel[timestamp])

		GoF = f(xbest)	# GoodnessOfFit, or rather residual from the least square fit.

		# ITERATIONS
		min_i = 0
		min = 1000
		max_i = 0
		max = 0
		sum = 0
		num = 0
		for i in ijs:
			dist = dist1(i,xbest)
			time = t[i]-xbest[3]
			if time > 0:
				vNow = dist/time
				sum += vNow
				num += 1
				if vNow < min:
					min = vNow
					min_i = i
				if vNow > max:
					max = vNow
					max_i = i
	
			#print(" i: %s dist(m): %s time(cs): %s vNow(m/cs): %s" %(i, dist, time, vNow))
		##print("min_i: %s max_i: %s" %(min_i, max_i))
		#print("%s" % ijs)
		mean = sum/num
		if (mean - min) > (max - mean):
			ijs.remove(min_i)
		else:
			ijs.remove(max_i)


		v += vStep/100.0
	print(line)

###########################
#
# get position and timing of the localised sounds, and get location and distance of all individuals (vicon marker patterns on the back)
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

dir="../../../12starling"

#micLocation = defaultdict(dict)
#with open("gettracks_7th.csv", 'r') as file:
#	csvreader = csv.reader(file)
#	header = next(csvreader)
#	for row in csvreader:
#		micLocation[row[0]] = [row[i] for i in range(1,4)]


# Read data from file
# read time and location of sound, vicon data file and timestamp (frame number)
sound_loc = defaultdict(dict)
sound_fullline = defaultdict(dict)
out_fullline = defaultdict(dict)
vicon_filename = defaultdict(dict)
vicon_frame = defaultdict(dict)
vicon_uniquefiles = []

if len(sys.argv) < 2:
	print("Give input file as argument")
	exit(-1)
else:
	file = str(sys.argv[1])	# "updated_dataBase_11-15.csv"


with open(file, 'r') as file:
	csvreader = csv.reader(file)
	header = next(csvreader)
	for row in csvreader:
		timestamp = row[0]
		sound_loc[timestamp] = [row[i] for i in range(2,5)]
		sound_fullline[timestamp] = row
		out_fullline[timestamp] = row
		filename = row[19]
		vicon_filename[timestamp] = filename
		vicon_frame[timestamp] = row[21]
		if filename not in vicon_uniquefiles:
			vicon_uniquefiles.append(filename)

#print(header)
#exit(0)

#### FIT function to be optimised (least squares for distance travell and the time diff)


def dist1(x,y):
	dist=np.sqrt( (x[0]-y[0])**2 + (x[1]-y[1])**2 + (z[2]-z[2])**2 )
	return dist

def dist_horizontal(x,y):
	dist=np.sqrt( (x[0]-y[0])**2 + (x[1]-y[1])**2 )
	return dist

uniqueIDs = []
viconXYZ = defaultdict(dict)
viconRXYZW = defaultdict(dict)
vicon_line = defaultdict(dict)
for filename in vicon_uniquefiles:
	#print(filename)
	for timestamp, value in sound_loc.items():
		#print(timestamp)
		if filename == vicon_filename[timestamp]:

			with open(dir+"/"+filename, 'r') as file:
				csvreader = csv.reader(file)
				header2 = next(csvreader)
				for row in csvreader:
					frame = row[0]
					if frame == vicon_frame[timestamp]:
						ID = row[1]
						viconRXYZW[timestamp][ID] = [row[i] for i in range(2,6)]
						viconXYZ[timestamp][ID] = [row[i] for i in range(6,9)]
						vicon_line[timestamp][ID] = row
						if ID not in uniqueIDs:
							uniqueIDs.append(ID)
						#print(row)
						#out_fullline[timestamp].append(row)
headerline = []
headerline.append(header)
for ID in uniqueIDs:
	headerline.append(header2)
print(headerline)

for timestamp, value in sound_fullline.items():
	line = []
	line.append(sound_fullline[timestamp])
	for ID in uniqueIDs:
		try:
			val = vicon_line[timestamp][ID]
		except KeyError:
			val = [""] * 9
		line.append(val)
	print(line)
exit(-1)

if(0):
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

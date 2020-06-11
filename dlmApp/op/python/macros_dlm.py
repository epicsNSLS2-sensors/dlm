#!/bin/env python

# examples of recorded macros, and recorded macros that have been edited
# to use arguments

import os
import time
import epics
import math

# The function "_abort" is special: it's used by caputRecorder.py to abort an
# executing macro
def _abort(prefix):
	print "%s.py: _abort() prefix=%s" % (__name__, prefix)
	epics.caput(prefix+"AbortScans", "1")

# Support for Yokogawa DLM4000 scope
# scope commands are in the manual IMDLM4038-17EN.pdf (DLM4000 Series Mixed Signal Oscilloscope
# Communication Interface User's Manual).
# Note record length is quantized: # 1250, 12500, 125000, and others that we don't support.

def _bestTimePerDiv(desiredTimePerDiv):
	minDiff = 1000000000
	nearest = 500
	for j in range(10,-10,-1):
		for i in [1,2,5]:
			timePerDiv = i*10**j
			diff = desiredTimePerDiv - timePerDiv
			if (diff >= 0) and (abs(diff) < minDiff):
				minDiff = diff
				nearest = timePerDiv
	print "nearest", nearest
	return(nearest)

def dlm(numAvg=1, numPts=1250000, nBins=4000, driveFreq=135777., format='word', traces=2, maxScopeAvg=8,debug=0):
	recordDate = "Tue Dec  1 15:24:21 2015"
	startTime = time.time()
	prefix = "dlm:"

	# this code has a bug that is exposed when maxScopeAvg==1 and numAvg>1.  For now...
	if numAvg>1 and maxScopeAvg<2:
		maxScopeAvg=2
		print "macros_dlm.py: dlm(): maxScopeAvg set to 2 to avoid a bug in this code"

	if traces>4:
		traces = 4
		print "database can only do four traces"
	if traces < 2:
		traces = 2
		print "min traces is 2"
	if format=='word':
		divisor = 3200
		bytesPerValue = 2
	else:
		divisor = 12.5
		bytesPerValue = 1
	headerBytes = 20 # more than it should ever be
	expectedBytes = numPts * bytesPerValue + headerBytes
	asynIMAX = epics.caget(prefix+"dlm:asyn.IMAX")
	if (expectedBytes > asynIMAX):
		numPts = (asynIMAX - headerBytes) / bytesPerValue
		print "numPts clipped at %d (asyn.IMAX)" % numPts

	# number of points in scope trace
	rLen = 12500
	if numPts > 12500:
		rLen = 125000
	if numPts > 125000:
		rLen = 1250000
	if numPts > rLen:
		numPts = rLen
		print "numPts clipped at %d (scope record length)" % numPts

	numSweeps = 1
	scopeAvgClosest = numAvg
	if scopeAvgClosest>maxScopeAvg: scopeAvgClosest=maxScopeAvg
	if numAvg > 1 and scopeAvgClosest>1:
		exp = 0
		for i in range(0,11):
			if debug: print "i=%d, 2**i=%f, numAvg=%f" % (i, 2**i, numAvg)
			if (2**i >= numAvg) and (2**i <= maxScopeAvg):
				if debug: print "2**i >= numAvg"
				exp = i
				scopeAvgClosest = 2**exp
				break
	if debug: print "scopeAvgClosest=", scopeAvgClosest

	# Allow user to control how much averaging happend in the scope, where the dynamic
	# range is limited
	if maxScopeAvg>1024: maxScopeAvg=1024
	if scopeAvgClosest>maxScopeAvg: scopeAvgClosest=maxScopeAvg

	# Must be in single trigger mode for linear averaging; otherwise exponential averaging.
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	if scopeAvgClosest>1:
		epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:MODE AVER", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:AVER:COUNT %d" % scopeAvgClosest, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:AVER:COUNT?", wait=True, timeout=1000000.0)
		actualScopeAverage = epics.caget(prefix+"dlm:asyn.TINP")
		actualScopeAverage = int(actualScopeAverage.rstrip("\\n"))
		#print "actualScopeAverage=", actualScopeAverage
		numSweeps = max(1,int(math.ceil(1.*numAvg/actualScopeAverage)))
	else:
		if debug: print ":ACQ:MODE NORM"
		epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:MODE NORM", wait=True, timeout=1000000.0)
		numSweeps = numAvg
		actualScopeAverage = 1

	#print "numSweeps=", numSweeps
	epics.caput(prefix+"dlm:actualNumAvg", numSweeps*actualScopeAverage, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:numScopeAvg", actualScopeAverage, wait=True, timeout=1000000.0)


	### set EPICS records for numPts, voltage range and offset, conversion divisor
	epics.caput(prefix+"dlm:acalcSyncVoltage.NUSE", numPts)
	epics.caput(prefix+"dlm:acalcTime.NUSE", numPts)
	for traceNum in range(1,traces+1):
		acalcRecord = prefix+"dlm:acalc%1d" % traceNum
		epics.caput(acalcRecord+".NUSE", numPts)

	epics.caput(prefix+"dlm:asyn.IFMT","Hybrid", wait=True, timeout=1000000.0)

	# Set scope communication behavior
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	# just the data, please, don't echo the command
	epics.caput(prefix+"dlm:asyn.AOUT",":COMM:HEADER 0", wait=True, timeout=1000000.0)

	# Set timePerDiv to get >= nBins at driveFreq
	#desiredAcqRate = nBins*float(driveFreq)
	#desiredTimePerDiv = (rLen/desiredAcqRate)/10.
	#nBins = desiredAcqRate/float(driveFreq)
	#desiredAcqRate = rLen/(desiredTimePerDiv*10)
	#nBins = rLen/(desiredTimePerDiv*10*float(driveFreq))

	for e in range(2,-9,-1):
		for t in [5,2,1]:
			desiredTimePerDiv = t*10**e
			n = rLen/(desiredTimePerDiv*10*float(driveFreq))
			#print "n=%d, nBins=%d" % (n, nBins)
			if n > nBins:
				#print "n>nBins"
				break
		if n > nBins:
			break
	epics.caput(prefix+"dlm:nBins", n, wait=True, timeout=1000000.0)
	#print "timePerDiv: desired:%g" % desiredTimePerDiv

	# timePerDiv
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:TDIV %g" % desiredTimePerDiv, wait=True, timeout=1000000.0)

	epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:TDIV?", wait=True, timeout=1000000.0)
	timePerDiv = epics.caget(prefix+"dlm:asyn.TINP")
	timePerDiv = float(timePerDiv.rstrip("\\n"))
	epics.caput(prefix+"dlm:scopeTimePerDiv",timePerDiv, wait=True, timeout=1000000.0)
	#print "timePerDiv: desired:%g, actual:%10g" % (desiredTimePerDiv, timePerDiv)
	acqRate = rLen/(timePerDiv*10)
	nBins = acqRate/float(driveFreq)
	#print "acqRate=%g, nBins=%d\n" % (acqRate, nBins)



	### Get scope parameters
	epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
	# trigger level
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIG:LEVEL?", wait=True, timeout=1000000.0)
	triggerLevel = epics.caget(prefix+"dlm:asyn.TINP")
	triggerLevel = float(triggerLevel.rstrip("\\n"))
	epics.caput(prefix+"dlm:scopeTriggerLevel",triggerLevel, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:sumSub.G", triggerLevel, wait=True, timeout=1000000.0)

	# trigger slope
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIG:SLOPE?", wait=True, timeout=1000000.0)
	triggerSlope = epics.caget(prefix+"dlm:asyn.TINP")
	triggerSlope = triggerSlope.rstrip("\\n")
	epics.caput(prefix+"dlm:scopeTriggerSlope",triggerSlope, wait=True, timeout=1000000.0)

	# timePerDiv
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:TDIV?", wait=True, timeout=1000000.0)
	timePerDiv = epics.caget(prefix+"dlm:asyn.TINP")
	timePerDiv = float(timePerDiv.rstrip("\\n"))
	epics.caput(prefix+"dlm:scopeTimePerDiv",timePerDiv, wait=True, timeout=1000000.0)

	# dataAcqTime
	dataAcqTime = timePerDiv * 10. * actualScopeAverage * numSweeps
	epics.caput(prefix+"dlm:dataAcqTime",dataAcqTime, wait=True, timeout=1000000.0)

	# volts/div
	for i in range(1,traces+1):
		command = ":CHANNEL%d:VAR?" % i
		epics.caput(prefix+"dlm:asyn.AOUT",command, wait=True, timeout=1000000.0)
		voltsPerDiv = epics.caget(prefix+"dlm:asyn.TINP")
		voltsPerDiv = float(voltsPerDiv.rstrip("\\n"))
		PVname = prefix+"dlm:scopeCh%dVoltsPerDiv" % i
		epics.caput(PVname,voltsPerDiv, wait=True, timeout=1000000.0)
	
	# sample rate
	epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:SRATE?", wait=True, timeout=1000000.0)
	sampleRate = epics.caget(prefix+"dlm:asyn.TINP")
	sampleRate = float(sampleRate.rstrip("\\n"))
	epics.caput(prefix+"dlm:acalcTime.A", sampleRate, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:scopeSampleRate", sampleRate, wait=True, timeout=1000000.0)

	### Set scope for measurement
	# Make scope trigger on channel 1
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIGGER:SIMPLE:SOURCE 1", wait=True, timeout=1000000.0)

	#print "rLen = %d" % rLen
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:RLEN %d" % rLen, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:BYT LSBF", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:END %d" % numPts, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:FORM %s" % format, wait=True, timeout=1000000.0)
	
	### set EPICS records for voltage range and offset, conversion divisor
	for traceNum in range(1,traces+1):
		acalcRecord = prefix+"dlm:acalc%1d" % traceNum
		
		# range (volts/division)
		epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:TRAC %d" % traceNum, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:RANGE?", wait=True, timeout=1000000.0)
		voltRange = epics.caget(prefix+"dlm:asyn.TINP")
		voltRange = float(voltRange.rstrip("\\n"))
		epics.caput(acalcRecord+".A", voltRange)

		# offset
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:OFFSET?", wait=True, timeout=1000000.0)
		offset = epics.caget(prefix+"dlm:asyn.TINP")
		offset = float(offset.rstrip("\\n"))
		epics.caput(acalcRecord+".B", offset)
		
		# conversion divisor (depends on format byte/word)
		epics.caput(acalcRecord+".C", divisor) 

	### acquire data

	epics.caput(prefix+"dlm:numSweeps", numSweeps)
	epics.caput(prefix+"dlm:eraseSums", 1)
	for sweep in range(numSweeps):
		epics.caput(prefix+"dlm:currSweep",sweep)
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.TMOT", 1000, wait=True, timeout=1000000.0)
		# start acquisition and wait up to 1000 seconds for it to finish
		# wait time is in tenths of a second
		acqStartTime = time.time()
		epics.caput(prefix+"dlm:asyn.AOUT",":SSTART? 10000", wait=True, timeout=1000000.0)
		if debug: print "sent ':SSTART? 10000'"
		done = False
		retVal = epics.caget(prefix+"dlm:asyn.TINP")
		retVal = retVal.rstrip("\\n")
		if debug: print "retVal='%s'" % retVal
		if retVal == '0':
			done = True
		while not done:
			time.sleep (0.1)
			epics.caput(prefix+"dlm:asyn.TMOD","Read", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.PROC", 0, wait=True, timeout=1000000.0)
			retVal = epics.caget(prefix+"dlm:asyn.TINP")
			retVal = retVal.rstrip("\\n")
			if debug>2: print "retVal='%s'" % retVal
			if retVal == '0':
				done = True
		if debug: print "acq done"
		acqEndTime = time.time()

		### read data from scope into asyn record; drive aSub record to read from asyn record
		# and convert data; drive per-trace acalcout records to read from aSub and convert to volts.
		epics.caput(prefix+"dlm:aSub.B", bytesPerValue)

		# tell acalcSum<n> records which sweep this is
		for i in range(2,traces+1):
			acalcRecord = prefix+"dlm:acalcSum%1d" % traceNum
			epics.caput(acalcRecord+".A", sweep, wait=True, timeout=1000000.0)

		for traceNum in range(1,traces+1):
			acalcRecord = prefix+"dlm:acalc%1d" % traceNum

			# Read scope data into asyn record
			epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
			# this command gets a code 410 error on the second sweep at traceNum==2, but only
			# with maxAvg==1
			epics.caput(prefix+"dlm:asyn.AOUT",":WAV:TRAC %d" % traceNum, wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.NRRD", expectedBytes, wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.IFMT","Binary", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.AOUT",":WAV:SEND? %d" % numPts, wait=True, timeout=1000000.0)
			# convert data to array of epicsInt16
			epics.caput(prefix+"dlm:aSub.PROC", 0, wait=True, timeout=1000000.0)

			# read data into this trace's acalcout record, and convert to volts
			epics.caput(acalcRecord+".PROC", 0, wait=True, timeout=1000000.0)

		# drive sumSub to sum all traces over periods
		epics.caput(prefix+"dlm:sumSub.PROC", 0, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:acalcSum2.PROC", 0, wait=True, timeout=1000000.0)
		if traces>2:
			epics.caput(prefix+"dlm:acalcSum3.PROC", 0, wait=True, timeout=1000000.0)
		if traces>3:
			epics.caput(prefix+"dlm:acalcSum4.PROC", 0, wait=True, timeout=1000000.0)
		procEndTime = time.time()
		
		if debug: print "acquire/process time %f %f" % (acqEndTime-acqStartTime, procEndTime-acqEndTime)
		epics.caput(prefix+"dlm:currSweep",sweep+1)
		epics.caput(prefix+"dlm:trigPlots", 1, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:eraseSums", 0)

	endTime = time.time()
	totalTime = endTime-startTime
	epics.caput(prefix+"dlm:totalTime", totalTime, wait=True, timeout=1000000.0)

	# leave scope in normal mode
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:MODE NORM", wait=True, timeout=1000000.0)

# dlm from last MEMS exp't
# scope commands are in the dlm/documentation/manual IMDLM4038-17EN.pdf (DLM4000 Series Mixed
# Signal Oscilloscope Communication Interface User's Manual).
# Note record length is quantized: # 1250, 12500, 125000, and others that we don't support.

def _old_dlm(numAvg=1, numPts=12500, format='word', traces=4):
	recordDate = "Tue Dec  1 15:24:21 2015"
	prefix = "dlm:"

	if traces>4:
		traces = 4
		print "database can only do four traces"
	if traces < 2:
		traces = 2
		print "min traces is 2"
	if format=='word':
		divisor = 3200
		bytesPerValue = 2
	else:
		divisor = 12.5
		bytesPerValue = 1
	headerBytes = 20 # more than it should ever be
	expectedBytes = numPts * bytesPerValue + headerBytes
	asynIMAX = epics.caget(prefix+"dlm:asyn.IMAX")
	if (expectedBytes > asynIMAX):
		numPts = (asynIMAX - headerBytes) / bytesPerValue
		print "numPts clipped at %d (asyn.IMAX)" % numPts

	rLen = 12500
	if numPts > 12500:
		rLen = 125000
	if numPts > rLen:
		numPts = rLen
		print "numPts clipped at %d (scope record length)" % numPts

	# numAvg is limited by record length and number of traces
	# For 12500-byte buffer, numAvg<=767; for 125000, numAvg<=191 (one trace)
	# For 12500-byte buffer, numAvg<=383; for 125000, numAvg<=191 (four traces)
	numSweeps = 1
	numAvgClipped = numAvg
	if rLen==12500:
		if traces==1:
			if numAvg>767:
				numAvgClipped = 767
		else:
			if numAvg>383:
				numAvgClipped = 383
	else:
		if numAvg>191:
			numAvgClipped = 191
	numSweeps = int(math.ceil(numAvg/numAvgClipped))
	#print "numSweeps=", numSweeps
	
	epics.caput(prefix+"dlm:asyn.IFMT","Hybrid", wait=True, timeout=1000000.0)

	# Set scope communication behavior
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	# just the data, please, don't echo the command
	epics.caput(prefix+"dlm:asyn.AOUT",":COMM:HEADER 0", wait=True, timeout=1000000.0)

	### Get scope parameters
	epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
	# trigger level
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIG:LEVEL?", wait=True, timeout=1000000.0)
	triggerLevel = epics.caget(prefix+"dlm:asyn.TINP")
	triggerLevel = float(triggerLevel.rstrip("\\n"))
	epics.caput(prefix+"dlm:scopeTriggerLevel",triggerLevel, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:sumSub.G", triggerLevel, wait=True, timeout=1000000.0)

	# trigger slope
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIG:SLOPE?", wait=True, timeout=1000000.0)
	triggerSlope = epics.caget(prefix+"dlm:asyn.TINP")
	triggerSlope = triggerSlope.rstrip("\\n")
	epics.caput(prefix+"dlm:scopeTriggerSlope",triggerSlope, wait=True, timeout=1000000.0)

	# timePerDiv
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:TDIV?", wait=True, timeout=1000000.0)
	timePerDiv = epics.caget(prefix+"dlm:asyn.TINP")
	timePerDiv = float(timePerDiv.rstrip("\\n"))
	epics.caput(prefix+"dlm:scopeTimePerDiv",timePerDiv, wait=True, timeout=1000000.0)

	# volts/div
	for i in range(1,traces+1):
		command = ":CHANNEL%d:VAR?" % i
		epics.caput(prefix+"dlm:asyn.AOUT",command, wait=True, timeout=1000000.0)
		voltsPerDiv = epics.caget(prefix+"dlm:asyn.TINP")
		voltsPerDiv = float(voltsPerDiv.rstrip("\\n"))
		PVname = prefix+"dlm:scopeCh%dVoltsPerDiv" % i
		epics.caput(PVname,voltsPerDiv, wait=True, timeout=1000000.0)
	
	# sample rate
	epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":TIME:SRATE?", wait=True, timeout=1000000.0)
	sampleRate = epics.caget(prefix+"dlm:asyn.TINP")
	sampleRate = float(sampleRate.rstrip("\\n"))
	epics.caput(prefix+"dlm:acalcTime.A", sampleRate, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:scopeSampleRate", sampleRate, wait=True, timeout=1000000.0)

	### Set scope for measurement
	# Make scope trigger on channel 1
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":TRIGGER:SIMPLE:SOURCE 1", wait=True, timeout=1000000.0)

	#print "rLen = %d" % rLen
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:RLEN %d" % rLen, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:BYT LSBF", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:END %d" % numPts, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":WAV:FORM %s" % format, wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:COUNT %d" % numAvgClipped, wait=True, timeout=1000000.0)
	
	### set EPICS records for numPts, voltage range and offset, conversion divisor
	epics.caput(prefix+"dlm:acalcSyncVoltage.NUSE", numPts)
	for traceNum in range(1,traces+1):
		acalcRecord = prefix+"dlm:acalc%1d" % traceNum
		
		# numPts
		epics.caput(acalcRecord+".NUSE", numPts)

		# range (volts/division)
		epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:TRAC %d" % traceNum, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:RANGE?", wait=True, timeout=1000000.0)
		voltRange = epics.caget(prefix+"dlm:asyn.TINP")
		voltRange = float(voltRange.rstrip("\\n"))
		epics.caput(acalcRecord+".A", voltRange)

		# offset
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:asyn.AOUT",":WAV:OFFSET?", wait=True, timeout=1000000.0)
		offset = epics.caget(prefix+"dlm:asyn.TINP")
		offset = float(offset.rstrip("\\n"))
		epics.caput(acalcRecord+".B", offset)
		
		# conversion divisor (depends on format byte/word)
		epics.caput(acalcRecord+".C", divisor) 


	### acquire data

	# Must be in single trigger mode for linear averaging; otherwise exponential averaging.
	epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:MODE AVER", wait=True, timeout=1000000.0)
	epics.caput(prefix+"dlm:asyn.AOUT",":ACQ:AVER:COUNT %d" % numAvgClipped, wait=True, timeout=1000000.0)

	epics.caput(prefix+"dlm:numSweeps",numSweeps)
	for sweep in range(numSweeps):
		epics.caput(prefix+"dlm:currSweep",sweep)
		epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
		# start acquisition and wait up to 10 seconds for it to finish
		# wait time is in tenths of a second
		acqStartTime = time.time()
		epics.caput(prefix+"dlm:asyn.AOUT",":SSTART? 100", wait=True, timeout=1000000.0)
		done = False
		while not done:
			retVal = epics.caget(prefix+"dlm:asyn.TINP")
			retVal = retVal.rstrip("\\n")
			if int(retVal) == 0:
				done = True
			else:
				pass
				#print "waiting for acquisition to complete"
		#print "acq done"
		acqEndTime = time.time()

		### read data from scope into asyn record; drive aSub record to read from asyn record
		# and convert data; drive per-trace acalcout records to read from aSub and convert to volts.
		epics.caput(prefix+"dlm:aSub.B", bytesPerValue)

		# tell acalcSum<n> records which sweep this is
		for i in range(2,traces+1):
			acalcRecord = prefix+"dlm:acalcSum%1d" % traceNum
			epics.caput(acalcRecord+".A", sweep, wait=True, timeout=1000000.0)

		for traceNum in range(1,traces+1):
			acalcRecord = prefix+"dlm:acalc%1d" % traceNum

			# Read scope data into asyn record
			epics.caput(prefix+"dlm:asyn.TMOD","Write", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.AOUT",":WAV:TRAC %d" % traceNum, wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.NRRD", expectedBytes, wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.TMOD","Write/Read", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.IFMT","Binary", wait=True, timeout=1000000.0)
			epics.caput(prefix+"dlm:asyn.AOUT",":WAV:SEND? %d" % numPts, wait=True, timeout=1000000.0)
			# convert data to array of epicsInt16
			epics.caput(prefix+"dlm:aSub.PROC", 0, wait=True, timeout=1000000.0)

			# read data into this trace's acalcout record, and convert to volts
			epics.caput(acalcRecord+".PROC", 0, wait=True, timeout=1000000.0)

		# drive sumSub to sum all traces over periods
		epics.caput(prefix+"dlm:sumSub.PROC", 0, wait=True, timeout=1000000.0)
		epics.caput(prefix+"dlm:acalcSum2.PROC", 0, wait=True, timeout=1000000.0)
		if traces>2:
			epics.caput(prefix+"dlm:acalcSum3.PROC", 0, wait=True, timeout=1000000.0)
		if traces>3:
			epics.caput(prefix+"dlm:acalcSum4.PROC", 0, wait=True, timeout=1000000.0)
		procEndTime = time.time()
		
		#print "acquire/process time %f %f" % (acqEndTime-acqStartTime, procEndTime-acqEndTime)
	epics.caput(prefix+"dlm:currSweep",sweep+1)

def test(go):
	#epcis.caput("dlm:dlm:caputRecorderDelaySec",delay,wait=True,timeout=1000000.0)
	print "theta vs.delay scan"
	DG=[1,1.2,1.4,1.5]
	for ii in range(len(DG)):
		epics.caput("7idc1:DG1:ABOutputAmpAO",DG[ii],wait=True,timeout=1000000.0)
		if go==1:
			epics.caput("7idc1:scan1.PASM",7,wait=True,timeout=1000000.0)
			time.sleep(2)
			epics.caput("7idc1:scan1.EXSC",go,wait=True,timeout=1000000.0)
			epics.caput("7idc1:scan1.PASM",2,wait=True,timeout=1000000.0)
			time.sleep(2)
			print "recenter delay scan range"
			epics.caput("7idc1:scan2.EXSC",go,wait=True,timeout=1000000.0)
		time.sleep(2)
		print "scan loop %d finish"%(ii+1)
	
	print "---------------------"
	print "drift test scan, at 60 V"
	epics.caput("7idc1:DG1:ABOutputAmpAO",1.2,wait=True,timeout=1000000.0)
	epics.caput("7idc1:scan1.PASM",7,wait=True,timeout=1000000.0)
	time.sleep(1)
	epics.caput("7idc1:scan1.EXSC",go,wait=True,timeout=1000000.0)
	epics.caput("7idc1:scan1.PASM",2,wait=True,timeout=1000000.0)
	time.sleep(1)
	print "1.forward delay scan"
	pts=[51, 101, 151, 201, 251]
	for ii in range(len(pts)):
		epics.caput("7idc1:scan1.NPTS",pts[ii],wait=True,timeout=1000000.0)
		if go==1:
			epics.caput("7idc1:scan1.EXSC",go,wait=True,timeout=1000000.0)
		time.sleep(2)
		print "scan loop %d finish"%(ii+1)
	
	print "2.backward delay scan"
	epics.caput("7idc1:scan1.P1WD",-3e-8,wait=True,timeout=1000000.0)
	for ii in range(len(pts)):
		epics.caput("7idc1:scan1.NPTS",pts[ii],wait=True,timeout=1000000.0)
		if go==1:
			epics.caput("7idc1:scan1.EXSC",go,wait=True,timeout=1000000.0)
		time.sleep(2)
		print "scan loop %d finish"%(ii+1)		
	epics.caput("7idc1:DG1:ABOutputAmpAO",0.5,wait=True,timeout=1000000.0)
	
def test2():
	print "hello"
	prefix="dlm:"
	#epcis.caput(prefix+"dlm:sampleThreshold",0.1, wait=True)
	#epics.caput("dlm:dlm:nBins", 10, wait=True, timeout=1000000.0)
	#epics.caput("dlm:scan1.P1SP",.1,wait=True,timeout=1000000.0)
	#a=epics.caget("dlm:dlm:scopeTriggerLevel")
	#a=epics.caget("dlm:scanH.P1SI")
	a=epics.ca.find_libca()
	print a
	

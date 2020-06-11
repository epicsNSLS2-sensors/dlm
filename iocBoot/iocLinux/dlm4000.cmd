# To configure the scope for ethernet control, set the communication interface
# to Network (from the UTILITY menu, select Remote Control > Device > Network).
# To set the scope's IP address, select Network from the UTILITY menu, scroll
# to IP Address, use menu buttons and the SET joystick at top right. Then
# power cycle the scope.

# NB is number of samples * max bytes per value + header length of maybe 12 - let's go with 100
# N is the maximum number of scope samples
# NW is the maximum number of summed waveform points
# NH is the number of v/t 2D histogram bins
#dbLoadRecords("$(TOP)/dlmApp/Db/dlm.db","P=dlm:,Q=dlm:,R=asyn,PORT=dlmPort,N=250100, NW=100000")
dbLoadRecords("$(TOP)/dlmApp/Db/dlm.db","P=dlm:,Q=dlm:,R=asyn,PORT=dlmPort,NB=2500100,N=1250000,NW=4000,NH=40000")

#vxi11Configure("dlmPort", "192.168.110.2", 0, 0.0, "inst0", 0)
# mooney's office
#vxi11Configure("dlmPort", "164.54.53.174", 0, 0.0, "inst0", 0)
# 7id
vxi11Configure("dlmPort", "10.11.2.180", 0, 0.0, "inst0", 0)
# We don't want EOS for input, because we'll tell the scope to send binary data
#asynInterposeEosConfig(port, addr, processEosIn, processEosOut)
#asynInterposeEosConfig("dlmPort", 0, 0, 0)
#asynOctetSetInputEos("dlmPort",0,"\n")
#asynOctetSetOutputEos("dlmPort",0,"\n")


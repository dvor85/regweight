#!/usr/bin/env python

import sys,time,os,pickle
from os import path
from protocols import NVT1N

DEVICE='/dev/ttyUSB0'
BAUDRATE=9600
SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
FILTER = 200

if __name__ == "__main__":
    nvt=NVT1N(DEVICE,BAUDRATE)
    nvt.setLogger('regweight')
    nvt.setDB(SELF_PATH)
    nvt.debug=True
    last_stab_weight=0
    cnt=0
    must_dump=False
    starting=True
    nvt.log.c("STARTING...")

    #if path.isfile(DUMP_FILE):
    #    with open(DUMP_FILE,"rb") as dump:
    #        old_weight=pickle.load(dump)
    
    while True:
        try:
            cur,stab=nvt.getBRUTTO()
            if nvt.debug:
                nvt.log.d(__name__+": weight = %1.1f (%i)" % (cur,stab))
            if cur is None: continue

	    if stab:
		cnt+=1 
	    else: 
		cnt=0
		
	    if last_stab_weight-cur>FILTER:
	        if nvt.regWeight(last_stab_weight):
		    last_stab_weight=0
		
	    elif (cur>FILTER) and (cnt>2):
	        if (last_stab_weight>FILTER):
		    last_stab_weight=min(last_stab_weight,cur)
		else:
		    last_stab_weight=cur
	

            #if (sedation) and (starting) and (abs(weight-TABLE_WEIGHT)<1):
            #    continue

            #if (abs(weight)<FILTER):
            #    must_dump=not(old_weight==0)
            #    old_weight=0
            #    starting=False
            #elif (abs(weight-old_weight)<FILTER) and (not starting):
            #    if (sedation):
            #        cnt+=1
            #        if (cnt>2) and tenso.regWeight(weight):
            #            old_weight=weight
            #            must_dump=True
            #            cnt=0
            #    else:
            #        cnt=0
            #if must_dump:
            #    with open(DUMP_FILE,"wb") as dump:
            #        pickle.dump(old_weight,dump)
            #    must_dump=False
	    #old_weight=weight

        except Exception as e:
            nvt.log.e(__name__+' ERROR: %s' % e)
            continue
        finally:
            time.sleep(0.5)



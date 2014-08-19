#!/usr/bin/env python

import sys,time,os,pickle
from os import path
from db import *
from protocols import NVT1N

DEVICE='/dev/ttyUSB0'
BAUDRATE=9600
SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
FILTER = 200

if __name__ == "__main__":
    nvt=NVT1N(DEVICE,BAUDRATE)
    nvt.setLogger('regweight')
    nvt.debug=True
    db=DBreg(SELF_PATH)
    last_stab_weight=0
    cnt=0
    must_dump=False
    starting=True
    nvt.log.c("STARTING...")
    
    if path.isfile(DUMP_FILE):
        with open(DUMP_FILE,"rb") as dump:
            last_stab_weight=pickle.load(dump)

    while True:
        try:
            cur,stab=nvt.getBRUTTO()
            if (cur is None) or (cur < 0): continue

	    if nvt.debug:
                nvt.log.d(__name__+": weight = %1.1f (%i)" % (cur,stab))

	    if stab:
		cnt+=1 
	    else: 
		cnt=0
		
	    if last_stab_weight-cur>FILTER:
		if db.reg(last_stab_weight): 
		    nvt.log.d('regWeight: %s' % last_stab_weight)
		    last_stab_weight=0
		    must_dump=True
		
	    elif (cur>FILTER) and (cnt>1):
	        must_dump=(cur!=last_stab_weight)
	        if (last_stab_weight>FILTER):
		    last_stab_weight=min(last_stab_weight,cur)
		else:
		    last_stab_weight=cur
	    
            if must_dump:
                with open(DUMP_FILE,"wb") as dump:
                    pickle.dump(last_stab_weight,dump)
                must_dump=False

        except Exception as e:
            nvt.log.e(__name__+' ERROR: %s' % e)
            continue
        finally:
            time.sleep(0.5)



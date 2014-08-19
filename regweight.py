#!/usr/bin/env python

import sys,time,os,pickle
from os import path
from db import *
from protocols import Tenso

DEVICE='/dev/ttyUSB0'
BAUDRATE=38400
ADDR='\x01'
SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
TABLE_WEIGHT=107.5
FILTER = 50

if __name__ == "__main__":
    tenso=Tenso(DEVICE,BAUDRATE,ADDR)
    tenso.setLogger('regweight')
    tenso.debug=True
    db=DBreg(SELF_PATH)
    last_stab_weight=0
    cnt=0
    old=0
    starting=True
    tenso.log.c("STARTING...")
    
    if path.isfile(DUMP_FILE):
        with open(DUMP_FILE,"rb") as dump:
            old=pickle.load(dump)

    while True:
        try:
            cur,stab=tenso.getBRUTTO()
            if (cur is None) or (cur < 0): continue

	    if tenso.debug:
                tenso.log.d(__name__+": weight = %1.1f (%i)" % (cur,stab))
                
            if (stab) and (starting):
                if (abs(cur-TABLE_WEIGHT)>1):
                    starting=False
                continue

	    if stab:
		cnt+=1
	    else: 
		cnt=0
		
	    if last_stab_weight-cur>FILTER:
		if db.reg(last_stab_weight): 
		    tenso.log.d('regWeight: %s' % last_stab_weight)
		    last_stab_weight=0
		
	    elif (cur>FILTER) and (cnt>1):
	        if (last_stab_weight>FILTER):
		    last_stab_weight=min(last_stab_weight,cur)
		else:
		    last_stab_weight=cur
	    
	    if stab and (cur!=old):
		old=cur
		with open(DUMP_FILE,"wb") as dump:
                    pickle.dump(old,dump)
	

        except Exception as e:
            tenso.log.e(__name__+' ERROR: %s' % e)
            continue
        finally:
            time.sleep(0.5)



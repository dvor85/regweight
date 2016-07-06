#!/usr/bin/env python

import sys,time,os,pickle
from os import path
from db import *
import protocols
from config import *
import logger

log = logger.Logger('regweight', 'Main', logger.Logger.NOTICE)

SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')

if __name__ == "__main__":
    if TERMINAL.get('proto') == 'tenso':
        term=protocols.Tenso(TERMINAL.get('dev'), TERMINAL.get('baudrate'), TERMINAL.get('addr'))
    elif TERMINAL.get('proto') == 'nvt1n':
        term=protocols.NVT1N(TERMINAL.get('dev'), TERMINAL.get('baudrate'))
    else:
        log.e('TERMINAL.proto not defined')
        sys.exit()
        
    db=DBreg(SELF_PATH)
    last_stab_weight=0
    must_dump=False
    cnt=0
    starting=True
    log("STARTING...")
    
    try:
        if path.isfile(DUMP_FILE):
            with open(DUMP_FILE,"rb") as dump:
                last_stab_weight=pickle.load(dump)
    except Exception as e:
        log.e(e)

    while True:
        try:
            cur,stab=term.getBRUTTO()
            if (cur is None) or (cur < 0): continue

            log.d("weight = %1.1f (%i)" % (cur,stab))
                
            if (stab) and (starting):
                if (abs(cur-TERMINAL.get('table_weight', 0))>1):
                    starting=False
                continue

	    if stab:
		cnt+=1
	    else: 
		cnt=0
		
	    if last_stab_weight-cur>TERMINAL.get('filter'):
		if db.reg(last_stab_weight): 
		    log('reg Weight: %s' % last_stab_weight)
		    last_stab_weight=0
		    must_dump=True
		
	    elif (cur>TERMINAL.get('filter')) and (cnt>1):
	        must_dump=(cur!=last_stab_weight)
	        if (last_stab_weight>TERMINAL.get('filter')):
		    last_stab_weight=min(last_stab_weight,cur)
		else:
		    last_stab_weight=cur
		
	    
	    if must_dump:
		with open(DUMP_FILE,"wb") as dump:
                    pickle.dump(last_stab_weight,dump)
                must_dump=False

        except Exception as e:
            log.e(e)
            continue
        finally:
            time.sleep(0.5)



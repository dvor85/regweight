#!/usr/bin/env python

import sys,serial,time,os,pickle,re
from datetime import datetime
from os import path
from logger import *
from db import *

DEVICE='/dev/ttyUSB0'
BAUDRATE=9600
ADDR='\x01'
SELF_PATH=path.dirname(path.realpath(__file__))
LOG_PATH=path.join(SELF_PATH,'regweight')
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
TABLE_WEIGHT=0
FILTER = 200

class NVT1N:
    __SEDATION=0x02
    __OVERLOAD=0x08
    __NULL=0x01

    def __init__(self,device=DEVICE,baudrate=BAUDRATE,addr=ADDR):
        self.__ser = serial.Serial()
        self.__ser.port=device
        self.__ser.baudrate=baudrate
        self.__ser.timeout=1
        self.__ser.writeTimeout=1
        self.__addr=addr
        self.log=Logger('regweight')
        self.debug=False
        self.__pattern_kadr=re.compile('\x02(?P<data>.{8})\x6b\x67\x0d')
        self.__d=DBreg(SELF_PATH)


    def CRCMaker(self, b_input, b_crc):
        w = (b_input & 0xff) + ((b_crc & 0xff) << 8)
        for i in range(8):
            c = w & 0x8000
            w = w << 1
            if c != 0:
                w = w ^ 0x6900
        return ((w >> 8) & 0xff)

    def CRC(self,data):
        res=0;
        for b in data:
            res=self.CRCMaker(ord(b), res)
        return chr(res)

    def checkCRC(self,data):
        chk=self.CRC(data)
        return chk=='\x00'

    def query(self):
        res=None
        try:
            if self.__ser.isOpen():
                trys=0
                outlen=0
                while (outlen==0)and(trys<(self.__ser.timeout*10)):
                    trys+=1
                    outlen=self.__ser.inWaiting()
                    time.sleep(0.1)

                if outlen>0:
                    ans=self.__ser.read(outlen)

                    out_obj=self.__pattern_kadr.search(ans)
                    outdata=out_obj.group('data')
                    res=outdata if (len(outdata)>1) else None
            else:
                self.__ser.open()
        except Exception as e:
            self.log.e('query ERROR: %s' % e)
            if not ans is None:
                self.log.e('query ANSWER: %s' % "\\x".join(["%02x" % ord(x) for x in ans]))
        finally:
            #self.__ser.close()
            pass
        return res
    
    def testquery(self):
	if self.__ser.isOpen():
	    outlen=self.__ser.inWaiting()
	    if outlen>0:
		ans=self.__ser.read(outlen)
		time.sleep(0.1)
		self.log.d('hex query ANSWER: %s' % " ".join(["%02x" % ord(x) for x in ans]))
		self.log.d('ansi query answer: %s' % " ".join(["%s" % x for x in ans]))
	else:
	    self.__ser.open()

    def decodeBCD(self,bcd):
        res=["%02x" % ord(x) for x in bcd]
        res.reverse()
        return list("".join(res))



    def getBRUTTO(self):
        weight=None
        res=self.query()
        if res is None: return None,False,0
        
        con=ord(res[-1:])
        if ((con & self.__OVERLOAD) != self.__OVERLOAD):
	    weight=float(res[:-1].strip())
        return weight,((con & self.__SEDATION)==self.__SEDATION),con

    def regWeight(self,weight):
        if self.__d.reg(weight):
            self.log.d('regWeight: %s' % weight)
            return True
        else:
            self.log.d('ERROR regWeight %s: FAIL' % weight)
            return False

if __name__ == "__main__":
    nvt=NVT1N(DEVICE,BAUDRATE,ADDR)
    nvt.debug=True
    old_weight=0
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
	    #nvt.testquery()
	    #nvt.log.d(nvt.query())
            cur,stab,con=nvt.getBRUTTO()
            if nvt.debug:
                nvt.log.d(__name__+": weight = %1.1f (%i) (%x)" % (cur,stab,con))
            if cur is None: continue

		
		
	    if last_stab_weight-cur>FILTER:
		if nvt.regWeight(last_stab_weight):
		    last_stab_weight=0
		    cnt=0
			    
	    if stab:
		if cnt>2:
		    last_stab_weight=cur
		else:
		    cnt+=1
	    else:
		cnt=0
	

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
            time.sleep(1)



#!/usr/bin/env python

import sys,serial,time,os,pickle,re
from datetime import datetime
from os import path
from logger import *
from db import *

DEVICE='/dev/ttyUSB0'
BAUDRATE=38400
ADDR='\x01'
SELF_PATH=path.dirname(path.realpath(__file__))
LOG_PATH=path.join(SELF_PATH,'regweight')
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
TABLE_WEIGHT=107.5
FILTER = 50

class Tenso:
    __MINUS=0x80
    __SEDATION=0x10
    __OVERLOAD=0x08
    __SEPARATOR=0x07

    def __init__(self,device=DEVICE,baudrate=BAUDRATE,addr=ADDR):
        self.__ser = serial.Serial()
        self.__ser.port=device
        self.__ser.baudrate=baudrate
        self.__ser.timeout=1
        self.__ser.writeTimeout=1
        self.__addr=addr
        self.log=Logger('regweight')
        self.debug=False
        self.__pattern_kadr=re.compile('\xff+(?P<data>.*?)(?P<crc>\xff\xfe|[^\xff])\xff{2,}')
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

    def query(self,data):
        res=None
        d=self.__addr+data+'\x00'
        crc=self.CRC(d)
        if crc=='\xff': crc=crc+'\xfe'
        d='\xff'+d[:-1].replace('\xff','\xff\xfe')+crc+'\xff\xff'

        try:
            if self.__ser.isOpen():
                self.__ser.flushInput()
                self.__ser.write(d)
                self.__ser.flush()
                trys=0
                outlen=0
                while (outlen==0)and(trys<(self.__ser.timeout*10)):
                    trys+=1
                    outlen=self.__ser.inWaiting()
                    time.sleep(0.1)

                if 0<outlen<255:
                    ans=self.__ser.read(outlen)

                    out_obj=self.__pattern_kadr.search(ans)
                    outdata=out_obj.group('data').replace('\xff\xfe','\xff')
                    outcrc=out_obj.group('crc').replace('\xff\xfe','\xff')
                    if self.checkCRC(outdata+outcrc):
                        res=outdata[2:] if (len(outdata)>1) else None
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

    def decodeBCD(self,bcd):
        res=["%02x" % ord(x) for x in bcd]
        res.reverse()
        return list("".join(res))


    def getBRUTTO(self):
        weight=None
        data='\xc3'
        res=self.query(data)
        if res is None: return None,False

        weight_digs=self.decodeBCD(res[:-1])
        con=ord(res[-1:])
        if (con & self.__OVERLOAD) != self.__OVERLOAD:
            sep = con & self.__SEPARATOR
            weight_digs.insert(6-sep,'.')
            if (con & self.__MINUS)==self.__MINUS:
                weight_digs.insert(0,'-')
            weight=float("".join(weight_digs))
        return weight,((con & self.__SEDATION)==self.__SEDATION)

    def regWeight(self,weight):
        if self.__d.reg(weight):
            self.log.d('regWeight: %s' % weight)
            return True
        else:
            self.log.d('ERROR regWeight %s: FAIL' % weight)
            return False

if __name__ == "__main__":
    tenso=Tenso(DEVICE,BAUDRATE,ADDR)
    tenso.debug=True
    old_weight=0
    cnt=0
    must_dump=False
    starting=True
    tenso.log.c("STARTING...")

    if path.isfile(DUMP_FILE):
        with open(DUMP_FILE,"rb") as dump:
            old_weight=pickle.load(dump)

    while True:
        try:
            weight,sedation=tenso.getBRUTTO()
            if tenso.debug:
                tenso.log.d(__name__+": weight = %1.1f (%i)" % (weight,sedation))
            if weight is None: continue

            if (sedation) and (starting) and (abs(weight-TABLE_WEIGHT)<1):
                continue

            if (abs(weight)<FILTER):
                must_dump=not(old_weight==0)
                old_weight=0
                starting=False
            elif (old_weight==0) and (not starting):
                if (sedation):
                    cnt+=1
                    if (cnt>2) and tenso.regWeight(weight):
                        old_weight=weight
                        must_dump=True
                        cnt=0
                else:
                    cnt=0
            if must_dump:
                with open(DUMP_FILE,"wb") as dump:
                    pickle.dump(old_weight,dump)
                must_dump=False

        except Exception as e:
            tenso.log.e(__name__+' ERROR: %s' % e)
            continue
        finally:
            time.sleep(0.5)



import sys,serial,time,re
from logger import *
from db import *

class Tenso:
    __MINUS=0x80
    __STABILITY=0x10
    __OVERLOAD=0x08
    __SEPARATOR=0x07
    

    def __init__(self,device,baudrate,addr):
        self.__ser = serial.Serial()
        self.__ser.port=device
        self.__ser.baudrate=baudrate
        self.__ser.timeout=1
        self.__ser.writeTimeout=1
        self.__addr=addr
	self.__pattern_kadr=re.compile('\xff+(?P<data>.*?)(?P<crc>\xff\xfe|[^\xff])\xff{2,}')
        self.debug=False

    def setLogger(self,tag):
	self.log=Logger(tag)

    def setDB(self,dbpath):
	self.db=DBreg(dbpath)


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
        return weight,((con & self.__STABILITY)==self.__STABILITY)

    def regWeight(self,weight):
        if self.db.reg(weight):
            self.log.d('regWeight: %s' % weight)
            return True
        else:
            self.log.d('ERROR regWeight %s: FAIL' % weight)
            return False

class NVT1N:
    __STABILITY=0x02
    __OVERLOAD=0x08
    __NULL=0x01

    def __init__(self,device,baudrate):
        self.__ser = serial.Serial()
        self.__ser.port=device
        self.__ser.baudrate=baudrate
        self.__ser.timeout=1
        self.__ser.writeTimeout=1
        self.__pattern_kadr=re.compile('\x02(?P<data>.{8})\x6b\x67\x0d') 
	self.debug=False

    def setLogger(self,tag):
	self.log=Logger(tag)

    def setDB(self,dbpath):
	self.db=DBreg(dbpath)

    def query(self):
        res=None
        try:
            ans=self.rawquery()
	    if not ans is None:
        	out_obj=self.__pattern_kadr.search(ans)
        	outdata=out_obj.group('data')
        	res=outdata if (len(outdata)>1) else None
        except Exception as e:
            self.log.e('query ERROR: %s' % e)
            if not ans is None:
                self.log.e('query ANSWER: %s' % "\\x".join(["%02x" % ord(x) for x in ans]))
        return res
    
    def rawquery(self):
	ans=None
	try:
	    if not self.__ser.isOpen():
		self.__ser.open()
	    if self.__ser.isOpen():
		trys=0
		outlen=0
    		while (outlen==0)and(trys<(self.__ser.timeout*10)):
        	    trys+=1
        	    outlen=self.__ser.inWaiting()
        	    time.sleep(0.1)
		if outlen>0:
		    ans=self.__ser.read(outlen)
	    else:
		self.log.e('rawquery ERROR: Can\'t open serial device')
	except Exception as e:
            self.log.e('rawquery ERROR: %s' % e)
	return ans

    def getBRUTTO(self):
        weight=None
        res=self.query()
        if res is None: return None,False
        
        con=ord(res[-1:])
        if ((con & self.__OVERLOAD) != self.__OVERLOAD):
	    weight=float(res[:-1].strip())
        return weight,((con & self.__STABILITY)==self.__STABILITY)

    def regWeight(self,weight):
        if (weight>0) and self.db.reg(weight):
            self.log.d('regWeight: %s' % weight)
            return True
        else:
            self.log.d('ERROR regWeight %s: FAIL' % weight)
            return False


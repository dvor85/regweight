#!/usr/bin/env python

import sys,time,os,pickle
from datetime import datetime
from os import path
from protocols import *
from db import *

DEVICE='/dev/ttyUSB0'
BAUDRATE=38400
ADDR='\x01'
SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
TABLE_WEIGHT=0
FILTER = 200

if __name__ == "__main__":
    tenso=Tenso(DEVICE,BAUDRATE,ADDR)
    tenso.setLogger('regweight')
    tenso.debug=True
    print " ".join(["%02x" % ord(x) for x in tenso.readRawData()])



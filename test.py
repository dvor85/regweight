#!/usr/bin/env python

import sys,time,os,pickle
from datetime import datetime
from os import path
from protocols import *
from db import *

DEVICE='/dev/ttyUSB0'
BAUDRATE=9600
ADDR='\x01'
SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,'regweight.dump')
TABLE_WEIGHT=0
FILTER = 200

if __name__ == "__main__":
    nvt=NVT1N(DEVICE,BAUDRATE)
    nvt.setLogger('regweight')
    nvt.debug=True
    print " ".join(["%02x" % ord(x) for x in nvt.readRawData()])



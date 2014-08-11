#!/usr/bin/env python

import pickle
import sys
from db import *
from datetime import *
from os import path


SELF_PATH=path.dirname(path.realpath(__file__))
DUMP_FILE=path.join(SELF_PATH,"regweight.dump")

def getNow():
    data=''
    if path.isfile(DUMP_FILE):
        with open(DUMP_FILE,"rb") as dump:
            data="CURRENT WEIGHT = %d kg" % pickle.load(dump)
    return data

def getData(dt1,dt2):
    data=''
    summ=0
    d=DBreg(SELF_PATH)
    weights=d.select(dt1,dt2)
    if len(weights)>0:
        for row in weights:
            data+="{0:^5d} {1:^22s} {2:^5d}\n".format(row[0],row[1],row[2])
            summ+=int(row[2])
    return data,summ

if __name__ == "__main__":
    if len(sys.argv)==1:
        dt1_obj=date.today()
        dt2_obj=dt1_obj+timedelta(days=1)
        dt1=dt1_obj.strftime("%Y-%m-%d")
        dt2=dt2_obj.strftime("%Y-%m-%d")
    elif len(sys.argv)==2:
        dt1_obj=datetime.strptime(sys.argv[1][:10],"%Y-%m-%d")
        dt2_obj=dt1_obj+timedelta(days=1)
        dt1=dt1_obj.strftime("%Y-%m-%d")
        dt2=dt2_obj.strftime("%Y-%m-%d")
    elif len(sys.argv)==3:
        dt1=sys.argv[1]
        dt2=sys.argv[2]
    print(getNow())
    print("{0:^5s} {1:<22s} {2:^5s}".format("ID","DATE TIME","WEIGHT"))
    data,summ=getData(dt1,dt2)
    print(data)
    print("TOTAL = %s tonns" % (summ/1000.0))
    


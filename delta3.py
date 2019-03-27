# -*- coding: utf-8 -*-
# $Id: delta3.py | Rev 40  | 2019/01/10 03:29:21 tin_fpga $
# xDevs.com TEC Experiment app 
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 2.7 | RPi3 
# Project maintainers:
#  o Ilya T.  (@)
# https://xdevs.com/guide/teckit
#
import os
import mmap
import sys
import time
import ftplib
import numbers
import signal
import numpy as np
from tools import *
import imp 

import ConfigParser
cfg = ConfigParser.ConfigParser()
cfg.read('teckit.conf')
cfg.sections()

if cfg.get('testset', 'mode', 1) == 'delta3':
    delta_res = 3
else:
    delta_res = 0

mfc1   = imp.load_source('hulk', 'devices/f5720a.py')                    # Load Fluke 5720+5725 support
mfc = mfc1.hulk(1,0,"5720")  # GPIB 1
print "\033[9;40H \033[1;34mDelta mode   : %d \033[0;39m" % (delta_res)

cur1                = float(cfg.get('testset', 'delta_ipos', 1))        # Positive current level for Delta-resistance mode
cur2                = float(cfg.get('testset', 'delta_ineg', 1))        # Negative current level for Delta-resistance mode

mfc.mfc_cmd("RANGELCK OFF")
time.sleep(1)
mfc.mfc_stby()
mfc.mfc_cmd("OUT %.6f A;OPER" % 0.1) #Neg
time.sleep(3)
mfc.mfc_cmd("RANGELCK ON")
time.sleep(1)
mfc.mfc_cmd("OUT 0 A, 0 Hz")
time.sleep(6)
mfc.mfc_oper()
time.sleep(6)
zerof1 = dmm1.get_data()
zerof2 = dmm2.get_data()
zerof3 = dmm3.get_data()
zerof4 = dmm4.get_data()
print ("Zero voltage = %f uV %f uV %f uV %f uV" % ( float(zerof1) * 1e6, float(zerof2) * 1e6, float(zerof3) * 1e6, float(zerof4) * 1e6) )

def delta_sample():
    mfc.mfc_cmd("OUT %.6f A;OPER" % cur1) #Neg
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos1")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1a = dmm1.read_val()[1]
    meas2a = dmm2.read_val()[1]
    meas3a = dmm3.read_val()[1]
    meas4a = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1a = dmm1.read_val()[1]
    meas2a = dmm2.read_val()[1]
    meas3a = dmm3.read_val()[1]
    meas4a = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1a += dmm1.read_val()[1]
    meas2a += dmm2.read_val()[1]
    meas3a += dmm3.read_val()[1]
    meas4a += dmm4.read_val()[1]
    meas1a = (meas1a / 2)
    meas2a = (meas2a / 2)
    meas3a = (meas3a / 2)
    meas4a = (meas4a / 2)

    mfc.mfc_cmd("OUT %.6f A;OPER" % cur2) #Neg
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Neg1")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1b = dmm1.read_val()[1]
    meas2b = dmm2.read_val()[1]
    meas3b = dmm3.read_val()[1]
    meas4b = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1b = dmm1.read_val()[1]
    meas2b = dmm2.read_val()[1]
    meas3b = dmm3.read_val()[1]
    meas4b = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1b += dmm1.read_val()[1]
    meas2b += dmm2.read_val()[1]
    meas3b += dmm3.read_val()[1]
    meas4b += dmm4.read_val()[1]
    meas1b = (meas1b / 2)
    meas2b = (meas2b / 2)
    meas3b = (meas3b / 2)
    meas4b = (meas4b / 2)

    mfc.mfc_cmd("OUT %.6f A;OPER" % cur1) #Neg
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos2")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1c = dmm1.read_val()[1]
    meas2c = dmm2.read_val()[1]
    meas3c = dmm3.read_val()[1]
    meas4c = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1c = dmm1.read_val()[1]
    meas2c = dmm2.read_val()[1]
    meas3c = dmm3.read_val()[1]
    meas4c = dmm4.read_val()[1]
    time.sleep(1)
    dmm1.trigger()
    dmm2.trigger()
    dmm3.trigger()
    dmm4.trigger()
    meas1c += dmm1.read_val()[1]
    meas2c += dmm2.read_val()[1]
    meas3c += dmm3.read_val()[1]
    meas4c += dmm4.read_val()[1]        
    meas1c = (meas1c / 2)
    meas2c = (meas2c / 2)
    meas3c = (meas3c / 2)
    meas4c = (meas4c / 2)

    calc_resa = ( ( (meas1a - zerof1) - 2*(meas1b - zerof1) + (meas1c - zerof1) ) / 4) / cur1
    print "\033[12;40H \033[1;34mDVal %.8f \033[0;39m" % float(calc_resa)
    calc_resb = ( ( (meas2a - zerof2) - 2*(meas2b - zerof2) + (meas2c - zerof2) ) / 4) / cur1
    calc_resc = ( ( (meas3a - zerof3) - 2*(meas3b - zerof3) + (meas3c - zerof3) ) / 4) / cur1
    calc_resd = ( ( (meas4a - zerof4) - 2*(meas4b - zerof4) + (meas4c - zerof4) ) / 4) / cur1

    #print emvals
    #meas_val  = calc_resa #float(emvals[0])#val()[1]
    #meas_val2 = calc_resb #float(emvals[1])#dmm3.read_val()[1]
    #meas_val3 = calc_resc #float(emvals[2])#dmm3.read_val()[1]
    #meas_val4 = calc_resd #float(emvals[3])#(meas_val + meas_val3 - (2 * meas_val2) ) / 4
    return calc_resa, calc_resb, calc_resc, calc_resd, meas1a, meas1b, meas1c

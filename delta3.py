# -*- coding: utf-8 -*-
# $Id: delta3.py | Rev 44  | 2020/02/13 19:28:25 tin_fpga $
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

dmm1   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
dmm2   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
dmm1 = dmm1.dmm_meter (3,0,"3458A")  # GPIB.
dmm2 = dmm2.dmm_meter (2,0,"3458B")  # GPIB.
dmm1.set_dcv_range(0.1)                                                # 3458A function/range config
dmm2.set_dcv_range(0.10)                                                # 3458B function/range config

mfc1   = imp.load_source('hulk', 'devices/f5720a.py')                    # Load Fluke 5720+5725 support
mfc = mfc1.hulk(1,0,"5720")  # GPIB 1
#csrc2   = imp.load_source('hp3245', 'devices/hp3245a.py')                    # Load Keithley 6221 support
#csrc = csrc2.usrc(8,0,"3245")  # GPIB 8
smu = imp.load_source('a4142b', 'devices/hp4142b.py')                    # Load Agilent 4142B support
csmu = smu.smu_src(14,0,"4142B")  # GPIB 14

print "\033[9;40H \033[1;34mDelta mode   : %d \033[0;39m" % (delta_res)

cur1                = float(cfg.get('testset', 'delta_ipos', 1))        # Positive current level for Delta-resistance mode
cur2                = float(cfg.get('testset', 'delta_ineg', 1))        # Negative current level for Delta-resistance mode

mfc.mfc_cmd("RANGELCK OFF")
time.sleep(1)
csmu.get_err()
csmu.inst.write("RI2, -19\n")
csmu.inst.write("RI5, -19\n")
csmu.src_on(5)
csmu.src_on(2)
csmu.src_curr(5,0,19,10)
mfc.mfc_stby()
mfc.mfc_cmd("OUT %.6f A;OPER" % 0.1) #Neg
time.sleep(3)
mfc.mfc_cmd("RANGELCK ON")
time.sleep(1)
mfc.mfc_cmd("OUT 0 A, 0 Hz")
#csrc.set_output_dci(0)
csmu.get_err()
csmu.inst.write("RI2, -19\n")
csmu.inst.write("RI5, -19\n")
csmu.src_on(2)
csmu.src_on(5)
csmu.src_curr(5,0,19,10)
time.sleep(2)
mfc.mfc_oper()
time.sleep(2)
zerof1 = dmm1.get_data()
zerof2 = dmm2.get_data()
zerof3 = 0#dmm3.get_data()
zerof4 = 0#dmm4.get_data()
print ("\033[7;50HZero V %f uV %f uV %f uV %f uV" % ( float(zerof1) * 1e6, float(zerof2) * 1e6, float(zerof3) * 1e6, float(zerof4) * 1e6) )

def delta_sample():
    mfc.mfc_cmd("OUT %.6f A;OPER" % cur1) #Neg
    #csrc.set_output_dci(cur1)
    csmu.src_curr(5,cur1,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos1")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1a = dmm1.read_val()[1]
    meas2a = dmm2.read_val()[1]
    meas3a = 0#dmm3.read_val()[1]
    meas4a = 0#dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1a = dmm1.read_val()[1]
    meas2a = dmm2.read_val()[1]
    meas3a = 0#dmm3.read_val()[1]
    meas4a = 0#dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1a += dmm1.read_val()[1]
    meas2a += dmm2.read_val()[1]
    meas3a += 0#dmm3.read_val()[1]
    meas4a += 0##dmm4.read_val()[1]
    meas1a = (meas1a / 2)
    meas2a = (meas2a / 2)
    #meas3a = (meas3a / 2)
    #meas4a = (meas4a / 2)

    mfc.mfc_cmd("OUT %.6f A;OPER" % cur2) #Neg
    #csrc.set_output_dci(cur2)
    csmu.src_curr(5,cur2,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Neg1")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1b = dmm1.read_val()[1]
    meas2b = dmm2.read_val()[1]
    meas3b = 0#dmm3.read_val()[1]
    meas4b = 0#dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1b = dmm1.read_val()[1]
    meas2b = dmm2.read_val()[1]
    #meas3b = dmm3.read_val()[1]
    #meas4b = dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1b += dmm1.read_val()[1]
    meas2b += dmm2.read_val()[1]
    #meas3b += dmm3.read_val()[1]
    #meas4b += dmm4.read_val()[1]
    meas1b = (meas1b / 2)
    meas2b = (meas2b / 2)
    #meas3b = (meas3b / 2)
    #meas4b = (meas4b / 2)

    mfc.mfc_cmd("OUT %.6f A;OPER" % cur1) #Neg
    #csrc.set_output_dci(cur1)
    csmu.src_curr(5,cur1,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos2")
    time.sleep(3)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1c = dmm1.read_val()[1]
    meas2c = dmm2.read_val()[1]
    meas3c = 0#dmm3.read_val()[1]
    meas4c = 0#dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1c = dmm1.read_val()[1]
    meas2c = dmm2.read_val()[1]
    #meas3c = dmm3.read_val()[1]
    #meas4c = dmm4.read_val()[1]
    time.sleep(0.1)
    dmm1.trigger()
    dmm2.trigger()
    #dmm3.trigger()
    #dmm4.trigger()
    meas1c += dmm1.read_val()[1]
    meas2c += dmm2.read_val()[1]
    #meas3c += dmm3.read_val()[1]
    #meas4c += dmm4.read_val()[1]        
    meas1c = (meas1c / 2)
    meas2c = (meas2c / 2)
    #meas3c = (meas3c / 2)
    #meas4c = (meas4c / 2)
    csmu.src_curr(2,cur1,19,10)

    calc_resa = ( ( (meas1a - zerof1) - 2*(meas1b - zerof1) + (meas1c - zerof1) ) / 4) / cur1
    calc_resb = ( ( (meas2a - zerof2) - 2*(meas2b - zerof2) + (meas2c - zerof2) ) / 4) / cur1
    #calc_resb = ( ( (meas2a - zerof2) + (meas2b - zerof2) + (meas2c - zerof2) ) / 3) / cur1
    calc_resc = 0#( ( (meas3a - zerof3) - 2*(meas3b - zerof3) + (meas3c - zerof3) ) / 4) / cur1
    calc_resd = 1#( ( (meas4a - zerof4) - 2*(meas4b - zerof4) + (meas4c - zerof4) ) / 4) / cur1
    print "\033[12;40H \033[1;34mDVal %.8f \033[0;39m" % float(calc_resa)

    dmm1.disp_msg("%.7f R" % calc_resa)
    dmm2.disp_msg("%.7f R" % calc_resb)

    #print emvals
    #meas_val  = calc_resa #float(emvals[0])#val()[1]
    #meas_val2 = calc_resb #float(emvals[1])#dmm3.read_val()[1]
    #meas_val3 = calc_resc #float(emvals[2])#dmm3.read_val()[1]
    #meas_val4 = calc_resd #float(emvals[3])#(meas_val + meas_val3 - (2 * meas_val2) ) / 4
    return calc_resa, calc_resb, calc_resc, calc_resd, meas1a, meas1b, meas1c

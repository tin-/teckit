# -*- coding: utf-8 -*-
# $Id: deltai.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
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

if cfg.get('testset', 'mode', 1) == 'deltan':
    delta_res = 5
else:
    delta_res = 0

#dmm1   = imp.load_source('k2182a', 'devices/k2182.py')                 # Load Keysight 3458A support
#dmm1   = imp.load_source('hp34420a', 'devices/hp34420.py')                 # Load Keysight 3458A support
#dmm2   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
#dmm3   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
dmm4   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
#dmm1 = dmm1.scpi_meter (19,0,"2182A")  # GPIB.
#dmm1 = dmm1.scpi_meter (5,0,"34420A")  # GPIB.
#dmm2 = dmm2.dmm_meter (3,0,"3458A3")  # GPIB.
#dmm3 = dmm3.dmm_meter (2,0,"3458A2")  # GPIB.
dmm4 = dmm4.dmm_meter (11,0,"3458A11")  # GPIB.
#dmm1.set_dcv_nrange(0.1,1)                                                # 3458A function/range config
#dmm1.set_dcv_nrange(0.1,2)                                                # 3458A function/range config


mfc1   = imp.load_source('hulk', 'devices/f5720a.py')                    # Load Fluke 5720+5725 support
mfc = mfc1.hulk(1,0,"5720A")  # GPIB 1
#mfcb = mfc1.hulk(20,0,"5720B")  # GPIB 1
#csrc2   = imp.load_source('hp3245', 'devices/hp3245a.py')                    # Load Keithley 6221 support
#csrc = csrc2.usrc(7,0,"3245")  # GPIB 8
#smu = imp.load_source('a4142b', 'devices/hp4142b.py')                    # Load Agilent 4142B support
#csmu = smu.smu_src(14,0,"4142B")  # GPIB 14

print "\033[9;40H \033[1;34mDelta mode   : %d \033[0;39m" % (delta_res)

cur1                = float(cfg.get('testset', 'delta_ipos', 1))        # Positive current level for Delta-resistance mode
cur2                = float(cfg.get('testset', 'delta_ineg', 1))        # Negative current level for Delta-resistance mode

mfc.mfc_cmd("RANGELCK OFF")
#mfcb.mfc_cmd("RANGELCK OFF")
time.sleep(1)
#csmu.get_err()
#csmu.inst.write("RI2, -19\n")
#csmu.inst.write("RI5, -19\n")
#csmu.src_on(5)
#csmu.src_on(2)
#csmu.src_curr(5,0,19,10)
mfc.mfc_stby()
#mfc.mfc_cmd("OUT %.6e A;OPER" % 1) #Neg
#mfcb.mfc_stby()
mfc.mfc_cmd("OUT %.6e A" % cur1) #Neg
#time.sleep(3)
mfc.mfc_cmd("RANGELCK ON")
#mfcb.mfc_cmd("RANGELCK ON")
#time.sleep(1)
mfc.mfc_cmd("OUT 0 A, 0 Hz")
#mfcb.mfc_cmd("OUT 0 A, 0 Hz")
#csrc.set_output_dci(0.0)
#csmu.get_err()
#csmu.inst.write("RI2, -19\n")
#csmu.inst.write("RI5, -19\n")
#csmu.src_on(2)
#csmu.src_on(5)
#csmu.src_curr(5,0,19,10)
mfc.mfc_oper()
time.sleep(10)

#dmm2.set_dcv_range(0.1)                                                # 3458B function/range config
#dmm3.set_dcv_range(0.1)                                                # 3458B function/range config
dmm4.set_dcv_range(0.1)                                                # 3458B function/range config
#dmm2.nplc(200)                                                # 3458B function/range config
#dmm3.nplc(200)                                                # 3458B function/range config
dmm4.nplc(200)                                                # 3458B function/range config


#mfcb.mfc_oper()
#time.sleep(2)
zerof1 = 0#dmm2.get_data() #dmm1.get_adata()
zerof2 = 0#dmm3.get_data() #dmm1.get_bdata()
zerof3 = dmm4.get_data()
zerof4 = 0#dmm4.get_data()
print ("\033[7;50HZero V %f uV %f uV %f uV %f uV" % ( float(zerof1) * 1e6, float(zerof2) * 1e6, float(zerof3) * 1e6, float(zerof4) * 1e6) )
samples = 3

def get_dsample():
    #dmm1.trigger()
    #dmm2.trigger()
    #dmm3.trigger()
    dmm4.trigger()
    s1a = 0#dmm1.get_adata()
    s2a = 0#dmm2.read_val()[1] #dmm1.get_bdata()
    s3a = 0#dmm3.read_val()[1] #(s1a + s2a) / 2#dmm3.read_val()[1]
    s4a = dmm4.read_val()[1]
    print ("\033[40;2H S1A = %.8e V  " % s2a)
    print ("\033[41;2H S2A = %.8e V  " % s3a)
    print ("\033[42;2H S3A = %.8e V  " % s4a)
    return s1a,s2a,s3a,s4a

def delta_sample():
    mfc.mfc_cmd("OUT %.6e A;OPER" % cur1) #Neg
    #mfcb.mfc_cmd("OUT %.6e A;OPER" % cur1) #Neg
    #csrc.set_output_dci(cur1)
    #csmu.src_curr(5,cur1,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos1")
    time.sleep(5)
    meas1a, meas2a, meas3a, meas4a = get_dsample()
    for vcnt in range (0, samples):
	ss1a, ss2a, ss3a, ss4a = get_dsample()
	meas1a += ss1a
	meas2a += ss2a
	meas3a += ss3a
	meas4a += ss4a

    meas1a = (meas1a / (samples+1))
    meas2a = (meas2a / (samples+1))
    meas3a = (meas3a / (samples+1))
    meas4a = (meas4a / (samples+1))

    mfc.mfc_cmd("OUT %.6e A;OPER" % cur2) #Neg
    #mfcb.mfc_cmd("OUT %.6e A;OPER" % cur2) #Neg
    #csrc.set_output_dci(cur2)
    #csmu.src_curr(5,cur2,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Neg1")
    time.sleep(5)
    meas1b, meas2b, meas3b, meas4b = get_dsample()
    for vcnt in range (0, samples):
	ss1a, ss2a, ss3a, ss4a = get_dsample()
	meas1b += ss1a
	meas2b += ss2a
	meas3b += ss3a
	meas4b += ss4a
    meas1b = (meas1b / (samples+1))
    meas2b = (meas2b / (samples+1))
    meas3b = (meas3b / (samples+1))
    meas4b = (meas4b / (samples+1))

    mfc.mfc_cmd("OUT %.6e A;OPER" % cur1) #Neg
    #mfcb.mfc_cmd("OUT %.6e A;OPER" % cur1) #Neg
    #csrc.set_output_dci(cur1)
    #csmu.src_curr(5,cur1,19,10)
    print "\033[12;40H \033[1;34mDStage   : %s \033[0;39m" % ("Pos2")
    time.sleep(5)
    meas1c, meas2c, meas3c, meas4c = get_dsample()
    for vcnt in range (0, samples):
	ss1a, ss2a, ss3a, ss4a = get_dsample()
	meas1c += ss1a
	meas2c += ss2a
	meas3c += ss3a
	meas4c += ss4a
    meas1c = (meas1c / (samples+1))
    meas2c = (meas2c / (samples+1))
    meas3c = (meas3c / (samples+1))
    meas4c = (meas4c / (samples+1))

    calc_resa = ( ( (meas1a - zerof1) - 2*(meas1b - zerof1) + (meas1c - zerof1) ) / 4) / (cur1)
    calc_resb = ( ( (meas2a - zerof2) - 2*(meas2b - zerof2) + (meas2c - zerof2) ) / 4) / (cur1)
    calc_resc = ( ( (meas3a - zerof3) - 2*(meas3b - zerof3) + (meas3c - zerof3) ) / 4) / (cur1)
    calc_resd = ( ( (meas4a - zerof4) - 2*(meas4b - zerof4) + (meas4c - zerof4) ) / 4) / (cur1)
    print "\033[12;40H \033[1;34mDVal %.8f \033[0;39m" % float(calc_resa)

    #dmm1.disp_msg("%.7f R" % calc_resa)

    #print emvals
    #meas_val  = calc_resa #float(emvals[0])#val()[1]
    #meas_val2 = calc_resb #float(emvals[1])#dmm3.read_val()[1]
    #meas_val3 = calc_resc #float(emvals[2])#dmm3.read_val()[1]
    #meas_val4 = calc_resd #float(emvals[3])#(meas_val + meas_val3 - (2 * meas_val2) ) / 4
    return calc_resa, calc_resb, calc_resc, calc_resd, meas2a, meas2b, meas2c, meas3a, meas3b, meas3c, meas4a, meas4b, meas4c

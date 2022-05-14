# -*- coding: utf-8 -*-
# xDevs.com Confidential
# 
# $Id: devices/hp3458a.py | Rev 4  | 2017/10/17 14:32:19 tin_fpga $
# xDevs.com TEC Experiment setup | HP 3458A module
# 
# Copyright (c) 2012-2017, xDevs.com
# 
# Python 2.7 | RPI3 | Win32
# Project maintainers:
#  o Tsemenko Ilya  (@)
# 
# https://xdevs.com/guide/teckit
#

import time
import sys
import ConfigParser
import Gpib

cfg = ConfigParser.ConfigParser()
cfg.read('teckit.conf')
cfg.sections()

#if cfg.get('teckit', 'if_debug', 1) == 'true':
#    from if_debug import *
#elif cfg.get('teckit', 'if_debug', 1) == 'false':
#    if cfg.get('teckit', 'interface', 1) == 'gpib':
#        from if_gpib import *
#    else:
#        print "No interface defined!"
#        quit()
        
today_date = time.strftime("%d %B %Y %H:%M")
today_caldate = time.strftime("%m%d%y%H%M")
cal_interval = 365

hp3458_proc_version = "$Id: devices/hp3458a.py | Rev 4  | 2017/10/17 14:32:19 tin_fpga $"

result_log_fn = cfg.get('teckit', 'raw_data_filelog', 1)

# Module-wide definitions
hp3458_mfg_id = "HEWLETT-PACKARD"
hp3458_model_id = "3458A"

hp3458_dcz_test_values = [0.1, 1.0, 10.0, 100.0, 1000.0] # Per cal.manual
hp3458_dcz_tstr_values = ["Short 0 mVDC", "Short 0.0 VDC", "Short 00.0 VDC", "Short 000.0 VDC", "Short 0000.0 VDC"] # Per cal.manual
hp3458_spec_dcv_zero = [0.16E-6, 0.15E-6, 0.32E-6, 14E-6, 41E-6] # Per cal.manual
hp3458_acz_tstr_values = ["Short 0 mVAC", "Short 0 mVAC", "Short 0.0 VAC", "Short 00.0 VAC", "Short 000.0 VAC", "Short 0000.0 VAC"] # Per cal.manual

hp3458_dcv_test_values = [100E-3, -100E-3,     # 100mV
 100E-3, 200E-3, 1.0, -100E-3, -200E-3, -1.0,  # 1V
 1.0, 2.0, 10.0, -1.0, -2.0,  -10.0,              # 10V
 10 ,  20,  100,  -10, -20,  -100,              # 100V
 100, 200, 1000, -100, -200, -1000] # 1000V Per cal.manual
hp3458_dcv_test_ranges = [0.1, 0.1, 
 1.0,  1.0,  1.0,  1.0,  1.0,  1.0, 
10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 
100.0,100.0,100.0,100.0,100.0,100.0,
1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
hp3458_dcl_test_values = [10.99999900, 9.999999, 8.888888, 7.777777, 6.666666, 5.555555, 4.444444, 3.333333, 2.222222, 1.111111, 0.123456789, -0.123456789, -1.111111, -2.222222, -3.333333, -4.444444, -5.555555, -6.666666, -7.777777, -8.888888, -9.999999, -10.999999] # Per cal.manual
hp3458_dci_test_values = [1E-7, -1E-7, 1E-6, -1E-6, 10E-6, -10E-6, 100E-6, -100E-6, 1E-3, -1E-3, 10E-3, -10E-3, 100E-3, -100E-3, 1.0, -1.0] # Per cal.manual
hp3458_dci_tstr_values = ["100 n", "-100 n", "1 &micro;", "-1 &micro;", "10 &micro;", "-10 &micro;", "100 &micro;", "-100 &micro;", "1.0 m", "-1.0 m", "10 m", "-10 m", "100 m", "-100 m", "1.0 ", "-1.0 "] # Per cal.manual
mfc_dcv_err = [0.00,  0.0,
 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0.0,  0.0, 0.0, 0.0, 0.0, 0.0,
 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0.00, 0.0, 0.0, 0.0, 0.0, 0.0,
] # Per cal.manual
mfc_dci_err = [0.0, 0.0, 0.0, 0.0,0.0, 0.0,0.0, 0.0,
0.0, 0.0, 
0.0, 0.0, 
0.0, 0.0, 
0.0, 0.0] # Per cal check 24h

hp3458_aci_test_values = [10E-6, 100E-6, 1E-3, 10E-3, 100E-3, 1.0] # Per cal.manual
hp3458_aci_tstr_values = ["10 &micro;", "100 &micro;", "1.0 m", "10 m", "100 m", "1.0 "] # Per cal.manual
hp3458_aci_test_fvalue = [50, 60, 1E3] # Per cal.manual

hp3458_acv_unc = [2, 2, 2, 2, 2, 2]

hp3458_acz_test_values = [10E-3, 100E-3, 1.0, 10, 100, 700] # Per cal.manual zero
hp3458_acv_test_values = [1, 10] # Per cal.manual
hp3458_acv_test_fvalue = [10, 200, 500, 50E3, 1E6]
hp3458_acvs_test_values = [10E-3, 100E-3, 1.0, 10, 100, 700] # Per cal.manual
hp3458_acvs_test_fvalue = [10, 20, 40, 100, 1E3, 10E3, 20E3, 50E3, 100E3, 300E3, 500E3, 1E6]
hp3458_loacv_test_fvalue = [10, 20, 40, 100]

# ACV specifications
hp3458_acv_ranges  = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
hp3458_acv_uvr_ranges  = [0.0009, 0.009, 0.09, 0.9, 9, 90]
hp3458_acv_ovr_ranges  = [12E-3, 120E-3, 1.2, 12, 120, 1050]
hp3458_acv_band    = [10, 40, 20E3, 50E3, 100E3, 500E3,  1E6, 2E6] # Max freq range
# ACV, 6 digit res, 6 month from last cal, after 30 min warmup
hp3458_spec_acv_1y = [75,   30,   70,   150,   300, 1000]    #0.3V - 100V
hp3458_spec_acv_1y_hv = [80,35,   75,   150] #300V - 1000V

hp3458_spec_acv_fvalue_band =   [40, 1E3, 20E3, 50E3, 100E3, 300E3, 1E6, 2E6, 4E6, 8E6, 10E6]
hp3458_spec_rdg_acv_24h = []      # 10mV   100mV      1V     10V    100V     1kV   ppm + ppm
hp3458_spec_rdg_acv_24h.append([    300  ,     70,     70,     70,    200,    400   ]) # 40 Hz   - 0 
hp3458_spec_rdg_acv_24h.append([    200  ,     70,     70,     70,    200,    400   ]) # 1 kHz   - 1 
hp3458_spec_rdg_acv_24h.append([    300  ,    140,    140,    140,    200,    600   ]) # 20 kHz  - 2 
hp3458_spec_rdg_acv_24h.append([   1000  ,    300,    300,    300,    350,   1200   ]) # 50 kHz  - 3 
hp3458_spec_rdg_acv_24h.append([   5000  ,    800,    800,    800,   1200,   3000   ]) # 100 kHz - 4 
hp3458_spec_rdg_acv_24h.append([  40000  ,   3000,   3000,   3000,   4000           ]) # 300 kHz - 5 
hp3458_spec_rdg_acv_24h.append([  40000  ,  10000,  10000,  10000,  15000           ]) # 1 MHz   - 6 
hp3458_spec_rdg_acv_24h.append([  40000  ,  15000,  15000,  15000                   ]) # 2 MHz   - 7 
hp3458_spec_rdg_acv_24h.append([  70000  ,  40000,  40000,  40000                   ]) # 4 MHz   - 8 
hp3458_spec_rdg_acv_24h.append([ 200000  ,  40000,  40000,  40000                   ]) # 8 MHz   - 9 
hp3458_spec_rdg_acv_24h.append([    0    , 150000, 150000, 150000                   ]) # 10 MHz  - 10 
hp3458_spec_rng_acv_24h = []      # 10mV   100mV      1V     10V    100V     1kV   ppm + ppm
hp3458_spec_rng_acv_24h.append([    300  ,     40,     40,     40,     40,     40   ]) # 40 Hz   - 1 
hp3458_spec_rng_acv_24h.append([    110  ,     20,     20,     20,     20,     20   ]) # 1 kHz   - 2 
hp3458_spec_rng_acv_24h.append([    110  ,     20,     20,     20,     20,     20   ]) # 20 kHz  - 3 
hp3458_spec_rng_acv_24h.append([    110  ,     20,     20,     20,     20,     20   ]) # 50 kHz  - 4 
hp3458_spec_rng_acv_24h.append([    110  ,     20,     20,     20,     20,     20   ]) # 100 kHz - 5 
hp3458_spec_rng_acv_24h.append([    200  ,    100,    100,    100,    100,          ]) # 300 kHz - 6 
hp3458_spec_rng_acv_24h.append([    500  ,    100,    100,    100,    100,          ]) # 1 MHz   - 7 
hp3458_spec_rng_acv_24h.append([    700  ,    100,    100,    100,                  ]) # 2 MHz   - 8 
hp3458_spec_rng_acv_24h.append([    800  ,    700,    700,    700,                  ]) # 4 MHz   - 9 
hp3458_spec_rng_acv_24h.append([    800  ,    800,    800,    800,                  ]) # 8 MHz   - 10 
hp3458_spec_rng_acv_24h.append([    0    ,   1000,   1000,   1000,                  ]) # 10 MHz  - 11 

hp3458_spec_rdg_acv = hp3458_spec_rdg_acv_24h
hp3458_spec_rng_acv = hp3458_spec_rng_acv_24h

hp3458_res_tstr_values = ["1 ","1.9 ","10 ","19 ", "100 ","190 ", "1.0 k", "1.9 k","10 k","19 k", "100 k", "190 k","1.0 M","1.9 M", "10 M","19 M", "100 M"] # Per cal.manual
hp3458_res_test_values = [1, 1.9, 10, 19, 100, 190, 1E3, 1.9E3, 10E3, 19E3, 100E3, 190E3, 1E6, 1.9E6, 10E6, 19E6, 100E6] # Per cal.manual
hp3458_res_test_ranges = [1, 10, 10, 100, 100, 1E3, 1E3, 10E3, 10E3, 100E3, 100E3, 1E6, 1E6, 10E6, 10E6, 100E6, 100E6] # Per cal.manual

hp3458_rez_tstr_values = ["10R REAR ", "10K REAR "] # Per cal.manual
hp3458_rez_test_values = [10, 10E3] # Per cal.manual
hp3458_1g_test_value = [0.99551672E9] # 1Gohm reference

# hp3458 Specifications values
hp3458_tcal_10m = 0.5 #1K tolerance
hp3458_tcal_24h = 1.0 #1K tolerance
hp3458_tcal_long = 5.0 #5K tolerance
hp3458_tcal_acv = 2.0 #2K tolerance from last ACCAL

hp3458_dcv_ranges = [0.1, 1, 10, 100, 1000]
hp3458_dcv_unc = [2, 2, 2, 2, 2]

# DCV 10 minute spec, 20-rdg repeat FILTER, Tref = 0.5c, readings within 10%
hp3458_spec_rdg_dcv_10m = [0.5, 0.3, 0.05, 0.5, 1.5] #RelAcc reading , 24 hour
hp3458_spec_rng_dcv_10m = [0.5, 0.1, 0.05, 0.1, 0.05] #RelAcc range, 24 hour
# DCV 100 NPLC
hp3458_spec_rdg_dcv_24h = [2.5, 1.5, 0.5, 2.5, 2.5] #RelAcc reading , 24 hour
hp3458_spec_rng_dcv_24h = [3, 0.3, 0.05, 0.3, 0.1] #RelAcc range, 24 hour
# DCV 100 NPLC
hp3458_spec_rdg_dcv_90d = [3.5, 3.1, 2.6, 4.5, 4.5] #RelAcc reading , 24 hour
hp3458_spec_rng_dcv_90d = hp3458_spec_rng_dcv_24h #RelAcc range, 24 hour
# DCV 100 NPLC
hp3458_spec_rdg_dcv_1y = [5, 4, 4, 6, 6] #RelAcc range, 1 year
hp3458_spec_rng_dcv_1y = hp3458_spec_rng_dcv_24h #RelAcc reading , 1 year
# DCV 100 NPLC
hp3458_spec_rdg_dcv_2y = [10, 10, 10, 10, 10] #RelAcc reading , 24 hour
hp3458_spec_rng_dcv_2y = hp3458_spec_rng_dcv_24h #RelAcc range, 24 hour

hp3458_hv_unc = 12 * 1E-6 #2.5ppm per Vin/1000V for 24h+ 

# Ohm specifications, DELAY 0, ARANGE OFF, OCOMP ON
hp3458_res_ranges = [10, 100, 1E3, 1E4, 1E5, 1E6, 1E7, 1E8, 1E9]
hp3458_res_unc = [   3,   3,   3,   3,   3,    3,    3,    3,    3]
# OHM 100NPLC
hp3458_spec_rdg_res_24h = [5, 3,  2 ,  2 ,  2 , 10, 50, 500, 5000] #RelAcc reading , 24 hour
hp3458_spec_rng_res_24h = [3  , 3, 0.2, 0.2 , 0.2,   1,  5 ,10,10] #RelAcc range, 24 hour
# OHM 100NPLC
hp3458_spec_rdg_res_90d = [15, 10, 8, 8,  8, 12, 50 , 500, 5000] #RelAcc reading , 24 hour
hp3458_spec_rng_res_90d = [5, 5, 0.5, 0.5, 0.5,   2,  10,10, 10] #RelAcc range, 24 hour
# OHM 100NPLC
hp3458_spec_rdg_res_1y = [15, 12, 10,10,10, 15, 50 , 500, 5000] #RelAcc range, 1 year
hp3458_spec_rng_res_1y = hp3458_spec_rng_res_90d #RelAcc reading , 1 year
# OHM 100NPLC
hp3458_spec_rdg_res_2y = [20, 20, 15, 15, 15, 20,  75,1000,10000] #RelAcc reading , 24 hour
hp3458_spec_rng_res_2y = [10,10, 1  ,  1 , 1,   4,  10,10, 10] #RelAcc range, 24 hour

# DC Current specifications
hp3458_dci_ranges = [100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3, 100E-3, 1]
hp3458_dci_unc =    [5, 5, 5, 5, 5, 5, 5, 5]
# DCI 100 NPLC
hp3458_spec_rdg_dci_24h = [ 10, 10, 10, 10, 10, 10, 25, 100] #RelAcc reading , 24 hour
hp3458_spec_rng_dci_24h = [ 400,40,  7,  6,  4,  4,  4,  10] #RelAcc range, 24 hour
# DCI 100 NPLC
hp3458_spec_rdg_dci_90d = [ 30, 15, 15, 15, 15, 15, 30, 100] #RelAcc reading , 90 day
hp3458_spec_rng_dci_90d = [400, 40, 10,  8,  5,  5,  5,  10] #RelAcc range, 90 day
# DCI 100 NPLC
hp3458_spec_rdg_dci_1y = [ 30, 20, 20, 20, 20, 20, 35, 110] #RelAcc range, 1 year
hp3458_spec_rng_dci_1y = hp3458_spec_rng_dci_90d #RelAcc reading , 1 year
# DCI 100 NPLC
hp3458_spec_rdg_dci_2y = [ 35, 25, 25, 25, 25, 25, 40, 115] #RelAcc reading , 2 years
hp3458_spec_rng_dci_2y = hp3458_spec_rng_dci_90d #RelAcc range, 2 years

# DC Current specifications
hp3458_aci_ranges = [100E-6, 1E-3, 10E-3, 100E-3, 1]
hp3458_aci_unc =    [     5,    5,     5,      5, 5]
hp3458_aci_ovr_ranges  = [120E-6, 1.2E-3, 12E-3, 120E-3, 1.1]
# DCI 100 NPLC
hp3458_spec_aci_fvalue_band =   [20,  45,  100,  5E3,  20E3,  50E3, 100E3]
hp3458_spec_rdg_aci_24h = [] #    100uA      1mA    10mA   100mA     1 A    ppm + ppm
hp3458_spec_rdg_aci_24h.append([   4000,   4000,   4000,   4000,   4000   ]) # 20 Hz   - 0 
hp3458_spec_rdg_aci_24h.append([   1500,   1500,   1500,   1500,   1600   ]) # 45 Hz   - 1 
hp3458_spec_rdg_aci_24h.append([    600,    600,    600,    600,    800   ]) # 100 Hz  - 2 
hp3458_spec_rdg_aci_24h.append([    600,    300,    300,    300,   1000   ]) # 5 kHz  - 3 
hp3458_spec_rdg_aci_24h.append([      0,    600,    600,    600,   3000   ]) # 20 kHz - 4 
hp3458_spec_rdg_aci_24h.append([      0,   4000,   4000,   4000,  10000   ]) # 50 kHz - 5 
hp3458_spec_rdg_aci_24h.append([      0,   5500,   5500,   5500,      0   ]) # 100 kHz   - 6 
hp3458_spec_rng_aci_24h = [] #    100uA      1mA    10mA   100mA     1 A    ppm + ppm
hp3458_spec_rng_aci_24h.append([    300,    200,    200,    200,    200   ]) # 20 Hz   - 0 
hp3458_spec_rng_aci_24h.append([    300,    200,    200,    200,    200   ]) # 45 Hz   - 1 
hp3458_spec_rng_aci_24h.append([    300,    200,    200,    200,    200   ]) # 100 Hz  - 2 
hp3458_spec_rng_aci_24h.append([    300,    200,    200,    200,    200   ]) # 5 kHz  - 3 
hp3458_spec_rng_aci_24h.append([      0,    200,    200,    200,    200   ]) # 20 kHz - 4 
hp3458_spec_rng_aci_24h.append([      0,    400,    400,    400,    400   ]) # 50 kHz - 5 
hp3458_spec_rng_aci_24h.append([      0,   1500,   1500,   1500,      0   ]) # 100 kHz   - 6 

# ACV specifications
std_acv_ranges = []
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10, 100.0, 100.0, 700.0]) # 10 Hz  - 0.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10, 100.0, 100.0, 700.0]) # 40 Hz  - 1.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10, 100.0, 100.0, 700.0]) # 20 kHz - 2.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10, 100.0, 100.0,      ]) # 50 kHz - 3.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10, 100.0, 100.0,      ]) # 100 kHz- 4.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10,                    ]) # 500 kHz- 5.
std_acv_ranges.append([100E-3, 100E-3, 1.0, 1.0, 10.0, 10,                    ]) # 1 MHz  - 6.

hp3458_spec_rdg_aci = hp3458_spec_rdg_aci_24h
hp3458_spec_rng_aci = hp3458_spec_rng_aci_24h

gpib_addr = int(cfg.get('dmm', 'dmm_gpib_addr', 1) )
intf = Gpib.gpib(0, gpib_addr,timeout=60)

def meter_dorm(timer):
    if (cfg.get('teckit', 'no_delays', 1) == 'true'):
        print " ",
    else:
        for dorm in range (0,timer):
            time.sleep(1)
            sys.stdout.write('.')
            if ((dorm % 10) == 0):
                sys.stdout.write('\r*********  %d to go     \r' % (timer - dorm) )
            sys.stdout.flush()
    
def hp3458_echo():
    print "TEST-internal"
    
def hp3458_setup():
    print "\033[1;30;42mInitialize HP 3458A\033[1;39;49m"
    intf.clear()
    intf.write ("TARM HOLD")
    intf.write ("TRIG SGL")
    intf.write ("PRESET NORM")
    intf.write ("OFORMAT ASCII")
    intf.write ("FUNC DCV,AUTO")
    intf.write ("NPLC 100")
    intf.write ("AZERO ON")
    intf.write ("NRDGS 1,AUTO")
    intf.write ("MEM OFF")
    intf.write ("END ALWAYS")
    intf.write ("NDIG 9")
    intf.write ("DELAY 0")
    
def hp3458_check_info():
    dutinf = []
    info = intf.read("ID?")
    dutinf.append("Meter Info")
    dutinf.append(info[1])

    print ("Read last calibration information")
    dutinf.append("Last calibration date")
    dutinf.append("01/01/2017")
    print ("Read next calibration information")
    dutinf.append("Next calibration date")
    dutinf.append("03/01/2018")
    
    dutinf.append("Test date")
    dutinf.append(today_date)
    print ("TEMP?")
    dut_temp = intf.read ("TEMP?")
    dutinf.append("DUT Internal TEMP?")
    dutinf.append("%s" % dut_temp[1])
    tval = intf.read ("CALNUM?")
    calnum = float(tval[1])
    dutinf.append("DUT Calibrations number?")
    dutinf.append("%4.0f" % calnum)
    
    if cfg.get('mode', 'run_selftest', 1) == 'true':
        # Perform self-test
        print ("Self-test")
        intf.write ("TEST")
        meter_dorm(80)                                      # Self-test takes 73 seconds
        print ("SELF-TEST DONE")
        tval = intf.read ("ERRSTR?")
        dutinf.append("Self-test result?")
        dutinf.append("%s" % tval[1])
    else:
        dutinf.append("Self-test result?")
        dutinf.append("Not tested")
    
    tval = intf.read ("ERRSTR?")                        # Read all errors if any
    print tval
    tval = intf.read ("ERRSTR?")                        # Read all errors if any
    print tval
    tval = intf.read ("ERRSTR?")                        # Read all errors if any
    print tval
    
    # Collect all calibration constants
    hp3458_vfd_on("DUMP CAL CONSTS.")
    cvtbl = []
    cix = 1
    print ("Reading CAL constants")
    while cix <= 253:
        #cvtbl.append ("%d" % cix)
        cvtbl.append (intf.read ("CAL? %d,1" % cix) )
        time.sleep(0.001)
        cix = cix + 1
        sys.stdout.write('.')
        sys.stdout.flush()
    
    with open(result_log_fn, 'a') as dile:
        dile.write ("\r\n")
        dile.write ("\r\nPRE-ACAL DUMP : %s" % cvtbl)
    dile.close()

    if cfg.get('mode', 'run_acal', 1) == 'true':
        print ("ACAL ALL")
        intf.write ("ACAL ALL")
        meter_dorm(860)                                     # Full ACAL takes 855 seconds
        print ("ACAL ALL DONE")
        tval = intf.read ("ERRSTR?")
        dutinf.append("ACAL ALL result?")
        dutinf.append("%s" % tval[1])
        hp3458_vfd_on("ACAL OK...")
    else:
        dutinf.append("ACAL ALL result?")
        dutinf.append("Not tested")
    
    # Collect all calibration constants
    hp3458_vfd_on("DUMP CAL CONSTS.")
    cvtbl = []
    cix = 1
    print ("Reading CAL constants")
    while cix <= 253:
        #cvtbl.append ("%d" % cix)
        cvtbl.append (intf.read ("CAL? %d,1" % cix) )
        time.sleep(0.001)
        cix = cix + 1
        sys.stdout.write('.')
        sys.stdout.flush()
    
    print ("\r\nREV?")
    tval = intf.read ("REV?")
    dutinf.append("Firmware")
    dutinf.append("%s" % tval[1])
    print ("OPT?")
    tval = intf.read ("OPT?")
    dutinf.append("Options")
    dutinf.append("%s" % tval[1])

    print ("Read CAL? 72")
    tval = intf.read ("CAL? 72")
    dutinf.append("CAL? 72")
    dutinf.append("%s" % tval[1])
    print ("Read CAL? 1,1")
    tval = intf.read ("CAL? 1,1")
    dutinf.append("CAL? 1,1")
    dutinf.append("%s" % tval[1])
    print ("Read CAL? 2,1")
    tval = intf.read ("CAL? 2,1")
    dutinf.append("CAL? 2,1")
    dutinf.append("%s" % tval[1])
    print ("Read CAL? 73")
    tval = intf.read ("CAL? 73")
    dutinf.append("CAL? Res 73")
    dutinf.append("%s" % tval[1])
    
    print ("Read CAL? 58")
    tval = intf.read ("CAL? 58")
    dutinf.append("CAL 0 TEMP")
    cal1temp = float(tval[1])
    dutinf.append("%4.2f" % cal1temp)
    print ("Read CAL? 59")
    tval = intf.read ("CAL? 59")
    dutinf.append("CAL 10V TEMP")
    cal2temp = float(tval[1])
    dutinf.append("%4.2f" % cal2temp)
    print ("Read CAL? 60")
    tval = intf.read ("CAL? 60")
    dutinf.append("CAL 10KOhm TEMP")
    cal3temp = float(tval[1])
    dutinf.append("%4.2f" % cal3temp)
    
    print ("Read CAL? 93")
    tval = intf.read ("CAL? 93")
    dutinf.append("CAL? DCI")
    dutinf.append("%s" % tval[1])
    dutinf.append("CAL DUMP")
    dutinf.append("%s" % cvtbl)
    
    with open(result_log_fn, 'a') as dile:
        dile.write ("\r\n")
        dile.write ("DUT TEMP? : %s" % dut_temp[1])
        dile.write ("\r\nPOST-ACAL DUMP : %s" % cvtbl)
    dile.close()
    
    tval = intf.read ("CAL? 2941")
    dutinf.append("Destructive overloads?")
    dutinf.append("%s" % tval[1])
    hp3458_vfd_on("DUMP CAL DONE :)")    
    
    mfc_out_dis()
    
    return dutinf
    
def hp3458_perfinit():
    print "\033[1;33;44mSetup HPAK 3458A for performance verification"
    print "Connect DMM to the calibrator, HI to DMM HI, LO to DMM LO. Use low-thermal shielded 1m cable"
    print "Allow 5 hour warm-up"
    print "Select DCV Function, 100 NPLC, Manual Range"
    print "Set MFC output to 0mV"
    print "Enable MATH NULL. Leave MATH NULL till DCV test finish\033[1;39;49m"

def hp3458_dczperf(value):
    if (value < 0.9):
        print ("Set MFC to 0 mVDC")
        mfc_output("0 V")
        mfc_out_en()
        hp3458_dcv_conf(value, 100)                     # DCV Function, 0.2V range
        hp3458_set_aver(1)                              # Enable Average filter 
        meter_dorm(5)                                   # 5 second soak
        reading = hp3458_get_meas()
    elif (value > 0.9 and value < 9.0):
        # Range 1V special test
        print ("\r\nSet MFC to 0.0 VDC")
        mfc_output("0 V")
        mfc_out_en()

        hp3458_dcv_conf(value, 100)                     # DCV Function, 0.2V range
        hp3458_set_aver(1)                              # Enable Average filter 
        meter_dorm(9)                                   # 9 s soaking
        minrdg = hp3458_get_meas()
        maxrdg = 0.0
        for ic in range (0,10):
            #Take 50 samples
            reading = hp3458_get_meas()
            if reading < minrdg:
                minrdg = reading
            elif reading > maxrdg:
                maxrdg = reading
            hp3458_vfd_on("Noise test %d" % ic)
        print ("Reading %e, min %e, max %e" % (reading, minrdg, maxrdg))
        noiseval = maxrdg - minrdg
        if (noiseval < 4E-6):
            print "Noise test pass"
            hp3458_vfd_on("Noise test PASS")
        else:
            print ("Noise test fail, value = %f uV" % noiseval)
            hp3458_vfd_on("Noise test FAIL")
        
    elif (value > 9.0):
        print ("\033[1;35mSet MFC to 0 VDC\033[1;39m")
        hp3458_vfd_on("Zero check...")
        hp3458_dcv_conf(value, 100)                     # DCV Function, 0.2V range
        hp3458_set_aver(1)                              # Enable Average filter 
        meter_dorm(9)                                   # 5 s soaking
        reading = hp3458_get_meas()
    return reading
    
def hp3458_dcvperf(value):
    print ("\033[1;35mSet MFC to %.8f VDC\033[1;39m" % value)
    hp3458_vfd_on("DCV %e" % value)
    meter_dorm(10)                                      # 10s soaking
    reading = hp3458_get_meas()
    reading = hp3458_get_meas()
    return reading

def hp3458_dciperf(value):
    print ("\033[1;35mSet MFC to %e ADC\033[1;39m" % value)
    #mfc_output("%E A, 0 Hz" % (value * (1 + mfc_dci_err[value]) ) )
    #mfc_out_en()
    meter_dorm(15)                                      # 15s soaking
    intf.write ("TARM AUTO")
    reading = hp3458_get_meas()
    intf.write ("TRIG SYN")
    reading = hp3458_get_meas()
    return reading

def hp3458_resperf(value):
    print ("Set resistance to %.8E Ohm" % value)
    meter_dorm(15)                                      # 15s soaking
    reading = hp3458_get_meas()
    # Take actual reading
    reading = hp3458_get_meas()
    return reading

def hp3458_1gresperf(value):
    print ("Set resistance to 1GOhm")
    meter_dorm(10)                                      # 10s soaking
    reading = hp3458_get_meas()
    # Take actual reading
    reading = hp3458_get_meas()
    return reading
    
def hp3458_acvperf(value, freq):
    print ("\033[1;36mSet MFC to %9.3f at %7.2f Hz\033[1;39m" % (value, freq) )
    mfc_output("%e V, %e Hz;*CLS;OPER" % (value, freq) )
    mfc_ext_sense(0)
    mfc_out_en()
    meter_dorm(30)
    reading = hp3458_get_meas()
     # Take actual reading
    meter_dorm(2)
    reading = hp3458_get_meas()
    return reading

def hp3458_aciperf(value, freq):
    print ("\033[1;36mSet MFC to %e ACI at %7.2f Hz\033[1;39m" % (value, freq) )
    mfc_output("%e A, %e Hz;*CLS;OPER" % (value, freq) )
    mfc_ext_sense(0)
    mfc_out_en()
    meter_dorm(15)
    print (" ")
    reading = hp3458_get_meas()
     # Take actual reading
    reading = hp3458_get_meas()
    return reading
    
def hp3458_dcztest():
    dcvresult = []
    input_sts = 255
    mfc_output("0 V")
    mfc_out_en()
    print ("\033[1;33;44mConnect 2-wire MFC 0 short on FRONT terminals")
    print ("Number of DCV Zero tests = %d\033[1;39;49m" % len(hp3458_dcz_test_values))
    #raw_input ("\033[1;47mSwitch to FRONT and press ENTER to start test\033[1;49m")
    input_sts = hp3458_check_terminal()
    if (input_sts != int(cfg.get('dut', 'dut_terminal_side', 1)) ):
        print ("\033[1;31m-ERROR- incorrect switch, abort\033[1;39m")
        quit()
    else:
        meter_dorm(300)
        reading = hp3458_get_meas()
        hp3458_vfd_off()
        for testcnt in range (0, len(hp3458_dcz_test_values)):
            dcvresult.append(hp3458_dczperf(hp3458_dcz_test_values[testcnt]))
            print ("DCV Range+1")
            print ("Reset MFC to 0.00000 VDC")
            mfc_output("0 V")
            mfc_out_en()
            reading = hp3458_get_meas()
            print reading
        hp3458_dcv_conf(0.1, 100)
        hp3458_rel(1, 1) # Set REL and ACQ REL
        reading = hp3458_get_meas()
        print reading
        print ("\033[1;33mDCV Zero test complete\033[1;39m")
    return dcvresult
    
def hp3458_dcvtest():
    dcvresult = []
    print ("Number of DCV tests = %d" % len(hp3458_dcv_test_values))
    for testcnt in range (0, len(hp3458_dcv_test_values)):
        mfc_output("%e V;*CLS;OPER" % (hp3458_dcv_test_values[testcnt] * (1 + (mfc_dcv_err[testcnt] * 1E-6) ) ) )
        hp3458_dcv_conf(hp3458_dcv_test_ranges[testcnt],100)
        mfc_ext_sense(0)
        mfc_out_en()
        if testcnt > 12:
            mfc_out_en()
            print ("Settle delay for high voltage 30 sec")
            meter_dorm(30)    
        dcvresult.append(hp3458_dcvperf(hp3458_dcv_test_values[testcnt]))
    print ("Reset MFC to 0.00000 VDC")
    print ("DCV test complete")
    mfc_output("0 V")
    mfc_out_en()
    #hp3458_rel(0, 0) # Set REL and ACQ REL
    return dcvresult

def hp3458_dcltest():
    dclresult = []
    print ("Number of DC Linearity tests = %d" % len(hp3458_dcl_test_values))
    for testcnt in range (0, len(hp3458_dcl_test_values)):
        mfc_output("%e V;*CLS;OPER" % (hp3458_dcl_test_values[testcnt] * (1 + (mfc_dcv_err[4] * 1E-6) ) ) )
        mfc_ext_sense(0)
        mfc_out_en()
        meter_dorm(30)                                  # Allow 30 sec for settle
        dclresult.append(hp3458_dcvperf(hp3458_dcl_test_values[testcnt]))
    print ("Reset MFC to 0.00000 VDC")
    print ("DC Linearity test complete")
    mfc_output("0 V")
    mfc_out_en()
    hp3458_rel(0, 0) # Set REL and ACQ REL
    return dclresult
    
def hp3458_dcitest():
    dciresult = []
    print ("\033[1;33;44mConnect MFC AUX HI output to CURR IN DMM and MFC LO output to DMM LO")
    print ("Select DCI, FILTER 10 AVER, 10 NPLC, manual range")
    print ("Number of DCI tests = %d\033[1;39;49m" % len(hp3458_dci_test_values))
    hp3458_vfd_on("CONNECT DCI JACK")
    mfc_curr_post(2)  
    #raw_input("\033[1;47mConnect Current MFC to DMM on FRONT\033[1;49m\r")
    # Null MFC
    mfc_output("0 A, 0 Hz")
    meter_dorm(25)
    hp3458_dci_conf(100E-9, 100)
    intf.write ("TARM AUTO")
    intf.write ("TRIG AUTO")
    hp3458_rel(1, 1) # Set REL and ACQ REL
    print ("Null DCI = %f uA" % (hp3458_get_meas() * 1E6))
    meter_dorm(5)
    for testcnt in range (0, len(hp3458_dci_test_values)):
        mfc_output("%e A, 0 Hz" % (hp3458_dci_test_values[testcnt] * (1 - (mfc_dci_err[testcnt] * 1E-6) ) ) )        
        mfc_out_en()
        hp3458_dci_conf(hp3458_dci_test_values[testcnt], 100)
        #hp3458_vfd_on("DCI %s" % hp3458_dci_tstr_values[testcnt])
        meter_dorm(5)
        dciresult.append(hp3458_dciperf(hp3458_dci_test_values[testcnt]))
    print ("Reset MFC to 0.00000 ADC")
    print ("DCI test complete")
    hp3458_rel(0, 0) # Reset REL and ACQ REL
    mfc_output("0 A, 0 Hz")
    mfc_out_dis()
    return dciresult

def hp3458_acztest():
    aczresult = []
    time.sleep(1)
    print "ACZ TEST"
    return aczresult

def hp3458_ana_acvtest():
    acvresult = []
    print ("\033[1;35;44mDisabled REL, mode - ANA")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Number of ACV tests = %d\033[1;39;49m" % len(hp3458_acv_test_values))
    for testcnt in range (0, len(hp3458_acv_test_values)):
        # Iterate frequencies
        print ("\r")
        for testfcnt in range (0, len(hp3458_acv_test_fvalue)):
	    # Iterate voltages
            if ((testcnt == 0) and (testfcnt > 2)) or (testcnt == 1):
        	if (testfcnt >= 3):
		    intf.write ("LFILTER OFF")
		else:
		    intf.write ("LFILTER ON")
                hp3458_acv_conf(hp3458_acv_test_values[testcnt], "ANA")
                acvresult.append(hp3458_acvperf(hp3458_acv_test_values[testcnt],hp3458_acv_test_fvalue[testfcnt]))
                acvresult.append(hp3458_acv_test_fvalue[testfcnt])
    #print ("Reset MFC to 0.00000 VAC")
    print ("ACV test complete")
    return acvresult

def hp3458_sync_acvtest():
    acvresult = []
    print ("Disable REL, mode - SYNC")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Number of ACV tests = %d" % len(hp3458_acvs_test_values))
    for testcnt in range (0, len(hp3458_acvs_test_values)):
        # Iterate frequencies
        print ("\r")
        for testfcnt in range (0, len(hp3458_acvs_test_fvalue)):
            # Iterate voltages
	    if ( ( (testcnt < 4) ) or ( (testcnt == 4) and (testfcnt >= 4) and (testfcnt <= 8 ) ) or ( (testcnt > 4) and (testfcnt == 4) ) ):
        	if (testfcnt >= 7):
		    intf.write ("LFILTER OFF")
		else:
		    intf.write ("LFILTER ON")
                hp3458_acv_conf(hp3458_acvs_test_values[testcnt], "SYNC")
                acvresult.append(hp3458_acvperf(hp3458_acvs_test_values[testcnt],hp3458_acvs_test_fvalue[testfcnt]))
                acvresult.append(hp3458_acvs_test_fvalue[testfcnt])
    print ("Reset MFC to 0.00000 VAC")
    mfc_output("0 V, 0 Hz;*CLS;STBY")
    mfc_ext_sense(0)
    mfc_out_dis()
    return acvresult
    
def hp3458_acitest():
    aciresult = []
    mfc_curr_post(2)  # AUX output from MFC
    print ("Disable REL, mode - SYNC")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Number of ACI tests = %d" % len(hp3458_aci_test_values))
    for testfcnt in range (0, len(hp3458_aci_test_fvalue)):
        # Iterate frequencies
        print ("\r")
        for testcnt in range (0, len(hp3458_aci_test_values)):
            # Iterate voltages
            hp3458_aci_conf(hp3458_aci_test_values[testcnt], "SYNC")
            aciresult.append(hp3458_aciperf(hp3458_aci_test_values[testcnt],hp3458_aci_test_fvalue[testfcnt]))
            aciresult.append(hp3458_aci_test_fvalue[testfcnt])
    print ("Reset MFC to 0.00000 ACI")
    mfc_output("0 A, 0 Hz;*CLS;STBY")
    mfc_ext_sense(0)
    mfc_out_dis()
    return aciresult

def hp3458_reztest():
    rezresult = []
    # Rear 4W short test
    mfc_output("0 OHM")
    mfc_ext_sense(1)
    mfc_out_en()
    input_sts = 255
    hp3458_vfd_on("CONNECT 4W JACKS")
    #raw_input ("\033[1;31m\033[1;47mSelect REAR SHORT 4W terminals and press ENTER\033[1;39m\033[1;49m")
    input_sts = hp3458_check_terminal()
    print input_sts
    if (input_sts != int(cfg.get('dut', 'dut_terminal_side', 1)) ):
        print ("\033[1;31m-ERROR- incorrect switch, abort\033[1;39m")
        quit()
    else:
        print ("Number of REZ REAR tests = %d" % len(hp3458_rez_test_values))
        reading = hp3458_get_meas()
        for testcnt in range (0, len(hp3458_rez_test_values)):
            hp3458_ocomp(1,1)
            hp3458_fres_conf(hp3458_rez_test_values[testcnt], 0)
            meter_dorm(10)
            rezresult.append(hp3458_resperf(hp3458_rez_test_values[testcnt]))
    print ("RES 4W REAR Zero test complete")
    return rezresult

def hp3458_unc_reztest():
    urezresult = []
    # Rear 4W short test
    mfc_output("0 OHM")
    mfc_ext_sense(1)
    for testcnt in range (0, len(hp3458_rez_test_values)):
        urezresult.append(5E-5)
    return urezresult

def hp3458_unc_restest():
    uresresult = []
    for testcnt in range (0, len(hp3458_res_test_values)):
        mfc_ext_sense(0)
        mfc_output("%f OHM\n" % hp3458_res_test_values[testcnt])
        uresresult.append(mfc_uncert() )
    return uresresult

def hp3458_unc_dcvtest():
    udcvresult = []
    for testcnt in range (0, len(hp3458_dcv_test_values)):
        mfc_output("%e V;*CLS;STBY" % hp3458_dcv_test_values[testcnt])
        mfc_ext_sense(0)
        udcvresult.append(mfc_uncert() )
    print ("Reset MFC to 0.00000 VDC")
    mfc_output("0 V")
    return udcvresult

def hp3458_unc_dcitest():
    udciresult = []
    mfc_curr_post(2)
    for testcnt in range (0, len(hp3458_dci_test_values)):
        mfc_output("%e A" % hp3458_dci_test_values[testcnt] * (1 + (mfc_dci_err[testcnt] * 1E-6) ) )
        mfc_out_dis()
        udciresult.append(mfc_uncert() )
    mfc_output("0 A")
    mfc_out_dis()
    return udciresult

def hp3458_unc_acatest():
    uacaresult = []
    for testcnt in range (0, len(hp3458_acv_test_values)):
        # Iterate frequencies
        print ("\r")
        for testfcnt in range (0, len(hp3458_acv_test_fvalue)):
            # Iterate voltages
            if ( ( (testcnt < 4) ) or ( (testcnt == 4) and (testfcnt >= 4) and (testfcnt <= 8 ) ) or ( (testcnt > 4) and (testfcnt == 4) ) ):
                mfc_output("%e V, %e Hz;*CLS;STBY" % (hp3458_acv_test_values[testcnt], hp3458_acv_test_fvalue[testfcnt]) )
                mfc_ext_sense(0)
                uacaresult.append(mfc_uncert() )
                uacaresult.append(hp3458_acv_test_fvalue[testfcnt])
    print ("Reset MFC to 0.00000 VAC")
    mfc_output("0 V;*CLS;STBY")
    mfc_ext_sense(0)
    mfc_out_dis()
    return uacaresult

def hp3458_unc_acvtest():
    uacvresult = []
    for testcnt in range (0, len(hp3458_acvs_test_values)):
        # Iterate frequencies
        print ("\r")
        for testfcnt in range (0, len(hp3458_acvs_test_fvalue)):
            # Iterate voltages
            if ( ( (testcnt < 4) ) or ( (testcnt == 4) and (testfcnt >= 4) and (testfcnt <= 8 ) ) or ( (testcnt > 4) and (testfcnt == 4) ) ):
                mfc_output("%e V, %e Hz;*CLS;STBY" % (hp3458_acvs_test_values[testcnt], hp3458_acvs_test_fvalue[testfcnt]) )
                mfc_ext_sense(0)
                uacvresult.append(mfc_uncert() )
                uacvresult.append(hp3458_acvs_test_fvalue[testfcnt])
    print ("Reset MFC to 0.00000 VAC")
    mfc_output("0 V;*CLS;STBY")
    mfc_ext_sense(0)
    mfc_out_dis()
    return uacvresult
    
def hp3458_unc_acitest():
    uaciresult = []
    for testcnt in range (0, len(hp3458_aci_test_values)):
        # Iterate frequencies
        print ("\r")
        for testfcnt in range (0, len(hp3458_aci_test_fvalue)):
            # Iterate voltages
            if ( ( (testcnt < 4) ) or ( (testcnt == 4) and (testfcnt >= 4) and (testfcnt <= 8 ) ) or ( (testcnt > 4) and (testfcnt == 4) ) ):
                mfc_output("%e A, %e Hz;*CLS;STBY" % (hp3458_aci_test_values[testcnt], hp3458_aci_test_fvalue[testfcnt]) )
                mfc_ext_sense(0)
                uaciresult.append(mfc_uncert() )
                uaciresult.append(hp3458_aci_test_fvalue[testfcnt])
    print ("Reset MFC to 0.00000 ACI")
    mfc_output("0 A;*CLS;STBY")
    mfc_ext_sense(0)
    mfc_out_dis()
    return uaciresult

    
def hp3458_restest():
    resresult = []
    print ("\033[1;33;44mConnect MFC H/L/S+/S- output to DMM H/L/S+/S-")
    print ("Select 4W Res, FILTER 10 AVER, 10 NPLC, OCOMP ON, manual range")
    print ("Select external sense ON at MFC, switch DMM to FRONT")
    print ("OCOMP cannot be used on ranges >10 MOhm")
    print ("Number of RES tests = %d\033[1;39;49m" % len(hp3458_res_test_values))
    # Rear 4W short test
    #raw_input("\033[1;47mPress ENTER once switch MFC-DMM 4W terminals to FRONT\033[1;49m\n")
    tmpval = 0.0
    input_sts = 255
    input_sts = hp3458_check_terminal()    
    if (input_sts != int(cfg.get('dut', 'dut_terminal_side', 1)) ):
        print ("-ERROR- incorrect switch, abort")
        quit()
    else:
        for testcnt in range (0, len(hp3458_res_test_values)):
            hp3458_vfd_off() #("R %e" % hp3458_res_test_values[testcnt])
	    intf.write ("DELAY 3")
            if (testcnt > 15):
                # 100 Meg resistors use 2W
                hp3458_ocomp(0,0)
                mfc_ext_sense(0)
                mfc_output("%f OHM\n" % hp3458_res_test_values[testcnt])
                mfc_out_en()
                hp3458_res_conf(hp3458_res_test_ranges[testcnt], 100)
                meter_dorm(20)
                tmpval = hp3458_resperf(hp3458_res_test_values[testcnt])
                resresult.append(tmpval)
            else:
                mfc_ext_sense(1)
                hp3458_ocomp(1,2)
                mfc_output("%f OHM\n" % hp3458_res_test_values[testcnt])
                mfc_out_en()
                mfc_ext_sense(1)
                hp3458_fres_conf(hp3458_res_test_values[testcnt], 100)
                meter_dorm(10) # soak 10sec
                tmpval = hp3458_resperf(hp3458_res_test_values[testcnt])
                resresult.append(tmpval)
	    intf.write ("DELAY 0")
    print ("Reset MFC to 0.0000 RES")
    print ("\033[1;32mRES test complete\033[1;39m")
    return resresult

def hp3458_1grtest():
    resresult = []
    print ("\033[1;31;44mConnect 1G Resistor H/L output to DMM H/L")
    print ("Select 2W Res, FILTER 10 AVER, 10 NPLC, manual range\033[1;39;49m")
    raw_input("\033[1;47mPress ENTER once switch DMM 2W terminals connected FRONT 1GOHM RES STD\033[1;49m\n")
    tmpval = 0.0
    hp3458_ocomp(0,0)
    hp3458_res_conf(1E9, 100)
    tmpval = hp3458_1gresperf(hp3458_1g_test_value[0])
    resresult.append(tmpval)
    print ("\033[1;31;44m1G RES test complete\033[1;39;44m")
    raw_input("\033[1;47mPress ENTER once switch MFC-DMM 2W DCV terminals to FRONT\033[1;49m\n")
    return resresult
    
def hp3458_perftest():
    dutresult = []
    uncresult = [] #uncertainty storage array

    print ("\033[1;31m HP 3458B verification \033[1;39m")
    hp3458_dutinit()
    hp3458_vfd_on("CALKIT START...")
    dutresult.append(hp3458_reztest())                                          #0
    #uncresult.append(hp3458_unc_reztest())                                     #0
    #dutresult.append([4.478912428e-06, -0.0003055148977])
    uncresult.append([50E-6, 50E-6]) # 50 uOhm

    hp3458_vfd_off()
    hp3458_vfd_on("RES 4W TEST...")
    dutresult.append(hp3458_restest())                                          #1
    #uncresult.append(hp3458_unc_restest())                                      #1
    #dutresult.append([0.9997985801, 9.999892367, 100.0017144, 999.991323, 10000.07481, 100001.0786, 999996.3291, 9998988.073, 100013331.7])
    uncresult.append([40.2, 8.3, 8.3, 4.3, 4.3, 3.3, 3.3, 3.3, 3.3, 3.3, 3.3, 5.3, 5.3, 14.3, 14.3, 60.3, 60.3])

    hp3458_vfd_on("RES 1G TEST...")
    #dutresult.append(hp3458_1grtest())                                         #2
    dutresult.append([1E9])                                             #2
    uncresult.append([30000])                                                   #2
    
    hp3458_dcv_conf(10,100)
    hp3458_vfd_on("DCV ZERO TEST.")
    dutresult.append(hp3458_dcztest())                                          #3
    #dutresult.append([4.763534132e-07, 4.85077892e-07, 1.103170269e-06, 6.304967951e-06, 7.180166681e-05])
    uncresult.append([8.23, 3.95, 3.32, 4.36, 6.45])                            #3

    hp3458_vfd_on("DCV TEST...")
    dutresult.append(hp3458_dcvtest())                                          #4
    #uncresult.append(hp3458_unc_dcvtest())                                     #4
    #dutresult.append([0.09999962475, -0.09999990745, 1.000000069, -1.00000003, 9.999998402, -9.999997538, 99.999966, -99.9999476, 999.9998248, -1000.000693])
    uncresult.append([3.81, 3.81, 
    2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 
    1.47, 1.47, 1.47, 1.47, 1.47, 1.47,
    2.36, 2.36, 2.36, 2.36, 2.36, 2.36,
    2.85, 2.85, 2.85, 2.85, 2.85, 2.85]) #0 Relative 24h
    
    hp3458_vfd_on("LIN DCV TEST..")
    hp3458_dcv_conf(10,100)
    dutresult.append(hp3458_dcltest()) #5
    #uncresult.append(hp3458_unc_dcvtest()) #5
    #dutresult.append([10.99999866, 9.999997824, 8.888887496, 7.777776993, 6.666665824, 5.555555058, 4.444444572, 3.333333649, 2.222222533, 1.111111157, 0.1234564153, -0.1234566356, -1.111111064, -2.222221844, -3.333332488, -4.444443271, -5.555553529, -6.666664067, -7.777774973, -8.888885617, -9.99999605, -10.99999784])
    uncresult.append([1.47, 1.47, 1.47, 1.47, 1.47,1.47,1.47,1.47,1.47,2.45,9.91,9.91,2.45,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47]) #5 Relative 24h
    
    #dutresult.append(hp3458_acztest()) #5
    #uncresult.append([0, 0, 0, 0, 0]) #0
    
    hp3458_vfd_on("ACV ANA TEST")
    
    dutresult.append(hp3458_ana_acvtest()) #6
    #uncresult.append(hp3458_unc_acatest()) #6
    #dutresult.append([1.000133767, 50000.0, 1.015303615, 1000000.0, 9.982167458, 10, 10.00086771, 200, 10.00084673, 500, 10.00062784, 50000.0, 10.13601703, 1000000.0])
    uncresult.append([129.09, 50000.0, 2500, 1000000.0, 2085, 10, 73.18, 200, 73.18, 500, 129.09, 50000.0, 3000, 1000000.0]) #6
    
    hp3458_vfd_on("ACVSYNC TEST")
    dutresult.append(hp3458_sync_acvtest()) #7
    #uncresult.append(hp3458_unc_acvtest()) #7
    #dutresult.append([0.01001009073, 10, 0.01001129379, 20, 0.01000985939, 40, 0.01001293284, 100, 0.01001084955, 1000.0, 0.01001277555, 10000.0, 0.01001105468, 20000.0, 0.01001029201, 50000.0, 0.009990519809, 100000.0, 0.00985370409, 300000.0, 0.009642847661, 500000.0, 0.008824326959, 1000000.0, 0.1000207317, 10, 0.10001201, 20, 0.1000172667, 40, 0.1000107692, 100, 0.1000175371, 1000.0, 0.1000168862, 10000.0, 0.1000161767, 20000.0, 0.1000077259, 50000.0, 0.09995437047, 100000.0, 0.0997753582, 300000.0, 0.09965616663, 500000.0, 0.099833206, 1000000.0, 1.000103165, 10, 1.00002157, 20, 1.000000967, 40, 0.9999884152, 100, 1.000027101, 1000.0, 0.9999318484, 10000.0, 0.9999336983, 20000.0, 0.9999705276, 50000.0, 1.000038094, 100000.0, 1.001183795, 300000.0, 1.003289516, 500000.0, 1.009893943, 1000000.0, 10.00105643, 10, 10.00040488, 20, 10.00026715, 40, 10.00015635, 100, 10.00020428, 1000.0, 9.999639694, 10000.0, 9.999638942, 20000.0, 9.999438775, 50000.0, 9.996622026, 100000.0, 9.988689597, 300000.0, 10.0030354, 500000.0, 10.08911275, 1000000.0, 100.0036052, 1000.0, 100.001728, 10000.0, 100.0002819, 20000.0, 100.0027668, 50000.0, 99.98938932, 100000.0, 700.0453319, 1000.0])
    uncresult.append([372.33, 10, 372.33, 20, 372.33, 40, 372.33, 100, 372.33, 1000.0, 372.33, 10000.0, 372.33, 20000.0, 612.73, 50000.0, 1200, 100000.0, 1800, 300000.0, 2900, 500000.0, 4400, 1000000.0, 
                      422.72, 10, 206.36, 20, 206.36, 40, 121.36, 100, 121.36, 1000.0, 121.36, 10000.0, 121.36, 20000.0, 345.45, 50000.0, 886.36, 100000.0, 1100, 300000.0, 1700, 500000.0, 3500, 1000000.0, 
                      436.36, 10, 141.36, 20, 141.36, 40, 62.72, 100, 62.72, 1000.0, 62.72, 10000.0, 62.72, 20000.0, 129.09, 50000.0, 266.36, 100000.0, 468.18, 300000.0, 1200, 500000.0, 2500, 1000000.0, 
                      403.63, 10, 141.36, 20, 141.36, 40, 62.72, 100, 62.72, 1000.0, 62.72, 10000.0, 62.72, 20000.0, 129.09, 50000.0, 248.18, 100000.0, 577.27, 300000.0, 1400, 500000.0, 3000, 1000000.0, 
                      65.00, 1000.0, 65.00, 10000.0, 65.00, 20000.0, 170.02, 50000.0, 400.03, 100000.0, 
                      78.64, 1000.0]
    ) #6
    
    hp3458_vfd_on("DCI TEST...")
    meter_dorm(5)
    intf.write ("DELAY 0")
    intf.write ("NRDGS 1,1")
    intf.write ("DCI 1E-6")
    dutresult.append(hp3458_dcitest()) #8
    #uncresult.append(hp3458_unc_dcitest()) #8
    uncresult.append([   71.36,       71.36,   71.36,     71.36,     71.36,      71.36,      71.36,       71.36,     38.63,      38.63,    38.63,     38.63,   48.63, 48.63,  71.36,   71.36]) #0
    #dutresult.append([9.797747786e-08, -1.019717023e-07, 9.980116471e-07, -1.001983866e-06, 9.997907828e-06, -1.000188373e-05, 0.00010001223, -0.00010001693, 0.0010000669, -0.0010000862, 0.009999949, -0.01000016, 0.1000078, -0.10001004, 0.9995889, -0.9995474])
    
    hp3458_vfd_on("ACI TEST...")
    dutresult.append(hp3458_acitest()) #9
    #uncresult.append(hp3458_unc_acitest()) #9
    #dutresult.append([1E-6, 50, 1E-5, 50, 1E-4, 50, 1E-3, 50, 1E-2, 50, 1E-1, 50, 1.0, 50, 1E-6, 60, 1E-5, 60, 1E-4, 60, 1E-3, 60, 1E-2, 60, 1E-1, 60, 1.0, 60, 1E-6, 1000, 1E-5, 1000, 1E-4, 1000, 1E-3, 1000, 1E-2, 1000, 1E-1, 1000, 1.0, 1000,]) #9
    uncresult.append([210.91, 50, 210.91, 50, 210.91, 50, 138.18, 50, 138.18, 50, 138.18, 50, 618.18, 50, 210.91, 60, 210.91, 60, 210.91, 60, 138.180, 60, 138.18, 60, 138.18, 60, 618.18, 60, 210.91, 1000.0, 210.91, 1000.0, 210.91, 1000.0, 138.18 , 1000.0,138.18, 1000.0,138.18, 1000.0, 618.18, 1000.0]) #9
    
    #dutresult.append(hp3458_pkacvtest())
    #dutresult.append(hp3458_acitest())
    #dutresult.append(hp3458_freqtest())

    with open(result_log_fn, 'a') as dile:
        for ival in xrange (0, len(dutresult)):
            dile.write ("\r\n%d %s" % (ival, dutresult[ival]))
        dile.write ("\r\n")
    dile.close()
    print ("\033[1;32;44mPERF CHECK DONE!\033[1;39;49m")
    hp3458_vfd_on(" (,,)=(^.^)=(,,)")
    
    return uncresult, dutresult

def hp3458_perftestdbg():
    dutresult = []
    uncresult = [] #uncertainty storage array

    print ("\033[1;31m DEBUG HP 3458A verification \033[1;39m")
    hp3458_dutinit()
    hp3458_vfd_on("CALKIT START...")
    #dutresult.append(hp3458_reztest()) #0
    #uncresult.append(hp3458_unc_reztest()) #0
    #B dutresult.append([-1.632095529e-05, 0.0004672542321])
    dutresult.append([-7.869195985e-06, -1.793701716e-05])
    uncresult.append([50E-6, 50E-6]) # 50 uOhm
    
    hp3458_vfd_off()
    hp3458_vfd_on("RES 4W TEST...")
    #dutresult.append(hp3458_restest()) #1
    #uncresult.append(hp3458_unc_restest()) #1
    #B dutresult.append([0.9998222762, 1.899516835, 10.0000845, 18.99906096, 100.0012713, 189.9920511, 999.920552, 1899.870085, 9999.12546, 18997.96145, 99990.22764, 189997.3958, 999760.1893, 1899584.462, 9983618.398, 18950279.68, 99990823.36]) #1
    dutresult.append([0.9998213786, 1.899549639, 10.00010609, 18.99912178, 100.0013818, 189.9923688, 999.9213292, 1899.872104, 9999.126248, 18997.99411, 99989.91852, 189997.6917, 999725.7102, 1899493.579, 9980116.179, 18937420.65, 99994019.76])
    uncresult.append([40.2, 8.3, 8.3, 4.3, 4.3, 3.3, 3.3, 3.3, 3.3, 3.3, 3.3, 5.3, 5.3, 14.3, 14.3, 60.3, 60.3])

    hp3458_vfd_on("RES 1G TEST...")
    #dutresult.append(hp3458_1grtest()) #2
    dutresult.append([1000000000.0])    #2
    uncresult.append([30000]) #0
    hp3458_dcv_conf(10,100)

    hp3458_vfd_on("DCV ZERO TEST.")
    #dutresult.append(hp3458_dcztest()) #3
    #B dutresult.append([8.049798492e-08, 1.120757088e-07, 6.478942273e-07, -1.436133445e-05, 5.078667822e-05]) #3
    dutresult.append([8.531043832e-09, 1.244713793e-08, 1.600631049e-07, 6.045622699e-06, 2.845505119e-05])    #3
    uncresult.append([8.23, 3.95, 3.32, 4.36, 6.45]) #0

    hp3458_vfd_on("DCV TEST...")
    #dutresult.append(hp3458_dcvtest()) #4
    #B dutresult.append([0.09999961656, -0.09999972989, 0.09999965873, 0.1999993202, 0.9999990725, -0.0999997623, -0.1999995621, -0.9999976718, 0.9999995515, 1.999996572, 9.99997981, -0.9999971511, -1.999994224, -9.999977095, 9.999977965, 19.99994695, 99.99973213, -9.999992062, -19.99994897, -99.99994992, 99.99978555, 199.999536, 1000.000592, -100.0000954, -199.9997338, -1000.000582]) #4
    dutresult.append([0.09999968368, -0.09999973558, 0.09999973778, 0.1999993308, 0.9999973556, -0.09999949635, -0.1999993615, -0.9999972386, 0.9999981471, 1.999994512, 9.999974053, -0.999997623, -1.999994361, -9.999975734, 9.999995039, 19.99995001, 99.99969134, -9.999957761, -19.99991949, -99.9999727, 99.99974686, 199.9995075, 1000.000065, -100.0001017, -199.9998019, -1000.000021])
    #uncresult.append(hp3458_unc_dcvtest()) #0
    uncresult.append([3.81, 3.81, 
    2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 
    1.47, 1.47, 1.47, 1.47, 1.47, 1.47,
    2.36, 2.36, 2.36, 2.36, 2.36, 2.36,
    2.85, 2.85, 2.85, 2.85, 2.85, 2.85]) #0 Relative 24h
    
    hp3458_vfd_on("LIN DCV TEST..")
    hp3458_dcv_conf(10,100)
    #dutresult.append(hp3458_dcltest()) #5
    #B dutresult.append([10.99997035, 9.999978847, 8.888871084, 7.777761814, 6.666654086, 5.555545271, 4.444436965, 3.333327328, 2.222218584, 1.111110014, 0.1234569024, -0.1234560254, -1.111107929, -2.222217041, -3.333325242, -4.444434564, -5.555542941, -6.666651212, -7.777759519, -8.88886814, -9.999976342, -10.99996631]) #5
    dutresult.append([10.99996489, 9.999974568, 8.888866327, 7.777759099, 6.666651053, 5.555542954, 4.444434499, 3.333325191, 2.222217145, 1.111108744, 0.1234567837, -0.1234560106, -1.111108468, -2.22221719, -3.333325289, -4.444434544, -5.555543035, -6.666651152, -7.777759251, -8.888867955, -9.999976303, -10.99996449])
    #dutresult.append([0.09999950382, -0.0999999126, 1.000000633, -1.0000007998, 10.00000459, -10.0000053779, 100.0001559, -100.00000149, 1000.001192, -1000.002446])
    #uncresult.append(hp3458_unc_dcvtest()) #5
    #                 0
    uncresult.append([1.47, 1.47, 1.47, 1.47, 1.47,1.47,1.47,1.47,1.47,2.45,3.81,3.81,2.45,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47,1.47]) #5 Relative 24h
    
    hp3458_vfd_on("ACV ANA TEST")
    #dutresult.append(hp3458_acztest()) #5
    #uncresult.append([0, 0, 0, 0, 0]) #0
    
    #dutresult.append(hp3458_ana_acvtest()) #6
    #B dutresult.append([1.000106382, 50000.0, 1.013394896, 1000000.0, 9.981687393, 10, 10.00062949, 200, 10.00062002, 500, 10.0006338, 50000.0, 10.09996017, 1000000.0]) #6
    dutresult.append([0.9998578215, 50000.0, 1.010872553, 1000000.0, 9.984042881, 10, 10.00072272, 200, 10.00070432, 500, 9.997450179, 50000.0, 10.07425134, 1000000.0])
    #uncresult.append(hp3458_unc_acatest()) #6
    uncresult.append([129.09, 50000.0, 2500, 1000000.0, 2085, 10, 73.18, 200, 73.18, 500, 129.09, 50000.0, 3000, 1000000.0]) #6
    
    hp3458_vfd_on("ACVSYNC TEST")
    #dutresult.append(hp3458_sync_acvtest()) #7
    #B dutresult.append([0.0100015231, 10, 0.01000023711, 20, 0.01000041416, 40, 0.009999784661, 100, 0.009999990969, 1000.0, 0.01000153789, 10000.0, 0.01000070886, 20000.0, 0.00999927365, 50000.0, 0.009984862572, 100000.0, 0.009835951131, 300000.0, 0.009629338057, 500000.0, 0.008785228589, 1000000.0, 0.1000013961, 10, 0.09999724663, 20, 0.09999445947, 40, 0.09999487501, 100, 0.09999313939, 1000.0, 0.09999701366, 10000.0, 0.09998932327, 20000.0, 0.09998791024, 50000.0, 0.09994741659, 100000.0, 0.09975022412, 300000.0, 0.09957654009, 500000.0, 0.09942633687, 1000000.0, 1.000095797, 10, 1.000027968, 20, 1.0000095, 40, 1.000004164, 100, 1.000020619, 1000.0, 0.999969825, 10000.0, 0.9999266071, 20000.0, 0.9999913438, 50000.0, 1.000063185, 100000.0, 1.0012422, 300000.0, 1.003105831, 500000.0, 1.008299676, 1000000.0, 10.00068263, 10, 10.00028001, 20, 10.00013483, 40, 10.0000881, 100, 10.00023915, 1000.0, 9.999815005, 10000.0, 9.999793537, 20000.0, 9.999675925, 50000.0, 9.996766924, 100000.0, 9.98745063, 300000.0, 9.99666564, 500000.0, 10.05493036, 1000000.0, 100.0030279, 1000.0, 100.001166, 10000.0, 99.99858283, 20000.0, 100.0053119, 50000.0, 100.0055856, 100000.0, 700.0199699, 1000.0]) #7
    dutresult.append([0.01000167601, 10, 0.01000164758, 20, 0.01000111709, 40, 0.01000130012, 100, 0.01000071174, 1000.0, 0.01000241527, 10000.0, 0.0100018826, 20000.0, 0.01000041724, 50000.0, 0.009985848219, 100000.0, 0.009846464269, 300000.0, 0.009629828414, 500000.0, 0.008699124408, 1000000.0, 0.1000039254, 10, 0.09999994229, 20, 0.09999860568, 40, 0.09999844639, 100, 0.09999980463, 1000.0, 0.09999918515, 10000.0, 0.09999593227, 20000.0, 0.09999136861, 50000.0, 0.09996038454, 100000.0, 0.09981288365, 300000.0, 0.09964866145, 500000.0, 0.0995713195, 1000000.0, 1.000100398, 10, 1.000054635, 20, 1.000041087, 40, 1.000032276, 100, 1.00006642, 1000.0, 1.000087725, 10000.0, 1.000038328, 20000.0, 1.000072416, 50000.0, 1.000097681, 100000.0, 1.001125673, 300000.0, 1.00258523, 500000.0, 1.008108537, 1000000.0, 10.00122579, 10, 10.00061396, 20, 10.00048564, 40, 10.00045532, 100, 10.00057645, 1000.0, 9.999921535, 10000.0, 9.999689791, 20000.0, 9.999356038, 50000.0, 9.996047244, 100000.0, 9.981823311, 300000.0, 9.983674145, 500000.0, 10.04860533, 1000000.0, 100.0049634, 1000.0, 100.0029027, 10000.0, 100.0005335, 20000.0, 100.0087674, 50000.0, 100.0172226, 100000.0, 699.9061257, 1000.0])
    #uncresult.append(hp3458_unc_acvtest()) #7
    uncresult.append([372.33, 10, 372.33, 20, 372.33, 40, 372.33, 100, 372.33, 1000.0, 372.33, 10000.0, 372.33, 20000.0, 612.73, 50000.0, 1200, 100000.0, 1800, 300000.0, 2900, 500000.0, 4400, 1000000.0, 
                      422.72, 10, 206.36, 20, 206.36, 40, 121.36, 100, 121.36, 1000.0, 121.36, 10000.0, 121.36, 20000.0, 345.45, 50000.0, 886.36, 100000.0, 1100, 300000.0, 1700, 500000.0, 3500, 1000000.0, 
                      436.36, 10, 141.36, 20, 141.36, 40, 62.72, 100, 62.72, 1000.0, 62.72, 10000.0, 62.72, 20000.0, 129.09, 50000.0, 266.36, 100000.0, 468.18, 300000.0, 1200, 500000.0, 2500, 1000000.0, 
                      403.63, 10, 141.36, 20, 141.36, 40, 62.72, 100, 62.72, 1000.0, 62.72, 10000.0, 62.72, 20000.0, 129.09, 50000.0, 248.18, 100000.0, 577.27, 300000.0, 1400, 500000.0, 3000, 1000000.0, 
                      65.00, 1000.0, 65.00, 10000.0, 65.00, 20000.0, 170.02, 50000.0, 400.03, 100000.0, 
                      78.64, 1000.0]
    ) #6
    
    hp3458_vfd_on("DCI TEST...")
    #B dutresult.append([9.961119542e-08, -1.003571169e-07, 9.996181302e-07, -1.000299119e-06, 9.999533665e-06, -1.000012527e-05, 9.999843527e-05, -9.999861126e-05, 0.0009999925497, -0.0009999965832, 0.009999955773, -0.01000002366, 0.099996097, -0.09999698799, 0.9999600846, -0.9999854667])
    dutresult.append([9.965140072e-08, -1.00242012e-07, 9.997784166e-07, -1.000164988e-06, 9.999689455e-06, -9.999919887e-06, 9.999856559e-05, -9.999819527e-05, 0.0009999835001, -0.000999983595, 0.009999860626, -0.009999914209, 0.09999650516, -0.09999833064, 0.9999403393, -0.999944663])
    uncresult.append([   71.36,       71.36,   71.36,     71.36,     71.36,      71.36,      71.36,       71.36,     38.63,      38.63,    38.63,     38.63,   48.63, 48.63,  71.36,   71.36]) #0
    #dutresult.append(hp3458_dcitest()) #8
    #uncresult.append(hp3458_unc_dcitest()) #8
    
    hp3458_vfd_on("ACI TEST...")
    #B dutresult.append([1.002864861e-05, 50, 0.0001000012005, 50, 0.001000631051, 50, 0.01000039222, 50, 0.100005902, 50, 1.000002535, 50, 1.000250975e-05, 60, 9.997823942e-05, 60, 0.001000616097, 60, 0.01000076687, 60, 0.1000085047, 60, 1.00002856, 60, 1.002774409e-05, 1000.0, 9.999287728e-05, 1000.0, 0.001000722093, 1000.0, 0.01000126535, 1000.0, 0.1000154991, 1000.0, 1.000155371, 1000.0]) #9
    dutresult.append([1.002524268e-05, 50, 9.999765553e-05, 50, 0.001000734788, 50, 0.01000012268, 50, 0.1000041308, 50, 0.999862359, 50, 1.001050869e-05, 60, 9.999649412e-05, 60, 0.001000713539, 60, 0.01000046859, 60, 0.1000066867, 60, 0.9998932327, 60, 1.002516306e-05, 1000.0, 9.999037279e-05, 1000.0, 0.00100082754, 1000.0, 0.01000096682, 1000.0, 0.1000135478, 1000.0, 0.9999992116, 1000.0])
    #dutresult.append(hp3458_acitest()) #9
    uncresult.append([71, 50, 72, 50, 10, 50, 100, 50, 1000, 50, 1000, 50, 200, 50, 0.0, 60, 0.0, 60, 0.0, 60, 0.0, 60, 0.0, 60, 0.0, 60, 0.0, 60, 0.0, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 0.0, 1000.0]) #9
    #uncresult.append(hp3458_unc_acitest()) #9

    #dutresult.append(hp3458_pkacvtest())
    #dutresult.append(hp3458_acitest())
    #dutresult.append(hp3458_freqtest())

    with open(result_log_fn, 'a') as dile:
        for ival in xrange (0, len(dutresult)):
            dile.write ("\r\n%d %s" % (ival, dutresult[ival]))
        dile.write ("\r\n")
    dile.close()
    print ("PERF CHECK DONE!")
    hp3458_vfd_on("PERF DONE :)")
    
    return uncresult, dutresult

def hp3458_dutinit():
    hp3458_setup()
    
# Low level functions
def hp3458_low_init(ifmode, addr):
    print ("Low-level configuration using %s with ADDR %d" % (ifmode, addr))
    inst.write ("END ALWAYS")
    inst.write ("ID?")
    dat = inst.read()
    tstr = dat.split()
    if (tstr[0] == "HP3458A"):
        sys.stdout.write ("\r\n\033[1;32m%s detected...\033[1;39m" % tstr[0])
        return 1 # OK
    else:
        sys.stdout.write ("\r\n\033[1;31mNo DMM present, exiting!\033[1;39m")
        return 0 # Not ok
        quit()
    return 0

def hp3458_set_aver(mode):
    if (mode == 1):
        intf.write ("NPLC 100")
    elif (mode == 0):
        intf.write ("NPLC 50")
    
def hp3458_set_nplc():
    print ("SET NPLC")
    
def hp3458_acal(type):
    if (type == "ALL" or type == "DCV" or type == "AC" or type == "OHMS"):
        print ("ACAL %s" % type)

def hp3458_vfd_off():
    intf.write ("DISP CLR")
    intf.write ("DISP ON")

def hp3458_vfd_on(str):
    intf.write ("DISP ON")
    intf.write ("DISP MSG,\"%s\"" % str)
    
def hp3458_vfd_cat(str):
    intf.write ("DISP OFF")
    intf.write ("DISP OFF,' (,,)=(^.^)=(,,)'")
    
def hp3458_ocomp(mode, delay):
    if (mode == 1):
        intf.write ("OCOMP 1")
        intf.write ("DELAY 3") #%d" % delay)
        print ("\033[1;31;43m OCOMP ENABLED WITH DELAY 3\033[1;39;49m")
    else:
        intf.write ("OCOMP 0")
        intf.write ("DELAY 0")
        print ("\033[1;33;44m OCOMP DISABLED\033[1;39;49m")

def hp3458_dcv_conf(range, adc_speed):
    #print ("Configure DCV range %d with NPLC %d" % (range, adc_speed))
    
    range = abs(range)
    # Set range
    if (range <= 0.120):
        print ("-i- DCV 0.1;NDIG 9")
        intf.write ("DCV 0.1;NDIG 9")
    elif (range > 0.12 and range < 1.2):
        print ("-i- 1 DCV")
        intf.write ("DCV 1;NDIG 9")
    elif (range > 1.2 and range < 12):
        print ("-i- 10 DCV")
        intf.write ("DCV 10;NDIG 9")
    elif (range > 12 and range < 120):
        print ("\033[1;31m-i- 100 DCV\033[1;39m")
        intf.write ("DCV 100;NDIG 9")
    elif (range > 120 and range < 1100):
        print ("\033[1;31m-i- 1000 DCV\033[1;39m")
        intf.write ("DCV 1000;NDIG 9")
        
    if (adc_speed > 0.0001 and adc_speed < 1000):
        intf.write ("NPLC %f" % adc_speed)

def hp3458_dci_conf(range, adc_speed):
    #print ("Configure DCI range %d with NPLC %d" % (range, adc_speed))
    intf.write ("TRIG SYN")
    intf.write ("TARM SYN")
    
    if (adc_speed > 0.0001 and adc_speed < 1000):
        #print ("NPLC %f" % adc_speed)
        intf.write("NPLC %f" % adc_speed)

    range = abs(range)
    print ("-i- DCI %f" % range)
    intf.write ("DCI %e;NDIG 9" % range)

def hp3458_acv_conf(value, mode):
    range = abs(value)
    # Set range
    intf.write ("SETACV %s" % mode)
    print ("SETACV %s" % mode)
    intf.write ("ACBAND 10,2E6")
    intf.write ("TRIG AUTO")
    intf.write ("TARM AUTO")
    intf.write ("DELAY 1")
    intf.write ("NRDGS 1")
    intf.write ("LFILTER ON")
    intf.write ("APER 1")
    intf.write ("ACV")
    
    if (range <= 0.0120):
        print ("RANGE 0.01;RES 0.00001")
        intf.write ("RANGE 0.01;RES 0.00001")
    elif (range > 0.012 and range < 0.12):
        print ("RANGE 0.1;RES 0.00001")
        intf.write ("RANGE 0.1;RES 0.00001")
    elif (range > 0.12 and range < 1.2):
        print ("RANGE 1;RES 0.00001")
        intf.write ("RANGE 1;RES 0.00001")
    elif (range > 1.2 and range < 12):
        print ("RANGE 10;RES 0.00001")
        intf.write ("RANGE 10;RES 0.00001")
    elif (range > 12 and range < 120):
        print ("RANGE 100;RES 0.00001")
        intf.write ("RANGE 100;RES 0.00001")
    elif (range > 120 and range < 1100):
        print ("RANGE 1000;RES 0.00001")
        intf.write ("RANGE 1000;RES 0.00001")
	meter_dorm(2)

def hp3458_aci_conf(value, mode):
    range = abs(value)
    # Set range
    intf.write ("SETACV %s" % mode)
    intf.write ("ACBAND 10,100E3")
    intf.write ("TRIG AUTO")
    intf.write ("TARM AUTO")
    intf.write ("DELAY 1")
    intf.write ("NRDGS 1")
    intf.write ("LFILTER ON")
    intf.write ("APER 1")
    intf.write ("ACI")
    
    if (range <= 120E-6):
        print ("RANGE 100E-6;RES 0.00001")
        intf.write ("RANGE 100E-6;RES 0.00001")
    elif (range > 1.2E-3 and range < 1.2E-3):
        print ("RANGE 1E-3;RES 0.00001")
        intf.write ("RANGE 1E-3;RES 0.00001")
    elif (range > 12E-3 and range < 12E-3):
        print ("RANGE 10E-3;RES 0.00001")
        intf.write ("RANGE 10E-3;RES 0.00001")
    elif (range > 120E-3 and range < 120E-3):
        print ("RANGE 100E-3;RES 0.00001")
        intf.write ("RANGE 100E-3;RES 0.00001")
    elif (range > 120E-3 and range < 1.100):
        print ("RANGE 1;RES 0.00001")
        intf.write ("RANGE 1;RES 0.00001")
        
def hp3458_ohmf_conf(range, adc_speed):
    print ("Configure OHMF range %d with NPLC %d" % (range, adc_speed))
    intf.write ("DELAY 3")
    print ("OHMF %f" % range)
    intf.write ("OHMF %f" % range)
        
    if (adc_speed > 0.0001 and adc_speed < 1000):
        #print ("NPLC %f" % adc_speed)
        intf.write("NPLC %f" % adc_speed)

def hp3458_ohm_conf(range, adc_speed):
    print ("Configure OHM range %d with NPLC %d" % (range, adc_speed))
    
    print ("OHM %f" % range)
    intf.write ("OHM %f" % range)
        
    if (adc_speed > 0.0001 and adc_speed < 1000):
        #print ("NPLC %f" % adc_speed)
        intf.write("NPLC %f" % adc_speed)

def hp3458_fres_conf():
    pass

def hp3458_res_conf():
    pass

hp3458_fres_conf = hp3458_ohmf_conf
hp3458_res_conf  = hp3458_ohm_conf

def hp3458_get_meas():
    time.sleep(0.1)
    print intf.get_data()
    time.sleep(0.2)
    return intf.get_data()

def hp3458_calibrate():
    print "CAL NOT READY"
    return 0

def hp3458_calibrate_low():
    print "CAL NOT READY"
    return 0

def hp3458_check_terminal():
    frs = intf.read("TERM?")
    frsw = int(frs[1])
    print frsw
    if frsw == 1:
        print ("-w- FRONT TERMINAL are selected")
    elif frsw == 2:
        print ("-w- REAR TERMINAL are selected")
        frsw = 0 #to compatible with 2002
    return frsw

def hp3458_azero(mode):
    # if 1 = enable SYNC, 0 = OFF
    # Turn auto-zero ON (2002 must be in the idle state to send :SYST:AZER:STAT x)
    if (mode == 1):
        intf.write ("AZER ON")
    elif (mode == 0):
        intf.write ("AZER OFF")

def hp3458_rel(mode, oper):
    if (mode == 1):
        hp3458_get_meas()
        meter_dorm(5)
        intf.write ("MATH NULL")
        hp3458_get_meas()
        print "REL ACTIVE"
        intf.write ("TRIG SYN")
    else:
        print "REL NONE"
        intf.write ("MATH OFF")

    if (oper == 1):
        intf.write ("TRIG SYN")
        refval = intf.read("RMATH OFFSET")
        try:
            print ("Reference value = %G" % refval[1])
        except:
            print ("Reference value = %G in debug mode" % float(refval) )
        return refval[1]
    else:
        time.sleep(0.1)
        
src_uncert = [0.0]
    
def hp3458_uncert():
    return src_uncert

def hp3458_end_check():
    duteinf = []
    
    today_date_end = time.strftime("%d %B %Y %H:%M")
    duteinf.append("Test date")
    duteinf.append(today_date_end)
    print ("TEMP?")
    dut_temp = intf.read ("TEMP?")
    duteinf.append("UUT Internal TEMP?")
    duteinf.append("%s" % dut_temp[1])
    
    # Collect all calibration constants
    cvtbl = []
    cix = 1
    print ("Reading CAL constants")
    while cix <= 253:
        #cvtbl.append ("%d" % cix)
        cvtbl.append (intf.read ("CAL? %d,1" % cix) )
        time.sleep(0.001)
        cix = cix + 1
        sys.stdout.write('.')
        sys.stdout.flush()
    with open(result_log_fn, 'a') as dile:
        dile.write ("\r\n")
        dile.write ("DUT Final TEMP? : %s" % dut_temp[1])
        dile.write ("\r\nCAL Post-check DUMP : %s" % cvtbl)
    dile.close()
    
    tval = intf.read ("CAL? 2941")
    duteinf.append("Destructive overloads?")
    duteinf.append("%s" % tval[1])
    
    
    return duteinf
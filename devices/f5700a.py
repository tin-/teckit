# -*- coding: utf-8 -*-
# xDevs.com Confidential
# 
# $Id: devices/f5700a.py | Rev 18  | 2018/03/16 00:20:02 tin_fpga $
# xDevs.com TEC Experiment setup | F5700 module
# 
# Copyright (c) 2012-2017, xDevs.com
# 
# Python 2.7 | RPI3 | Win32
# Project maintainers:
#  o Tsemenko Ilya  (@)
# 
# https://xdevs.com/guide/teckit
#
import sys
from datetime import datetime
import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.read('calkit.conf')
cfg.sections()

if cfg.get('calkit', 'if_debug', 1) == 'true':
    from if_debug import *
elif cfg.get('calkit', 'if_debug', 1) == 'false':
    if cfg.get('calkit', 'interface', 1) == 'gpib':
        from if_gpib import *
    else:
        print "No interface defined!"
        quit()

# Module-wide definitions
#f5700_dcv_test_values = [100E-3, 190E-3, -100E-3, -190E-3, 1.0, 1.9, -1.0, -1.9, 10, 19, -10, -19, 100, 190, -100, -190, 500, 1000, -500, -1000] # Per cal.manual
#f5700_dci_test_values = [100E-6, 190E-6, -100E-6, -190E-6, 1E-3, 1.9E-3, -1E-3, -1.9E-3, 10E-3, 19E-3, -10E-3, -19E-3, 100E-3, 190E-3, -100E-3, -190E-3, 1.0, 1.9, -1.0, -1.9] # Per cal.manual
#f5700_dci_tstr_values = ["100 &micro;", "190 &micro;", "-100 &micro;","-190 &micro;", "1.0 m", "1.9 m", "-1.0 m", "-1.9 m", "10 m", "19 m", "-10 m", "-19 m", "100 m", "190 m", "-100 m", "-190 m", "1.0 ", "1.9 ", "-1.0 ", "-1.9 "] # Per cal.manual
#f5700_acv_test_values = [190E-3, 1.9, 19, 190, 750] # Per cal.manual
#f5700_acv_test_fvalue = [100, 1E3, 5E3, 25E3, 50E3, 100E3, 200E3, 1E6, 2E6]
#f5700_loacv_test_fvalue = [10, 50, 100]
#f5700_res_tstr_values = ["10 ", "19 ", "100 ", "190 ", "1.0 k", "1.9 k", "10 k", "19 k", "100 k", "190 k", "1.0 M", "1.9 M", "10 M", "19 M", "100 M"] # Per cal.manual
#f5700_res_test_values = [10, 19, 100, 190, 1E3, 1.9E3, 10E3, 19E3, 100E3, 190E3, 1E6, 1.9E6, 10E6, 19E6, 100E6] # Per cal.manual
#f5700_1g_test_value = [0.915596626E9] # 1Gohm reference

f5700_mfg_id = "FLUKE"
f5700_model_id = "5700A"
f5700_dateformat = '%m%d%y'
f5700_proc_version = "$Id: devices/f5700a.py | Rev 18  | 2018/03/16 00:20:02 tin_fpga $"

cal_report_check_before = ("calchecks/mcal_check_report_%s_%s_before.txt" % (f5700_mfg_id, f5700_model_id))
cal_report_check_after = ("calchecks/mcal_check_report_%s_%s_after.txt" % (f5700_mfg_id, f5700_model_id))
cal_report_cal_before = ("calchecks/mcal_cal_report_%s_%s_before.txt" % (f5700_mfg_id, f5700_model_id))
cal_report_cal_after = ("calchecks/mcal_cal_report_%s_%s_after.txt" % (f5700_mfg_id, f5700_model_id))
cal_report_const_before = ("calchecks/mcal_const_report_%s_%s_before.txt" % (f5700_mfg_id, f5700_model_id))
cal_report_const_after = ("calchecks/mcal_const_report_%s_%s_after.txt" % (f5700_mfg_id, f5700_model_id))
cal_st_cal_after = ("calchecks/mcal_stcal_report_%s_%s_after.txt" % (f5700_mfg_id, f5700_model_id))
cal_st_shift_after = ("calchecks/mcal_stcheck_report_%s_%s_after.txt" % (f5700_mfg_id, f5700_model_id))

# Fluke 5700A 95% Specifications values

f5700_tcal_24h = 1.0 #1K tolerance
f5700_tcal_long = 5.0 #5K tolerance
f5700_tcal_acv = 2.0 #2K tolerance from last ACCAL

f5700_dcz_test_values = [0.22, 2.2, 11, 22, 220.0, 1100.0] # Per cal.manual
f5700_dcz_tstr_values = ["Short 0 mVDC", "Short 0.0 VDC", "Short 00.00 VDC", "Short 00.0 VDC", "Short 000.0 VDC", "Short 0000.0 VDC"] # Per cal.manual

f5700_dcv_ranges = [0.22, 2.2, 11, 22, 220, 1100]

f5700_dcv_test_values = [100E-3, 190E-3, -100E-3, -190E-3, 1.0, 1.9, -1.0, -1.9, 10, -10, 19, -19, 100, 190, -100, -190, 500, 1000, -500, -1000] # Per cal.manual
                        # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5700_acv_ranges      = [2.2E-3, 22E-3,220E-3,  2.2,   22,  220,  1100]
f5700_acv_ovr_ranges  = [2.21E-3, 22.1E-3, 220.1E-3, 2.21, 22.1, 220.1, 1100.1]
f5700_acv_uvr_ranges  = [600E-6, 6E-6, 60E-6, 600E-6,  6,   60,   600]

f5700_dcv_unc_ppm_24h = [5.5, 3.5, 3, 3, 4, 6]
f5700_dcv_unc_uv_24h =  [0.6, 1, 3.5, 6.5, 80, 500]
f5700_dcv_unc_ppm_90d = [6, 5, 4, 4, 5, 7]
f5700_dcv_unc_uv_90d =  f5700_dcv_unc_uv_24h
f5700_dcv_unc_ppm_180d =[7, 6, 6, 6, 7, 8]
f5700_dcv_unc_uv_180d = f5700_dcv_unc_uv_24h
f5700_dcv_unc_ppm_1y =  [8, 7, 7, 7, 8, 9]
f5700_dcv_unc_uv_1y =   f5700_dcv_unc_uv_24h

f5700_acv_unc_fband = [20, 50, 20E3, 50E3, 100E3, 300E3, 500E3, 1E6]

f5700_acv_unc_ppm_24h = []
                             # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5700_acv_unc_ppm_24h.append([   200,   200,   200,  200,  200,   200,   240]) #0 10-20 Hz
f5700_acv_unc_ppm_24h.append([    80,    80,    80,   75,   75,    75,    55]) #1 20-40   
f5700_acv_unc_ppm_24h.append([    70,    70,    70,   37,   37,    45,   105]) #2 40-20k  
f5700_acv_unc_ppm_24h.append([   170,   170,   170,   65,   65,    70,   230]) #3 20k-50k 
f5700_acv_unc_ppm_24h.append([   400,   400,   400,  100,   90,   120,   600]) #4 50k-100k
f5700_acv_unc_ppm_24h.append([   300,   300,   700,  300,  250,   700,     0]) #5 100k-300k
f5700_acv_unc_ppm_24h.append([  1100,  1100,  1100,  800,  800,  4000,     0]) #6 300k-500k
f5700_acv_unc_ppm_24h.append([  2400,  2400,  2400, 1300, 1200,  6000,     0]) #7 500k-1M 

f5700_acv_unc_uv_24h = []
                             # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5700_acv_unc_uv_24h.append([     4,     4,    12,   40,  400,  4000, 16000]) #0 10-20 Hz
f5700_acv_unc_uv_24h.append([     4,     4,     7,   15,  150,  1500,  3500]) #1 20-40   
f5700_acv_unc_uv_24h.append([     4,     4,     7,    8,   50,   600,  6000]) #2 40-20k  
f5700_acv_unc_uv_24h.append([     4,     4,     7,   10,  100,  1000, 11000]) #3 20k-50k 
f5700_acv_unc_uv_24h.append([     5,     5,    17,   30,  200,  2500, 45000]) #4 50k-100k
f5700_acv_unc_uv_24h.append([    10,    10,    20,   80,  600, 16000,     0]) #5 100k-300k
f5700_acv_unc_uv_24h.append([    20,    20,    25,  200, 2000, 40000,     0]) #6 300k-500k
f5700_acv_unc_uv_24h.append([    20,    20,    45,  300, 3200, 80000,     0]) #7 500k-1M 

f5700_res_tstr_values = ["Zero ", "1 ", "1.9 ", "10 ", "19 ", "100 ", "190 ", "1.0 k", "1.9 k", "10 k", "19 k", "100 k", "190 k", "1.0 M", "1.9 M", "10 M", "19 M", "100 M"] # Per cal.manual
f5700_res_test_values = [      0,    1,    1.9,    10,    19,    100,    190,     1E3,   1.9E3,   10E3,   19E3,   100E3,   190E3,     1E6,   1.9E6,   10E6,   19E6,   100E6] # Per cal.manual

#f5700_res_actual_val  = [10E-6,9.9981580E-01,1.8995474E+00,9.9999130E+00,1.8999094E+01,1.0000171E+02,1.8999497E+02,9.9999150E+02,1.8999978E+03,1.0000082E+04,1.8999704E+04,1.0000138E+05,1.8999307E+05,1.0000020E+06,1.8999595E+06,9.9993990E+06,1.8999094E+07,1.0000823E+08] # Per cal.manual

#f5700_res_actual_val = [0.0000001,0.9998586,1.8995959,10.000054,18.998895,100.00046,189.99067,999.91400,1899.8570,9999.0910,18997.925,99992.040,190000.53,999908.10,1899910.4,9998423.0,18999385,99993640] # Mar 28
#f5700_res_actual_val = [0.0000001,0.9998467,1.8995688,10.000167,18.999098,100.00151,189.99269,0.9999244E3,1.8998779E3, 9.999195E3,18.998130E3, 99.99306E3,190.00241E3,0.9999175E6,1.8999280E6, 9.998536E6,18.999574E6, 99.99457E6] #May 5
#f5700_res_actual_val = [0.0000001,0.9998467,1.8995247,10.000171,18.999110,100.00154,189.99256,999.92490,1899.8775,9999.1980,18998.125,99992.53,190002.10,999916.80,1899926.2,9998548.0,18999613,99994340] # May 6
#f5700_res_actual_val = [0.00000001,0.9998582,1.8995959,10.000124,18.999047,100.00109,189.99202,0.9999216E3,1.8998714E3, 9.999163E3,18.998060E3, 99.99269E3,190.00156E3,0.9999143E6,1.8999227E6, 9.998537E6,18.999498E6,99.99339E6] # Tin A9/A10
#f5700_res_actual_val = [0.0000001,0.9998464,1.8995764,10.000137,18.999065,100.00117,189.99222,0.9999208E3,1.8998698E3, 9.999151E3,18.998053E3, 99.99262E3,190.00138E3,0.9999133E6,1.8999199E6, 9.998516E6,18.999582E6, 99.99418E6]
f5700_res_actual_val = [0.0000001,0.9998158,1.8995474,9.999911,18.999103,100.00175,189.99519,999.9918,1899.9976,10000.079,18999.698,100001.36,189992.91,1000004.4,1899959.3,9999381,18999041,100008460]

#f5700_res_actual_rval = [-2.880543923e-06, 0.9997981, 1.8995145, 9.999907, 18.999081, 100.00163, 189.99486, 999.9910, 1899.9966, 10000.081, 18999.704, 100001.38, 189996.15, 1000000.77, 1899948.369, 9999080.876, 19000225.9, 100.01146E6] # Per cal.manual
f5700_rez_actual_val  = [f5700_res_actual_val[0] ,f5700_res_actual_val[0]] # Per cal.manual
f5700_res_unc_24h     = [ 50E-6 ,   70,     70,    21,    20,     13,     13,      9 ,    9   ,   7.5 ,   7.5 ,    9   ,   9    ,   13   ,   14   ,   27  ,   35  ,   90   ] # Per cal.manual
f5700_res_unc_90d     = [ 50E-6 ,   80,     80,    23,    22,     14,     14,     10 ,   10   ,   9.5 ,   9.5 ,   11   ,  11    ,   15   ,   16   ,   31  ,   39  ,   100  ] # Per cal.manual
f5700_res_unc_180d    = [ 50E-6 ,   85,     85,    27,    24,     15,     15,     11 ,   11   ,  10.5 ,  10.5 ,   12   ,  12    ,   17   ,   18   ,   34  ,   42  ,   105  ] # Per cal.manual
f5700_res_unc_1y      = [ 50E-6 ,   95,     95,    28,    27,     17,     17,     13 ,   13   ,   12  ,   12  ,   14   ,  14    ,   20   ,   21   ,   40  ,   47  ,   110  ] # Per cal.manual
f5700_res_rel_unc_24h = [ 50E-6 ,   32,     25,     5,     4,      2,      2,      2 ,    2   ,   2   ,     2 ,    2   ,   2    ,  2.5   ,   3    ,  10   ,   20  ,   50   ] # Per cal.manual
f5700_res_rel_unc_90d = [ 50E-6 ,   40,     33,     8,     7,      4,      4,    3.5 ,  3.5   ,   3.5 ,   3.5 ,  3.5   , 3.5    ,    5   ,   6    ,  14   ,   24  ,   60   ] # Per cal.manual
f5700_res_unc         = f5700_res_unc_90d
f5700_res_rel_unc     = f5700_res_rel_unc_24h

gpib_addr = int(cfg.get('standard', 'mfc_gpib_addr', 1) )
intf = gpib(gpib_addr,"5700A")

def f5700_echo():
    print "MFC-test"
    
def f5700_id():
    id_str = intf.read("*IDN?\n")
    print id_str
    idmfg = id_str[1].split(",")
    print idmfg[0]
    if ((idmfg[0] == f5700_mfg_id) and (idmfg[1] == f5700_model_id)):
        print ("%s detected, S/N %s, Version %s" % (idmfg[0], idmfg[1], idmfg[2]))
    else:
        print ("No Fluke 5700A instrument detected. Check GPIB address. Testing abort.")
        #quit()
            
    #if (int(idmfg[2]) < 6565601):
    #    print ("This is Series I unit")
    #else:
    #    series1 = 0
    #    print ("This is Series II unit")
    
def f5700_setup():
    print "Initialize Fluke 5700A"
    intf.clear()
    intf.write ("*CLS")
    intf.write ("*ESR?")
    intf.write ("CAL_INTV 1")
    intf.write ("CONF95")

    f5700_out_disable()
    time.sleep(1)           # take short nap
    flt = intf.read("FAULT?")
    #if (int(flt[1]) == 0):
    #    print "No GPIB data faults, we good to go"
    
def f5700_check_info():
    dutinf = []
    series1 = 1
    
    #intf.write ("SP_SET 19200,TERM,XON,DBIT8,SBIT1,PNONE,CRLF") 
    ##intf.read()
    #print("Reading last calibration data\r\n")
    #intf.write ("CAL_PR CAL")                           # Printout last calibration data 
    #time.sleep(1)                                       # Take a nap for 20 seconds
    #print("Reading last calibration check data\r\n")
    #intf.write ("CAL_PR CHECK")                         # Printout last calibration check data
    #time.sleep(1)                                       # Take a nap for 20 seconds
    #print("Reading raw goodies!\r\n")
    #intf.write ("CAL_PR RAW")                           # Printout RAW goodies
    #time.sleep(1)                                       # Take a nap for 20 seconds
    
           
    mfc_isr = f5700_read_isr()
    print mfc_isr
    if (mfc_isr & 0x0001):
        print "Calibrator output OPERATING"
    if (mfc_isr & 0x0002):
        print "Calibrator EXT GUARD enabled"
    if (mfc_isr & 0x0004):
        print "Calibrator EXT SENSE enabled"
    if (mfc_isr & 0x0008):
        print "Calibrator BOOST (auxilary amp) enabled"
    if (mfc_isr & 0x0010):
        print "Calibrator 2-wire RCOMP enabled"
    if (mfc_isr & 0x0020):
        print "Calibrator output range is LOCKED"
    if (mfc_isr & 0x0040):
        print "Calibrator variable phase is active"
    if (mfc_isr & 0x0080):
        print "Calibrator output PLL LOCKED to EXT SOURCE"
    if (mfc_isr & 0x0100):
        print "Calibrator OFFSET active"
    if (mfc_isr & 0x0200):
        print "Calibrator SCALE active"
    if (mfc_isr & 0x0400):
        print "Calibrator WIDEBAND active"
    if (mfc_isr & 0x0800):
        print "Calibrator UNDER REMOTE CONTROL"
    if (mfc_isr & 0x1000):
        print "Calibrator STABLE (settled within spec)"
    if (mfc_isr & 0x2000):
        print "Calibrator is cooking report over SERIAL"
    
    pud_str = intf.read("*PUD?")
    print ("User string PUD : %s" % pud_str[1])
    
    #for cnt in range (0, 10):
    # Need check if this command works correctly. So far it just try to read 10 times fatality errors history
    #ferr_str = intf.read("FATALITY?")
    #print ("Fatal errors history: %s" % ferr_str[1])
    
    #print ("Line frequency")
    #lfr = intf.read(":SYST:LFR?")
    #dutinf.append("Line frequency")
    #dutinf.append(lfr[1])
    #print ("Read next calibration information")
    #nextcal = intf.read(":CAL:PROT:NDUE?")
    #dutinf.append("Next calibration date")
    #dutinf.append(nextcal[1])
    #print ("Read last calibration information")
    #currcal = intf.read(":CAL:PROT:DATE?")
    #dutinf.append("Last calibration date")
    #dutinf.append(currcal[1])
    
    #caldata = intf.read(":CAL:PROT:DATA?")
    #caldata = ("test,test2")
    #caldut = caldata.split(',')
    #for lex in range (0, len(caldut)):
    #    print ("%d = %s\r" % (lex, caldut[lex]))
    
    
    
    print("Reading cal days\r\n")
    temp_str = intf.read("CAL_DAYS? CAL\n")
    dutinf.append("MFC last calibrated")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("Reading since cal zero days\r\n")
    temp_str = intf.read("CAL_DAYS? ZERO\n")
    dutinf.append("MFC since DCV ZERO")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("Reading since cal WBFLAT days\r\n")
    temp_str = intf.read("CAL_DAYS? WBFLAT\n")
    dutinf.append("MFC since WBFLAT")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("Reading since cal WBGAIN days\r\n")
    temp_str = intf.read("CAL_DAYS? WBGAIN\n")
    dutinf.append("MFC since WBGAIN")
    dutinf.append("%s days ago" % temp_str[1])
    
    dutinf.append("MFC Confidence level")
    dutinf.append("24h 95%")
    
    print("Reading last calibration\r\n")
    temp_str = intf.read("CAL_DATE? CAL\n")
    try:
        caldstr = "%d" % temp_str[1]
        caldat = datetime.strptime(caldstr, f5700_dateformat)
    except:
        caldat = "Debug"
    dutinf.append("MFC Calibrate date")
    dutinf.append("%s" % caldat)
        
    
    print("Reading last calibration Zero\r\n")
    temp_str = intf.read("CAL_DATE? ZERO\n")
    try:
        caldstr = "%d" % temp_str[1]
        calzdat = datetime.strptime(caldstr, f5700_dateformat)
    except:
        calzdat = "Debug"
    dutinf.append("MFC Calibrate date Zero")
    dutinf.append("%s" % calzdat)
    
    print("Reading last calibration WBF\r\n")
    temp_str = intf.read("CAL_DATE? WBFLAT\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwfdat = datetime.strptime(caldstr, f5700_dateformat)
    except:
        calwfdat = "Debug"
    dutinf.append("Calibrate date WB Flatness")
    dutinf.append("%s" % calwfdat)
    
    print("Reading last calibration WBG\r\n")
    temp_str = intf.read("CAL_DATE? WBGAIN\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwgdat = datetime.strptime(caldstr, f5700_dateformat)
    except:
        calwgdat = "Debug"
    dutinf.append("Calibrate date WB Gain")
    dutinf.append("%s" % calwgdat)
    
    if(series1 == 0):
        temp_str = intf.read("CAL_CONF?")
        print ("Unit calibration confidence level : %s" % temp_str[1])
        
    #lifetim = intf.read("ETIME?\n")
    #lifetime = int(lifetim[1])
    #print ("Unit running time : %d hr" % (lifetime/60))
    #dutinf.append("Unit running time")
    #dutinf.append("%d hr" % (lifetime/60))
    
    rd_const = intf.read("CAL_CONST? CHECK, KV6")
    print ("CAL CONST 6.5V reference voltage : %s" % rd_const[1])
    dutinf.append("CAL CONST 6.5V reference voltage")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, KV13")
    print ("CAL CONST 13V reference voltage : %s" % rd_const[1])
    dutinf.append("CAL CONST 13V reference voltage")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, D4P")
    print ("CAL CONST 22V range positive zero : %s" % rd_const[1])
    dutinf.append("CAL CONST 22V range positive zero")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, D4M")
    print ("CAL CONST 22V range negative zero : %s" % rd_const[1])
    dutinf.append("CAL CONST 22V range negative zero")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, DACLIN")
    print ("CAL CONST DAC Linearity : %s" % rd_const[1])
    dutinf.append("CAL CONST DAC Linearity")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, R10K")
    print ("CAL CONST 10KOHM output resistance : %s" % rd_const[1])
    dutinf.append("CAL CONST 10KOHM true output resistance")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, RS10K") 
    print ("CAL CONST 10KOHM standard resistance : %s" % rd_const[1])
    dutinf.append("CAL CONST 10KOHM standard resistance")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, ZERO_TEMP")
    print ("CAL CONST, Zero calibration temperature : %s" % rd_const[1])
    dutinf.append("CAL CONST, Zero calibration temperature")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, ALL_TEMP")
    print ("CAL CONST, All calibration temp : %s" % rd_const[1])
    dutinf.append("CAL CONST, All calibration temp")
    dutinf.append("%s" % rd_const[1])
    
    intf.clear()
    intf.write ("*CLS")
    intf.write ("*ESR?")

    return dutinf
    
def f5700_perfinit():
    print "Setup F5700A for performance verification"
    print "Connect DMM to the calibrator, HI to DMM HI, LO to DMM LO. Use low-thermal shielded 1m cable"
    print "Allow 8 hour warm-up"
    print "Select DCV Function, 10NPLC, FILTER 10 AVER, Manual Range"
    print "Set MFC output to 0mV"
    print "Enable REL. Leave REL till DCV test finish"

def f5700_dutinit():
    f5700_id()
    f5700_setup()
    
def f5700_dcvperf(value):
    if (value < 1.0):
        print ("Set MFC to %.8f mVDC" % (value * 1E3))
    else:
        print ("Set MFC to %.8f VDC" % value)
    print "Allow 60sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 8E-6)
    return reading

def f5700_dciperf(value):
    if (value < 1.0):
        print ("Set MFC to %.8f mADC" % (value * 1E3))
    else:
        print ("Set MFC to %.8f ADC" % value)
    print "Allow 20sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 2.5E-6)
    return reading

def f5700_resperf(value):
    print ("Set resistance to %.8E Ohm" % value)
    print "Allow 30sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 5E-6)
    return reading
    
def f5700_acvperf(value, freq):
    if (value < 1.0):
        print ("Set MFC to %.8f mVAC at %d Hz" % (value * 1E3, freq))
    else:
        print ("Set MFC to %.8f VAC at %d Hz" % (value, freq))
    #print "Allow 20sec to settle"
    #print "Take K2002 reading"
    reading = value
    return reading
    
def f5700_dcvtest():
    dcvresult = []
    print ("Number of DCV tests = %d" % len(f5700_dcv_test_values))
    for testcnt in range (0, len(f5700_dcv_test_values)):
        dcvresult.append(f5700_dcvperf(f5700_dcv_test_values[testcnt]))
    print ("Reset MFC to 0.00000 VDC")
    print ("DCV test complete")
    return dcvresult

def f5700_dcitest():
    dciresult = []
    print ("Connect MFC HI output to CURR IN DMM and MFC LO output to DMM LO")
    print ("Select DCI, FILTER 10 AVER, 10 NPLC, manual range")
    print ("Number of DCI tests = %d" % len(f5700_dci_test_values))
    for testcnt in range (0, len(f5700_dci_test_values)):
        dciresult.append(f5700_dciperf(f5700_dci_test_values[testcnt]))
    print ("Reset MFC to 0.00000 ADC")
    print ("DCI test complete")
    return dciresult

def f5700_uncert():
    uncr = intf.read("UNCERT?")
    uncerval = uncr[1].split(",")
    if (uncerval[1] == "PPM"):
	uncv = float(uncerval[0])
    elif (uncerval[1] == "PCT"):
	uncv = float(uncerval[0]) * 1E3
    elif (uncerval[1] == "OHM"):
	uncv = float(uncerval[0])
    elif (uncerval[1] == "A"):
	uncv = float(uncerval[0])
    elif (uncerval[1] == "V"):
	uncv = float(uncerval[0])

    print ("MFC Uncertainty = %f ppm" % uncv)
    return uncv

def f5700_measout():
    return intf.read("OUT?")
    
def f5700_dormant(sec):
    print ("\nWorking for %d" % sec)
    while (sec != 0):
        print("To go %d sec" % sec)
        time.sleep(5)
        sec = sec - 5
        if (sec < 0):
            return sec    
    print "\n"
    
def f5700_cal_report(fname, cmd):
    print ("Generating %s report" % cmd)
    intf.clear()
    intf.write("*CLS*")
    intf.write(cmd)
    time.sleep(1)
    
    report = intf.inst.read(len=64000) # read 32k chars
    #report = "NOTHING for debug"
    
    with open(fname,'ab') as od:
        print report
        od.write("%s" % report)
    print "Report %s done\n" % fname
    
def f5700_calchk():
    print ("Running CAL ZERO and CAL CHECK")
    intf.clear()
    intf.write("*CLS*")
    intf.write("CAL_ZERO")
    f5700_dormant(180)
    intf.write ("CAL_CHK")
    f5700_dormant(3700)
    print "Cal check is done\n"
    
def f5700_selfcal():
    f5700_setup()
    print ("Start xDevs.com self-calibration procedures")
    f5700_cal_report (cal_report_check_before,"CAL_RPT? CHECK")
    f5700_cal_report (cal_report_cal_before,  "CAL_RPT? CAL")
    f5700_cal_report (cal_report_const_before,"CAL_RPT? RAW")
    f5700_calchk()
    f5700_cal_report (cal_report_check_after, "CAL_RPT? CHECK")
    f5700_cal_report (cal_report_cal_after,   "CAL_RPT? CAL")
    f5700_cal_report (cal_report_const_after, "CAL_RPT? RAW")
    f5700_cal_report (cal_st_cal_after,       "CAL_SLST? CAL")
    f5700_cal_report (cal_st_shift_after,     "CAL_SLST? CHECK")
    print ("Done!")
    
def f5700_report_aftercal():
    f5700_setup()
    mfcinfo = f5700_check_info()
    print mfcinfo
    f5700_cal_report (cal_report_check_after, "CAL_RPT? CHECK")
    f5700_cal_report (cal_report_cal_after,   "CAL_RPT? CAL")
    f5700_cal_report (cal_report_const_after, "CAL_RPT? RAW")
    f5700_cal_report (cal_st_cal_after,       "CAL_SLST? CAL")
    f5700_cal_report (cal_st_shift_after,     "CAL_SLST? CHECK")
    print ("Done!")
        
def f5700_acvtest():
    acvresult = []
    print ("Disable REL and FILTER")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Number of ACV tests = %d" % 36)
    for testfcnt in range (0, len(f5700_acv_test_fvalue)):
        # Iterate frequencies
        print ("\r")
        for testcnt in range (0, len(f5700_acv_test_values)):
            # Iterate voltages
            if ((testfcnt < 4) or (testfcnt < 6 and testcnt < 4) or (testfcnt < 8 and testcnt < 3) or (testfcnt < 9 and testcnt < 2)):
                acvresult.append(f5700_acvperf(f5700_acv_test_values[testcnt],f5700_acv_test_fvalue[testfcnt]))
                acvresult.append(f5700_acv_test_fvalue[testfcnt])
    #print ("Reset MFC to 0.00000 VAC")
    print ("ACV test complete")
    return acvresult

def f5700_loacvtest():
    acvresult = []
    print ("Disable REL and FILTER")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Configure ACV Func with AC-TYPE:LOW-FREQ-RMS")
    print ("Number of ACV tests = %d" % 14)
    for testfcnt in range (0, len(f5700_loacv_test_fvalue)):
        # Iterate frequencies
        print ("\r")
        for testcnt in range (0, len(f5700_acv_test_values)):
            # Iterate voltages
            if ( not (testfcnt == 0 and testcnt == 4)):
                acvresult.append(f5700_acvperf(f5700_acv_test_values[testcnt],f5700_loacv_test_fvalue[testfcnt]))
                acvresult.append(f5700_loacv_test_fvalue[testfcnt])
    #print ("Reset MFC to 0.00000 VAC")
    print ("Low Freq ACV test complete")
    return acvresult

def f5700_ocomp(mode):
    print ("RES OCOMP mode = %d" % mode)
    
def f5700_restest():
    resresult = []
    print ("Connect MFC H/L/S+/S- output to DMM H/L/S+/S-")
    print ("Select 4W Res, FILTER 10 AVER, 10 NPLC, OCOMP ON, manual range")
    print ("Select external sense ON at MFC")
    print ("OCOMP cannot be used on ranges >20kOhm")
    print ("Number of RES tests = %d" % len(f5700_res_test_values))
    for testcnt in range (0, len(f5700_res_test_values)):
        if (testcnt > 3):
            f5700_ocomp(0)
            resresult.append(f5700_resperf(f5700_res_test_values[testcnt]))
        else:
            f5700_ocomp(1)
            resresult.append(f5700_resperf(f5700_res_test_values[testcnt]))
    print ("Reset MFC to 0.0000 RES")
    print ("RES test complete")
    return resresult

def f5700_1grtest():
    resresult = []
    print ("Connect 1G Resistor H/L output to DMM H/L")
    print ("Select 2W Res, FILTER 10 AVER, 10 NPLC, manual range")
    f5700_ocomp(0)
    resresult.append(f5700_resperf(f5700_1g_test_value[0]))
    print ("1G RES test complete")
    return resresult
    
def f5700_perftest():
    dutresult = []
    dutresult.append(f5700_dcvtest())
    dutresult.append(f5700_acvtest())
    dutresult.append(f5700_loacvtest())
    #dutresult.append(f5700_pkacvtest())
    dutresult.append(f5700_dcitest())
    #dutresult.append(f5700_acitest())
    dutresult.append(f5700_restest())
    dutresult.append(f5700_1grtest())
    #dutresult.append(f5700_freqtest())
    
    return dutresult

def f5700_out_set(cmd):
    intf.write ("OUT %s" % cmd)
    #print cmd

def f5700_out_enable():
    intf.write ("OPER") 
    #print ("ENABLE")
    time.sleep(0.1)

def f5700_out_disable():
    #print ("STBY")
    intf.write ("STBY")

def f5700_ext_sense(mode):
    if mode == 1:
	#print ("\033[1;40m-i- External sense on MFC is \033[1;42mON\033[1;49m")
	intf.write ("EXTSENSE ON")
    elif mode == 0:
	#print ("\033[1;40m-i- External sense on MFC is \033[1;41mOFF\033[1;49m")
	intf.write ("EXTSENSE OFF")

def f5700_curr_post(mode):
    if mode == 1:
	intf.write ("CUR_POST NORMAL")
	time.sleep(1)
    elif mode == 2:
	intf.write ("CUR_POST AUX")
	time.sleep(1)
    elif mode == 3:
	intf.write ("CUR_POST IB5725")
	time.sleep(1)

def f5700_read_isr():
    #mfc_isr = intf.read("ISR?")
    mfc_isr = [0, 1]
    return int(mfc_isr[1])

def f5700_select_range():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5700_select_res():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5700_sel_res():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5700_out_dcv():
    print "Incorrect operation on Fluke MFC"
    time.sleep(0.1)
    
def f5700_out_dci():
    print "Incorrect operation on Fluke MFC"
    time.sleep(0.1)

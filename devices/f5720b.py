# $Id: f5720b.py | Rev 1110  | 2019/01/03 11:24:54 tin_fpga $
# Fluke 5720A test and calibration module
# 
# (C) 2012-2017, cal.equipment
# 
# Python 2.7
# Project maintainers:
# * clu
# * mm
import sys
from mfc import *
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
    elif cfg.get('calkit', 'interface', 1) == 'vxi':
        from if_vxi import *
    else:
        print "No interface defined!"
        quit()

start_time = time.time()
test_time = 18600
end_time = start_time + test_time # 3.5hrs test time
elapsed = time.time() - start_time
remaining = end_time - (start_time + elapsed)

f5720_mfg_id = "FLUKE"
f5720_model_id = "5720A"
f5720_dateformat = '%m%d%y'
f5720_proc_version = "$Id: f5720b.py | Rev 1110  | 2019/01/03 11:24:54 tin_fpga $"

# Fluke 5720A 95% Specifications values

f5720_volthertz_limit = (2.2 * 1e7)
f5720_volthertz_booster_limit = (7.5 * 1e7)

f5720_tcal_24h = 1.0 #1K tolerance
f5720_tcal_long = 5.0 #5K tolerance
f5720_tcal_acv = 2.0 #2K tolerance from last ACCAL

f5720_dcz_test_values = [0.22, 2.2, 11, 22, 220.0, 1100.0] # Per cal.manual
f5720_dcz_tstr_values = ["Short 0 mVDC", "Short 0.0 VDC", "Short 00.00 VDC", "Short 00.0 VDC", "Short 000.0 VDC", "Short 0000.0 VDC"] # Per cal.manual

f5720_dcv_ranges = [0.22, 2.2, 11, 22, 220, 1100]

f5720_dcv_test_values = [100E-3, 190E-3, -100E-3, -190E-3, 1.0, 1.9, -1.0, -1.9, 10, -10, 19, -19, 100, 190, -100, -190, 500, 1000, -500, -1000] # Per cal.manual
                        # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5720_acv_ranges      = [2.2E-3, 22E-3,220E-3,  2.2,   22,  220,  1100]
f5720_acv_ovr_ranges  = [2.21E-3, 22.1E-3, 220.1E-3, 2.21, 22.1, 220.1, 1100.1]
f5720_acv_uvr_ranges  = [600E-6, 6E-6, 60E-6, 600E-6,  6,   60,   600]

f5720_dcv_unc_ppm_24h = [5.5, 3.5, 3, 3, 4, 6]
f5720_dcv_unc_uv_24h =  [0.6, 1, 3.5, 6.5, 80, 500]
f5720_dcv_unc_ppm_90d = [6, 5, 4, 4, 5, 7]
f5720_dcv_unc_uv_90d =  f5720_dcv_unc_uv_24h
f5720_dcv_unc_ppm_180d =[7, 6, 6, 6, 7, 8]
f5720_dcv_unc_uv_180d = f5720_dcv_unc_uv_24h
f5720_dcv_unc_ppm_1y =  [8, 7, 7, 7, 8, 9]
f5720_dcv_unc_uv_1y =   f5720_dcv_unc_uv_24h

f5720_acv_unc_fband = [20, 50, 20E3, 50E3, 100E3, 300E3, 500E3, 1E6]

f5720_acv_unc_ppm_24h = []
                             # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5720_acv_unc_ppm_24h.append([   200,   200,   200,  200,  200,   200,   240]) #0 10-20 Hz
f5720_acv_unc_ppm_24h.append([    80,    80,    80,   75,   75,    75,    55]) #1 20-40   
f5720_acv_unc_ppm_24h.append([    70,    70,    70,   37,   37,    45,   105]) #2 40-20k  
f5720_acv_unc_ppm_24h.append([   170,   170,   170,   65,   65,    70,   230]) #3 20k-50k 
f5720_acv_unc_ppm_24h.append([   400,   400,   400,  100,   90,   120,   600]) #4 50k-100k
f5720_acv_unc_ppm_24h.append([   300,   300,   700,  300,  250,   700,     0]) #5 100k-300k
f5720_acv_unc_ppm_24h.append([  1100,  1100,  1100,  800,  800,  4000,     0]) #6 300k-500k
f5720_acv_unc_ppm_24h.append([  2400,  2400,  2400, 1300, 1200,  6000,     0]) #7 500k-1M 

f5720_acv_unc_uv_24h = []
                             # 2.2mV,  22mV, 220mV, 2.2V,  22V,  220V, 1100V
f5720_acv_unc_uv_24h.append([     4,     4,    12,   40,  400,  4000, 16000]) #0 10-20 Hz
f5720_acv_unc_uv_24h.append([     4,     4,     7,   15,  150,  1500,  3500]) #1 20-40   
f5720_acv_unc_uv_24h.append([     4,     4,     7,    8,   50,   600,  6000]) #2 40-20k  
f5720_acv_unc_uv_24h.append([     4,     4,     7,   10,  100,  1000, 11000]) #3 20k-50k 
f5720_acv_unc_uv_24h.append([     5,     5,    17,   30,  200,  2500, 45000]) #4 50k-100k
f5720_acv_unc_uv_24h.append([    10,    10,    20,   80,  600, 16000,     0]) #5 100k-300k
f5720_acv_unc_uv_24h.append([    20,    20,    25,  200, 2000, 40000,     0]) #6 300k-500k
f5720_acv_unc_uv_24h.append([    20,    20,    45,  300, 3200, 80000,     0]) #7 500k-1M 

f5720_res_tstr_values = ["Zero ", "1 ", "1.9 ", "10 ", "19 ", "100 ", "190 ", "1.0 k", "1.9 k", "10 k", "19 k", "100 k", "190 k", "1.0 M", "1.9 M", "10 M", "19 M", "100 M"] # Per cal.manual
f5720_res_test_values = [      0,    1,    1.9,    10,    19,    100,    190,     1E3,   1.9E3,   10E3,   19E3,   100E3,   190E3,     1E6,   1.9E6,   10E6,   19E6,   100E6] # Per cal.manual

#f5720_res_actual_val  = [10E-6,9.9981580E-01,1.8995474E+00,9.9999130E+00,1.8999094E+01,1.0000171E+02,1.8999497E+02,9.9999150E+02,1.8999978E+03,1.0000082E+04,1.8999704E+04,1.0000138E+05,1.8999307E+05,1.0000020E+06,1.8999595E+06,9.9993990E+06,1.8999094E+07,1.0000823E+08] # Per cal.manual

f5720_res_actual_val   = [0.00000001,0.9998127,1.8998846,10.000321,19.000007,100.00322,189.99820,1.0000100e3,1.9000237e3, 9.999791e3,18.999393e3, 99.99470e3,189.98860e3,0.9999792e6,1.8999620e6, 9.998943e6,18.998193e6,100.00636e6] #Hulk main set of ohm boards
f5720_rez_actual_val  = [f5720_res_actual_val[0] ,f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0], f5720_res_actual_val[0]] # Per cal.manual
f5720_res_unc_24h     = [ 50E-6 ,   70,     70,    21,    20,     13,     13,      9 ,    9   ,   7.5 ,   7.5 ,    9   ,   9    ,   13   ,   14   ,   27  ,   35  ,   90   ] # Per cal.manual
f5720_res_unc_90d     = [ 50E-6 ,   80,     80,    23,    22,     14,     14,     10 ,   10   ,   9.5 ,   9.5 ,   11   ,  11    ,   15   ,   16   ,   31  ,   39  ,   100  ] # Per cal.manual
f5720_res_unc_180d    = [ 50E-6 ,   85,     85,    27,    24,     15,     15,     11 ,   11   ,  10.5 ,  10.5 ,   12   ,  12    ,   17   ,   18   ,   34  ,   42  ,   105  ] # Per cal.manual
f5720_res_unc_1y      = [ 50E-6 ,   95,     95,    28,    27,     17,     17,     13 ,   13   ,   12  ,   12  ,   14   ,  14    ,   20   ,   21   ,   40  ,   47  ,   110  ] # Per cal.manual
f5720_res_rel_unc_24h = [ 50E-6 ,   32,     25,     5,     4,      2,      2,      2 ,    2   ,   2   ,     2 ,    2   ,   2    ,  2.5   ,   3    ,  10   ,   20  ,   50   ] # Per cal.manual
f5720_res_rel_unc_90d = [ 50E-6 ,   40,     33,     8,     7,      4,      4,    3.5 ,  3.5   ,   3.5 ,   3.5 ,  3.5   , 3.5    ,    5   ,   6    ,  14   ,   24  ,   60   ] # Per cal.manual
f5720_res_unc         = f5720_res_unc_24h
f5720_res_rel_unc     = f5720_res_rel_unc_24h

gpib_addr = int(cfg.get('standard', 'mfc_gpib_addr', 1) )
intf = gpib(gpib_addr,"5720A")

def f5720_echo():
    time.sleep(0.1)
    
def f5720_id():
    id_str = intf.read("*IDN?\n")
    #print "\033[6;5H"
    #print id_str
    idmfg = id_str[1].split(",")
    if ((idmfg[0] == f5720_mfg_id) and (idmfg[1] == f5720_model_id)):
        print ("\033[6;5H\033[1;33m%s %s detected, S/N %s on GPIB %d\033[0;39m" % (idmfg[0], idmfg[1], idmfg[2], gpib_addr)),
    else:
        print ("\033[6;5HNo Fluke 5720A instrument detected. Check GPIB address %d. Testing abort." % gpib_addr),
        #quit()
    
def f5720_setup():
    intf.clear()
    intf.write ("*CLS")
    intf.write ("*ESR?")
    intf.write ("CAL_INTV 1")
    intf.write ("CAL_CONF CONF95")
    intf.write ("EXTGUARD OFF")

    f5720_out_disable()
    time.sleep(1)           # take short nap
    flt = intf.read("FAULT?")
    #if (int(flt[1]) == 0):
    #    print "No GPIB data faults, we good to go"
    
def f5720_check_info():
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
           
#    mfc_isr = f5720_read_isr()
#    print "\033[7;5H",
#    print mfc_isr
#    if (mfc_isr & 0x0001):
#        print "\033[7;30H OPERATING",
#    if (mfc_isr & 0x0002):
#        print "\033[7;40H EXT GUARD",
#    if (mfc_isr & 0x0004):
#        print "\033[7;50H EXT SENSE",
#    if (mfc_isr & 0x0008):
#        print "\033[7;60H BOOST ON",
#    if (mfc_isr & 0x0010):
#        print "\033[7;70H 2-wire RCOMP",
#    if (mfc_isr & 0x0020):
#        print "\033[7;80H RNG LOCKED",
#    if (mfc_isr & 0x0040):
#        print "\033[7;90H VAR PH",
#    if (mfc_isr & 0x0080):
#        print "\033[7;100H PLL LOCK",
#    if (mfc_isr & 0x0100):
#        print "\033[7;110H OFFSET",
#    if (mfc_isr & 0x0200):
#        print "\033[7;120H SCALE",
#    if (mfc_isr & 0x0400):
#        print "\033[7;130H WB EN",
#    if (mfc_isr & 0x0800):
#        print "\033[7;140H REMOTE",
#    if (mfc_isr & 0x1000):
#        print "\033[7;150H STABLE",
#    if (mfc_isr & 0x2000):
#        print "\033[8;2H Calibrator is cooking report over SERIAL"
    
    pud_str = intf.read("*PUD?")
    print ("\033[8;5H User string PUD : %s" % pud_str[1]),
    
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
    
    
    
    print("\033[13;6H Reading cal days"),
    temp_str = intf.read("CAL_DAYS? CAL\n")
    dutinf.append("MFC last calibrated")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("\033[14;6H Reading since cal zero days"),
    temp_str = intf.read("CAL_DAYS? ZERO\n")
    dutinf.append("MFC since DCV ZERO")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("\033[15;6H Reading since cal WBFLAT days"),
    temp_str = intf.read("CAL_DAYS? WBFLAT\n")
    dutinf.append("MFC since WBFLAT")
    dutinf.append("%s days ago" % temp_str[1])
    
    print("\033[16;6H Reading since cal WBGAIN days"),
    temp_str = intf.read("CAL_DAYS? WBGAIN\n")
    dutinf.append("MFC since WBGAIN")
    dutinf.append("%s days ago" % temp_str[1])
    
    dutinf.append("MFC Confidence level")
    dutinf.append("<b>24h 95% REL</b>")
    
    print("\033[17;6H Reading last calibration"),
    temp_str = intf.read("CAL_DATE? CAL\n")
    try:
        caldstr = "%d" % temp_str[1]
        caldat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        caldat = "Debug"
    dutinf.append("MFC Calibrate date")
    dutinf.append("%s" % caldat)
        
    
    print("\033[18;6H Reading last calibration Zero"),
    temp_str = intf.read("CAL_DATE? ZERO\n")
    try:
        caldstr = "%d" % temp_str[1]
        calzdat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        calzdat = "Debug"
    dutinf.append("MFC Calibrate date Zero")
    dutinf.append("%s" % calzdat)
    
    print("\033[19;6H Reading last calibration WBF"),
    temp_str = intf.read("CAL_DATE? WBFLAT\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwfdat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        calwfdat = "Debug"
    dutinf.append("Calibrate date WB Flatness")
    dutinf.append("%s" % calwfdat)
    
    print("\033[20;6H Reading last calibration WBG"),
    temp_str = intf.read("CAL_DATE? WBGAIN\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwgdat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        calwgdat = "Debug"
    dutinf.append("Calibrate date WB Gain")
    dutinf.append("%s" % calwgdat)
    
    if(series1 == 0):
        temp_str = intf.read("CAL_CONF?")
        print ("\033[13;60H Unit calibration confidence level : %s" % temp_str[1]),
        
    #lifetim = intf.read("ETIME?\n")
    #lifetime = int(lifetim[1])
    #print ("Unit running time : %d hr" % (lifetime/60))
    #dutinf.append("Unit running time")
    #dutinf.append("%d hr" % (lifetime/60))
    
    rd_const = intf.read("CAL_CONST? CHECK, KV6")
    print ("\033[13;5H CAL CONST 6.5V reference voltage : %s" % rd_const[1]),
    dutinf.append("CAL CONST 6.5V reference voltage")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, KV13")
    print ("\033[14;5H CAL CONST 13V reference voltage : %s" % rd_const[1]),
    dutinf.append("CAL CONST 13V reference voltage")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, D4P")
    print ("\033[15;5H CAL CONST 22V range positive zero : %s" % rd_const[1]),
    dutinf.append("CAL CONST 22V range positive zero")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, D4M")
    print ("\033[16;5H CAL CONST 22V range negative zero : %s" % rd_const[1]),
    dutinf.append("CAL CONST 22V range negative zero")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, DACLIN")
    print ("\033[17;5H CAL CONST DAC Linearity : %s" % rd_const[1]),
    dutinf.append("CAL CONST DAC Linearity")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, R10K")
    print ("\033[18;5H CAL CONST 10KOHM output resistance : %s" % rd_const[1]),
    dutinf.append("CAL CONST 10KOHM true output resistance")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, RS10K") 
    print ("\033[19;5H CAL CONST 10KOHM standard resistance : %s" % rd_const[1])
    dutinf.append("CAL CONST 10KOHM standard resistance")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, ZERO_TEMP")
    print ("\033[20;5H CAL CONST, Zero calibration temperature : %s" % rd_const[1])
    dutinf.append("CAL CONST, Zero calibration temperature")
    dutinf.append("%s" % rd_const[1])
    
    rd_const = intf.read("CAL_CONST? CHECK, ALL_TEMP")
    print ("\033[13;5H CAL CONST, All calibration temp : %s" % rd_const[1]),
    dutinf.append("CAL CONST, All calibration temp")
    dutinf.append("%s" % rd_const[1])

    # Booster items
    rd_const = intf.read("BTYPE?")
    print ("\033[20;5H Booster type : %s" % rd_const[1])
    dutinf.append("Booster type")
    dutinf.append("%s" % rd_const[1])

    rd_const = intf.read("CUR_POST?")
    print ("\033[13;5H CUR_POST? : %s" % rd_const[1]),
    dutinf.append("Current output posts")
    dutinf.append("%s" % rd_const[1])
    
    print("\033[19;6H Reading last calibration AMP"),
    temp_str = intf.read("CAL_DATE? B5725\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwfdat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        calwfdat = "Debug"
    dutinf.append("Calibrate date 5725A AMP")
    dutinf.append("%s" % calwfdat)

    print("\033[19;6H Reading days AMP"),
    temp_str = intf.read("CAL_DAYS? B5725\n")
    try:
        caldstr = "%d" % temp_str[1]
        calwfdat = datetime.strptime(caldstr, f5720_dateformat)
    except:
        calwfdat = "Debug"
    dutinf.append("Calibrated days ago")
    dutinf.append("%s" % calwfdat)

    rd_const = intf.read("CAL_CONST? CAL, CAL5725_TEMP")
    print ("\033[20;5H CAL CONST, Amp calibration temperature : %s" % rd_const[1])
    dutinf.append("CAL CONST, Amp ACAL temperature")
    dutinf.append("%s" % rd_const[1])

    rd_const = intf.read("CAL_CONST? CHECK, CAL5725_TEMP")
    print ("\033[20;5H CAL CONST, Zero calibration temperature : %s" % rd_const[1])
    dutinf.append("CAL CONST, Amp CalCheck temperature")
    dutinf.append("%s" % rd_const[1])

    intf.clear()
    intf.write ("*CLS")
    intf.write ("*ESR?")
    f5720_ext_guard(1)
    return dutinf
    
def f5720_perfinit():
    print "Setup f5720a for performance verification"
    print "Connect DMM to the calibrator, HI to DMM HI, LO to DMM LO. Use low-thermal shielded 1m cable"
    print "Allow 8 hour warm-up"
    print "Select DCV Function, 10NPLC, FILTER 10 AVER, Manual Range"
    print "Set MFC output to 0mV"
    print "Enable REL. Leave REL till DCV test finish"

def f5720_dutinit():
    f5720_id()
    f5720_setup()
    
def f5720_dcvperf(value):
    if (value < 1.0):
        print ("Set MFC to %.8f mVDC" % (value * 1E3))
    else:
        print ("Set MFC to %.8f VDC" % value)
    print "Allow 60sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 8E-6)
    return reading

def f5720_dciperf(value):
    if (value < 1.0):
        print ("Set MFC to %.8f mADC" % (value * 1E3))
    else:
        print ("Set MFC to %.8f ADC" % value)
    print "Allow 20sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 2.5E-6)
    return reading

def f5720_resperf(value):
    print ("Set resistance to %.8E Ohm" % value)
    print "Allow 30sec to settle"
    print "Take K2002 reading"
    reading = (value + value * 5E-6)
    return reading
    
def f5720_acvperf(value, freq):
    if (value < 1.0):
        print ("Set MFC to %.8f mVAC at %d Hz" % (value * 1E3, freq))
    else:
        print ("Set MFC to %.8f VAC at %d Hz" % (value, freq))
    #print "Allow 20sec to settle"
    #print "Take K2002 reading"
    reading = value
    return reading
    
def f5720_dcvtest():
    dcvresult = []
    print ("Number of DCV tests = %d" % len(f5720_dcv_test_values))
    for testcnt in range (0, len(f5720_dcv_test_values)):
        dcvresult.append(f5720_dcvperf(f5720_dcv_test_values[testcnt]))
    print ("Reset MFC to 0.00000 VDC")
    print ("DCV test complete")
    return dcvresult

def f5720_dcitest():
    dciresult = []
    print ("Connect MFC HI output to CURR IN DMM and MFC LO output to DMM LO")
    print ("Select DCI, FILTER 10 AVER, 10 NPLC, manual range")
    print ("Number of DCI tests = %d" % len(f5720_dci_test_values))
    for testcnt in range (0, len(f5720_dci_test_values)):
        dciresult.append(f5720_dciperf(f5720_dci_test_values[testcnt]))
    print ("Reset MFC to 0.00000 ADC")
    print ("DCI test complete")
    return dciresult

def f5720_uncert():
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

def f5720_measout():
    return intf.read("OUT?")
    
def f5720_dormant(sec):
    global start_time
    global elapsed
    global remaining
    
    sys.stdout.write("\033[4;100H")
    if (cfg.get('calkit', 'no_delays', 1) == 'true'):
        print " ",
    else:
        print "\033[33m\033[4;100H"
        for dorm in range (0,sec):
            time.sleep(1)
            elapsed = time.time() - start_time
            remaining = end_time - (start_time + elapsed)
            sys.stdout.write("\033[2;60H\033[35m; Remaining time: " + time.strftime("%H:%M:%S", time.gmtime(remaining) ) + "    %3.1f %%" % ((( elapsed / test_time) * 100 )) )
            sys.stdout.write('\033[4;%dH.' % ((dorm % 10) + 100))
            if ((dorm % 5) == 0):
                sys.stdout.write('\033[4;100H *********  %d to go    \r' % (sec - dorm) )
		intf.write("FAULT?")
		flt = int(intf.inst.read())
		if (flt >= 2500):
		    intf.write("EXPLAIN? %d" % flt)
		    exp = intf.inst.read()
		    sys.stdout.write('\033[5;5H \033[41;33m CALCHECK returned error %s \033[49;39m\r' % (exp) )
	            sys.stdout.flush()
		    quit()
            sys.stdout.flush()
    print ("\033[39m")
    
def f5720_cal_report(fname, cmd, repline):
    print ("\033[%d;5H Generating %s report                     " % (29+repline,cmd) )
    intf.clear()
    intf.write("*CLS*")
    intf.write(cmd)
    time.sleep(1)
    
    if cfg.get('calkit', 'interface', 1) == 'vxi':
	report = intf.inst.read() # read 32k chars
    elif cfg.get('calkit', 'interface', 1) == 'gpib':
	report = intf.inst.read(len=64000) # read 32k chars
    with open(fname,'ab') as od:
        #print report
        od.write("%s" % report)
    #print "Report %s done\n" % fname

def f5720_calchk():
    print ("\033[27;5H Running CAL ZERO and CAL CHECK ")
    intf.clear()
    intf.write("*CLS*")
    intf.write("CAL_ZERO")
    f5720_dormant(250)
    intf.write ("CAL_CHK")
    f5720_dormant(4130)
    print "\033[27;5H Cal check is done               \n"
    
def f5720_selfcal():
    f5720_setup()
    print ("\033[28;5H Start xDevs.com self-calibration procedures")
    f5720_cal_report (cal_report_check_before,"CAL_RPT? CHECK", 1)
    f5720_cal_report (cal_report_cal_before,  "CAL_RPT? CAL", 2)
    f5720_cal_report (cal_report_const_before,"CAL_RPT? RAW", 3)
    f5720_calchk()
    f5720_cal_report (cal_report_check_after, "CAL_RPT? CHECK", 4)
    f5720_cal_report (cal_report_cal_after,   "CAL_RPT? CAL", 5)
    f5720_cal_report (cal_report_const_after, "CAL_RPT? RAW", 6)
    f5720_cal_report (cal_st_cal_after,       "CAL_SLST? CAL", 7)
    f5720_cal_report (cal_st_shift_after,     "CAL_SLST? CHECK", 8)
    print ("\033[28;5H Done!")
    
def f5720_report_aftercal():
    f5720_setup()
    mfcinfo = f5720_check_info()
    #print mfcinfo
    f5720_cal_report (cal_report_check_after, "CAL_RPT? CHECK", 1)
    f5720_cal_report (cal_report_cal_after,   "CAL_RPT? CAL", 2)
    f5720_cal_report (cal_report_const_after, "CAL_RPT? RAW", 3)
    f5720_cal_report (cal_st_cal_after,       "CAL_SLST? CAL", 4)
    f5720_cal_report (cal_st_shift_after,     "CAL_SLST? CHECK", 5)
    print ("\033[28;5H Done!")
        
def f5720_acvtest():
    acvresult = []
    print ("Disable REL and FILTER")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Number of ACV tests = %d" % 36)
    for testfcnt in range (0, len(f5720_acv_test_fvalue)):
        # Iterate frequencies
        print ("\r")
        for testcnt in range (0, len(f5720_acv_test_values)):
            # Iterate voltages
            if ((testfcnt < 4) or (testfcnt < 6 and testcnt < 4) or (testfcnt < 8 and testcnt < 3) or (testfcnt < 9 and testcnt < 2)):
                acvresult.append(f5720_acvperf(f5720_acv_test_values[testcnt],f5720_acv_test_fvalue[testfcnt]))
                acvresult.append(f5720_acv_test_fvalue[testfcnt])
    #print ("Reset MFC to 0.00000 VAC")
    print ("ACV test complete")
    return acvresult

def f5720_loacvtest():
    acvresult = []
    print ("Disable REL and FILTER")
    print ("Power on MFC and amplifier at least 1 hour")
    print ("Configure ACV Func with AC-TYPE:LOW-FREQ-RMS")
    print ("Number of ACV tests = %d" % 14)
    for testfcnt in range (0, len(f5720_loacv_test_fvalue)):
        # Iterate frequencies
        print ("\r")
        for testcnt in range (0, len(f5720_acv_test_values)):
            # Iterate voltages
            if ( not (testfcnt == 0 and testcnt == 4)):
                acvresult.append(f5720_acvperf(f5720_acv_test_values[testcnt],f5720_loacv_test_fvalue[testfcnt]))
                acvresult.append(f5720_loacv_test_fvalue[testfcnt])
    #print ("Reset MFC to 0.00000 VAC")
    print ("Low Freq ACV test complete")
    return acvresult

def f5720_ocomp(mode):
    print ("RES OCOMP mode = %d" % mode)
    
def f5720_restest():
    resresult = []
    print ("Connect MFC H/L/S+/S- output to DMM H/L/S+/S-")
    print ("Select 4W Res, FILTER 10 AVER, 10 NPLC, OCOMP ON, manual range")
    print ("Select external sense ON at MFC")
    print ("OCOMP cannot be used on ranges >20kOhm")
    print ("Number of RES tests = %d" % len(f5720_res_test_values))
    for testcnt in range (0, len(f5720_res_test_values)):
        if (testcnt > 3):
            f5720_ocomp(0)
            resresult.append(f5720_resperf(f5720_res_test_values[testcnt]))
        else:
            f5720_ocomp(1)
            resresult.append(f5720_resperf(f5720_res_test_values[testcnt]))
    print ("Reset MFC to 0.0000 RES")
    print ("RES test complete")
    return resresult

def f5720_1grtest():
    resresult = []
    print ("Connect 1G Resistor H/L output to DMM H/L")
    print ("Select 2W Res, FILTER 10 AVER, 10 NPLC, manual range")
    f5720_ocomp(0)
    resresult.append(f5720_resperf(f5720_1g_test_value[0]))
    print ("1G RES test complete")
    return resresult
    
def f5720_perftest():
    dutresult = []
    dutresult.append(f5720_dcvtest())
    dutresult.append(f5720_acvtest())
    dutresult.append(f5720_loacvtest())
    #dutresult.append(f5720_pkacvtest())
    dutresult.append(f5720_dcitest())
    #dutresult.append(f5720_acitest())
    dutresult.append(f5720_restest())
    dutresult.append(f5720_1grtest())
    #dutresult.append(f5720_freqtest())
    
    return dutresult

def f5720_out_set(cmd):
    intf.write ("OUT %s" % cmd)
    print ("\033[23;5H\033[33;45m %s       \033[39;49m" % cmd),
    #print cmd

def f5720_out_enable():
    intf.write ("OPER") 
    print ("\033[26;4H\033[41;33mMFC OPERATE \033[49;39m"),
    time.sleep(0.1)

def f5720_out_disable():
    intf.write ("STBY")
    print ("\033[26;4H\033[40;32mMFC STANDBY \033[49;39m"),

def f5720_ext_guard(mode):
    if mode == 1:
	#print ("\033[1;40m-i- External grd on MFC is \033[1;42mON\033[1;49m")
	intf.write ("EXTGUARD ON")
	print ("\033[26;35H\033[31mEXTGRD ON \033[39m"),
    elif mode == 0:
	#print ("\033[1;40m-i- External grd on MFC is \033[1;41mOFF\033[1;49m")
	intf.write ("EXTGUARD OFF")
	print ("\033[26;35H\033[31mEXTGRD OFF\033[39m"),

def f5720_ext_sense(mode):
    if mode == 1:
	#print ("\033[1;40m-i- External sense on MFC is \033[1;42mON\033[1;49m")
	intf.write ("EXTSENSE ON")
	print ("\033[26;20H\033[33mEXTSENSE ON \033[39m"),
    elif mode == 0:
	#print ("\033[1;40m-i- External sense on MFC is \033[1;41mOFF\033[1;49m")
	intf.write ("EXTSENSE OFF")
	print ("\033[26;20H\033[33mEXTSENSE OFF\033[39m"),

def f5720_curr_post(mode):
    if mode == 1:
        intf.write ("CUR_POST NORMAL")
        print ("\033[26;35H\033[33mISRC MAIN \033[39m"),
        time.sleep(1)
    elif mode == 2:
        intf.write ("CUR_POST AUX")
        print ("\033[26;35H\033[33mISRC AUX  \033[39m"),
        time.sleep(1)
    elif mode == 3:
        intf.write ("CUR_POST IB5725")
        print ("\033[26;35H\033[33mISRC 5725 \033[39m"),
        time.sleep(1)

def f5720_read_isr():
    mfc_isr = intf.read("ISR?")
    #mfc_isr = [0, 1]
    return int(mfc_isr[1])

def f5720_select_range():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5720_select_res():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5720_sel_res():
    # Do nothing, use autorange for now
    time.sleep(0.1)
    
def f5720_out_dcv():
    print "Incorrect operation on Fluke MFC"
    time.sleep(0.1)
    
def f5720_out_dci():
    print "Incorrect operation on Fluke MFC"
    time.sleep(0.1)

def f5720_lock_range(status):
    if status == 1:
        intf.write("RANGELCK ON")
        print ("\033[25;35H\033[33mRANGELOCK \033[39m"),
    else:
        intf.write("RANGELCK OFF")
        print ("\033[25;35H\033[33m          \033[39m"),

def f5720_check_rngs():
    rngst = intf.read("RANGE?")
    print ("\033[25;5H            \033[33m\033[25;5H%s\033[39m" % rngst[1]),
    

def f5720_function():
    time.sleep(0.1)

def f5720_out_freq():
    time.sleep(0.1)

def f5720_out_read():
    rngst = intf.read("OUT?")
    val = rngst[1].split(",")
    return float(val[0])

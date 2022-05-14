# -*- coding: utf-8 -*-
# $Id: devices/hp3458.py | Rev 42  | 2019/01/10 07:31:01 clu_wrk $
# xDevs.com HP 3458A module
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 2.7 | RPi3 
# Project maintainers:
#  o Tsemenko Ilya  (@)
# https://xdevs.com/guide/teckit
#
import os.path
import sys
import time
import numbers
import signal
import six
import imp
import numpy as np

if six.PY2:
    import ConfigParser as configparser
    cfg = configparser.ConfigParser()
else:
    import configparser
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';','#',))

cfg.read('teckit.conf')
cfg.sections()

if cfg.get('teckit', 'if_debug') == 'false':
    if cfg.get('teckit', 'interface') == 'gpib':
        import Gpib
    elif cfg.get('teckit', 'interface') == 'vxi':
        import vxi11
    elif cfg.get('teckit', 'interface') == 'visa':
        import visa
        rm = visa.ResourceManager()
    else:
        print ("No Device HW interface defined!")
        quit()

acv_xfers = 1
val2 = 0.0
cnt = 0
tread = 20
temp2 = 0
refhp = 7
reflevel = refhp
prev_t = 0
temp = 18
res_rtd = 0.3

class Timeout():
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass

  def __init__(self, sec):
    self.sec = sec

  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)

  def __exit__(self, *args):
    signal.alarm(0) # disable alarm

  def raise_timeout(self, *args):
    raise Timeout.Timeout()

global mfc
global dmmx
global dmmu

logfn = "f792a_raw_1kv_test.log"
def log(cmd):
    with open(logfn, 'a') as lg:
	stre = (time.strftime("%d/%M/%Y-%H:%M:%S;"))
	lg.write("%s %s\r" % (stre, cmd))
    lg.close()

def init_source_acvxfer():
    print ("\033[3;5H 792A AC/DC XFER MODE ")
    mfc1   = imp.load_source('hulk', 'devices/f5720a.py')                    # Load Fluke 5720+5725 support
    dut   = imp.load_source('dmmx', 'devices/hp3458.py')                    # Load Fluke 5720+5725 support
    global mfc
    mfc = mfc1.hulk(1,0,"5720A")  # GPIB 1
    mfc.mfc_out_acv(0, 0)  # 0 V, 0 Hz
    mfc.mfc_rangelock( cfg.get('acv_xfer', 'range') , 0 , 1 ) # Range Lock MFC
    mfc.mfc_stby()
    log("RANGE 792A = %.3f V, MFC 5720A H2 20, EXTGUARD OFF, EXTSENSE OFF, Direct connection" % float(cfg.get('acv_xfer', 'range')) )
    dmm1   = imp.load_source('dmm', 'devices/hp3458.py')                    # Load Fluke 5720+5725 support
    global dmmx
    dmmx = dmm1.dmm_meter(2,0,"3458B")  # GPIB 1
    dmmx.set_dcv_range(10)
    dmmx.nplc(100)

    log("3458A GPIB11, DCV range, NPLC100, GUARD OFF")
    global dmmu
    dmmu = dut.dmm_meter(11,0,"3458C")  # GPIB 1
    dmmu.set_acvs_range(10)

    print ("  MFC initialized")

def measure_dc_ref(voltage):
    volt_dcp = []
    volt_dcn = []
    samplenum = 12
    snooze = 20 #seconds
    print ("Measuring +DC for %.4f level" % voltage)
    #read for 2 min to give last 5
    mfc.mfc_out_acv ( voltage, 0 )
    mfc.mfc_oper()
    mfc.mfc_oper()
    log("Voltage to MFC = %.4f V, DC+" % voltage)
    #dmmx.set_dcv_range(10)
    dmmx.set_autorange("DCV")
    dmmx.nplc(100)
    for cnt in range(0, 12):
	dmmx.trigger()
        reading = dmmx.read_val()[1]
        log("3458A read soak %.7f +V" % reading)
	print ("\033[%d;145H\033[35m Soaking = %.7f\033[39m" % (cnt +2, reading))
        time.sleep(snooze / samplenum)
    log("Sleep %d s" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
	reading = dmmx.read_val()[1]
	volt_dcp.append(reading)
        log("3458A read %.7f +V" % reading)
	print ("\033[%d;145H\033[36m Read VP = %.7f\033[39m" % (cnt+2, reading))
    print ("Median +DC : %.8e V" % np.median(volt_dcp[3:]))
    print ("Measuring -DC for %.4f level" % voltage)
    log ("Median +DC : %.7f V" % np.median(volt_dcp[3:]))
    log ("Measuring -DC for %.4f level" % voltage)
    #read for 2 min to give last 5
    mfc.mfc_out_acv ( -voltage, 0 )
    mfc.mfc_oper()
    # wait for settle, read dummy values
    for cnt in range(0, 12):
	dmmx.trigger()
        reading = dmmx.read_val()[1]
        log("3458A read soak %.7f -V" % reading)
	print ("\033[%d;145H\033[35m Soaking = %.7f\033[39m" % (cnt + 28, reading))
        time.sleep(snooze / samplenum)
    log("Waited %d sec" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
	reading = abs(dmmx.read_val()[1])
	volt_dcn.append(reading)
        log("3458A read %.7f -V" % reading)
	print ("\033[%d;145H\033[37m Read VN = %.7f\033[39m" % (cnt + samplenum + 3, reading))
    print ("Median -DC : %.8e V" % np.median(volt_dcn[3:]))
    log ("Median -DC : %.8e V" % np.median(volt_dcn[3:]))
    dc_emf = (np.median(volt_dcp[5:]) + np.median(volt_dcn[3:])) / 2
    volt_sdevp = np.std(volt_dcp[8:])
    volt_sdevn = np.std(volt_dcn[8:])
    temf = np.median(volt_dcp[5:]) - dc_emf
    print ("Result reference DC for %.4f level is %.8e VDC, TEMF = %.8e VDC\033[14;145HSDP %.6e SDN %.6e" % (voltage, dc_emf, temf, volt_sdevp, volt_sdevn))
    log ("Result reference DC for %.4f level is %.8e VDC, TEMF = %.8e VDC  HSDP %.6e SDN %.6e" % (voltage, dc_emf, temf, volt_sdevp, volt_sdevn))
    return dc_emf, volt_sdevp, volt_sdevn

def measure_dc_refdut(voltage):
    volt_dcp = []
    volt_dcn = []
    volt_dup = []
    volt_dun = []
    samplenum = 12
    snooze = 20 #seconds
    print ("Measuring +DC for %.4f level" % voltage)
    #read for 2 min to give last 5
    mfc.mfc_out_acv ( voltage, 0 )
    mfc.mfc_oper()
    mfc.mfc_oper()
    log("Voltage to MFC = %.4f V, DC+" % voltage)
    #dmmx.set_dcv_range(10)
    dmmx.set_autorange("DCV")
    dmmx.nplc(100)
    dmmu.set_dcv_range(1)
    dmmu.nplc(100)
    for cnt in range(0, 12):
	dmmx.trigger()
	dmmu.trigger()
        reading = dmmx.read_val()[1]
        readingu = dmmu.read_val()[1]
        log("3458A read soak %.7f +V" % reading)
        log("3458C read soak %.7f +V" % readingu)
	print ("\033[%d;145H\033[35m Soaking = %.7f %.7f\033[39m" % (cnt +2, reading, readingu))
        time.sleep(snooze / samplenum)
    log("Sleep %d s" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
	dmmu.trigger()
	reading = dmmx.read_val()[1]
        readingu = dmmu.read_val()[1]
	volt_dcp.append(reading)
	volt_dup.append(readingu)
        log("3458A read %.7f +V" % reading)
        log("3458C read %.7f +V" % readingu)
	print ("\033[%d;145H\033[36m Read VP = %.7f %.7f\033[39m" % (cnt+2, reading, readingu))
    print ("Median +DC : %.8e V" % np.median(volt_dcp[3:]))
    print ("Measuring -DC for %.4f level" % voltage)
    log ("Median +DC : %.7f V" % np.median(volt_dcp[3:]))
    log ("Measuring -DC for %.4f level" % voltage)

    print ("Median +UDC : %.8e V" % np.median(volt_dup[3:]))
    log ("Median +UDC : %.7f V" % np.median(volt_dup[3:]))

    #read for 2 min to give last 5
    mfc.mfc_out_acv ( -voltage, 0 )
    mfc.mfc_oper()
    # wait for settle, read dummy values
    for cnt in range(0, 12):
	dmmx.trigger()
	dmmu.trigger()
        reading = dmmx.read_val()[1]
        readingu = dmmu.read_val()[1]
        log("3458A read soak %.7f -V" % reading)
        log("3458C read soak %.7f -V" % readingu)
	print ("\033[%d;145H\033[35m Soaking = %.7f %.7f\033[39m" % (cnt + 28, reading, readingu))
        time.sleep(snooze / samplenum)
    log("Waited %d sec" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
	dmmu.trigger()
	reading = abs(dmmx.read_val()[1])
	readingu = abs(dmmu.read_val()[1])
	volt_dcn.append(reading)
	volt_dun.append(readingu)
        log("3458A read %.7f -V" % reading)
        log("3458C read %.7f -V" % readingu)
	print ("\033[%d;145H\033[37m Read VN = %.7f %.7f\033[39m" % (cnt + samplenum + 3, reading, readingu))
    print ("Median -DC : %.8e V" % np.median(volt_dcn[3:]))
    print ("Median -UDC : %.8e V" % np.median(volt_dun[3:]))
    log ("Median -DC : %.8e V" % np.median(volt_dcn[3:]))
    log ("Median -UDC : %.8e V" % np.median(volt_dun[3:]))
    dc_emf = (np.median(volt_dcp[5:]) + np.median(volt_dcn[3:])) / 2
    volt_sdevp = np.std(volt_dcp[8:])
    volt_sdevn = np.std(volt_dcn[8:])
    temf = np.median(volt_dcp[5:]) - dc_emf
    duc_emf = (np.median(volt_dup[5:]) + np.median(volt_dun[3:])) / 2
    volt_udevp = np.std(volt_dup[8:])
    volt_udevn = np.std(volt_dun[8:])
    temfu = np.median(volt_dup[5:]) - duc_emf
    print ("Result reference DC for %.4f level is %.8e VDC, TEMF = %.8e VDC\033[14;145HSDP %.6e SDN %.6e" % (voltage, dc_emf, temf, volt_sdevp, volt_sdevn))
    log ("Result reference DC for %.4f level is %.8e VDC, TEMF = %.8e VDC  HSDP %.6e SDN %.6e" % (voltage, dc_emf, temf, volt_sdevp, volt_sdevn))
    print ("Result DMM DC for %.4f level is %.8e VDC, TEMFU = %.8e VDC\033[14;145USDP %.6e USDN %.6e" % (voltage, duc_emf, temfu, volt_udevp, volt_udevn))
    log ("Result DMM DC for %.4f level is %.8e VDC, TEMFU = %.8e VDC  USDP %.6e USDN %.6e" % (voltage, duc_emf, temfu, volt_udevp, volt_udevn))
    return dc_emf, volt_sdevp, volt_sdevn, duc_emf, volt_udevp, volt_udevn

def measure_acv_det(voltage, freq):
    print ("Measuring AC for %.4f level, %.3e Hz" % (voltage, freq))
    log ("Measuring AC by 792A for %.4f level, %.3e Hz" % (voltage, freq))
    volt_acv = []
    samplenum = 20
    if (voltage <= 1):
	snooze = 70 # seconds settle per 792A manual 1-8
    elif (voltage >= 22):
	snooze = 50 # seconds settle per 792A manual 1-8
    else:
	snooze = 30 # seconds settle per 792A manual 1-8
    #read for 2 min to give last 5
    mfc.mfc_out_acv ( voltage, freq )
    mfc.xfer("OFF")
    mfc.mfc_oper()
    mfc.mfc_oper()
    # wait for settle, read dummy values
    for cnt in range(0, 20):
	dmmx.trigger()
        reading = dmmx.read_val()[1]
	print ("\033[%d;145H\033[35m Soaking = %.7f\033[39m" % (cnt + 28, reading))
        log("3458A read soak %.7f Vac" % reading)
        time.sleep(snooze / samplenum)
    log("Waited %d sec" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
        reading = dmmx.read_val()[1]
	volt_acv.append(reading)
	print ("\033[%d;145H\033[33;1m Reading = %.7f\033[39;0m" % (cnt + 28, reading))
        log("3458A read %.7f Vac" % reading)
    volt_ac = np.median(volt_acv[8:])
    volt_sdev = np.std(volt_acv[18:])
    mfc_uncert = mfc.get_uncert()
    print ("\033[2;0H Result AC readout for %.4f level is %.8e VDC \033[49;145H AC SDEV = %.8e" % (voltage, volt_ac, volt_sdev))
    log ("Result AC readout for %.4f level is %.8e VDC AC SDEV = %.8e; MFC U = %s" % (voltage, volt_ac, volt_sdev, mfc_uncert))
    return volt_ac, volt_sdev, mfc_uncert

def measure_acv_detdut(voltage, freq):
    print ("Measuring AC for %.4f level, %.3e Hz" % (voltage, freq))
    log ("Measuring AC by 792A and 3458C for %.4f level, %.3e Hz" % (voltage, freq))
    volt_acv = []
    volt_acvu = []
    samplenum = 20
    if (voltage <= 1):
	snooze = 70 # seconds settle per 792A manual 1-8
    elif (voltage >= 22):
	snooze = 50 # seconds settle per 792A manual 1-8
    else:
	snooze = 30 # seconds settle per 792A manual 1-8
    #read for 2 min to give last 5
    mfc.mfc_out_acv ( voltage, freq )
    dmmu.set_acvs_range(1)
    if (freq >= 30e3):
	dmmu.set_lfilter("OFF")
    else:
	dmmu.set_lfilter("ON")
    mfc.xfer("OFF")
    mfc.mfc_oper()
    mfc.mfc_oper()
    # wait for settle, read dummy values
    for cnt in range(0, 20):
	dmmx.trigger()
	dmmu.trigger()
        reading = dmmx.read_val()[1]
        readingu = dmmu.read_val()[1]
	print ("\033[%d;145H\033[35m Soaking = %.7f %.7f\033[39m" % (cnt + 28, reading, readingu))
        log("3458A read soak %.7f Vac" % reading)
        log("3458C read soak %.7f Vac" % readingu)
        time.sleep(snooze / samplenum)
    log("Waited %d sec" % snooze)
    for cnt in range(0, samplenum):
	dmmx.trigger()
	dmmu.trigger()
        reading = dmmx.read_val()[1]
        readingu = dmmu.read_val()[1]
	volt_acv.append(reading)
	volt_acvu.append(readingu)
	print ("\033[%d;145H\033[33;1m Reading = %.7f %.7f\033[39;0m" % (cnt + 28, reading, readingu))
        log("3458A read %.7f Vac" % reading)
        log("3458C read %.7f Vac" % readingu)
    volt_ac = np.median(volt_acv[8:])
    volt_sdev = np.std(volt_acv[18:])
    volt_acu = np.median(volt_acvu[8:])
    volt_sdevu = np.std(volt_acvu[18:])
    mfc_uncert = mfc.get_uncert()
    print ("\033[2;0H Result AC readout for %.4f level is %.8e VDC \033[49;145H AC SDEV = %.8e" % (voltage, volt_ac, volt_sdev))
    log ("Result AC 792A readout for %.4f level is %.8e VDC AC SDEV = %.8e; MFC U = %s" % (voltage, volt_ac, volt_sdev, mfc_uncert))
    print ("\033[3;0H Result AC readout for %.4f level is %.8e VDC \033[49;145H AC SDEV = %.8e" % (voltage, volt_acu, volt_sdevu))
    log ("Result AC 3458C readout for %.4f level is %.8e VDC AC SDEV = %.8e; MFC U = %s" % (voltage, volt_acu, volt_sdevu, mfc_uncert))
    return volt_ac, volt_sdev, mfc_uncert, volt_acu, volt_sdevu


def run_flatness_test(xfer_range):
    flatness_res = []
    dc_ref = 0.0
    
    print ("Flatness test starting, RANGE %.4f V" % float(xfer_range))
    
    acv_points = ([2.1e-3, 2.2e-3, 3e-3, 6.0e-3, 7e-3, 10e-3, 19e-3, 20e-3, 21e-3],                        # 22mV
        [19e-3, 20e-3, 30e-3, 50e-3, 60e-3, 100e-3, 120e-3, 190e-3, 200e-3, 210e-3], # 220mV
        [190e-3, 200e-3, 210e-3, 300e-3, 600e-3, 700e-3],                   # 700mV
        [100e-3, 200e-3, 300e-3, 500e-3, 600e-3, 700e-3, 0.9, 1, 1.1],                           # 2.2 V
        #[200e-3, 300e-3, 600e-3, 700e-3, 1, 1.1, 1.9, 2, 2.1],                           # 2.2 V
        [1.9, 2, 2.1, 3, 5, 6, 7],                                  # 7 V
        [6, 7, 8, 9, 9.9, 10, 10.9],                          # 22 V
        #[6, 7, 10, 11, 12, 19, 20, 21],                          # 22 V
        [19, 20, 21, 30, 50, 60, 70],                                 # 70 V
        [60, 70, 90, 100, 120, 190, 200, 210],                          # 220 V
        [100, 190, 200, 210, 220, 250, 300, 500, 600, 700, 750, 1000],         # 1000 V
    )
    
    acv_mapping_792a = [0,0,0,1,2,3,4,5,6,7,8]
                      # 0       1       2      3   4   5   6    7     8
    acv_ranges_792a = [22e-3, 220e-3, 700e-3, 2.2, 7, 22, 70, 220, 1000]
    
    req_range = (float (cfg.get('acv_xfer', 'range') ) )
    
    for rg_idx in range (0,9):
        if (req_range < acv_ranges_792a[rg_idx]):
            continue
        else:
            sel_range = rg_idx
    
    print ("SEL 792A RANGE = %.4f V" % (acv_ranges_792a[sel_range]) )
    
    freq_low_points = [10, 20, 40, 60, 100, 400, 1000, 2000, 5000, 6250, 10000, 20000, 30e3, 50e3, 100e3, 200e3, 300e3, 500e3, 800e3, 1000e3, 1199e3]
    freq_mid_points = [10, 20, 40, 60, 100, 400, 1000, 2000, 5000, 6250, 10000, 20000, 30e3, 50e3, 100e3, 200e3, 300e3]
    freq_hi_points  = [        40, 60, 100, 400, 1000, 2000, 5000, 6250, 10000, 20000, 30e3, 50e3, 100e3]
    
    global mfc
    
    test = raw_input("Make sure 5720A->792A->3458A connections, 3458C and switch 792A RANGE to %.3f V, make sure 792A POWERED!\r\n" % (acv_ranges_792a[sel_range]) )

    testid = 0
    if (acv_ranges_792a[sel_range] < 23):
        for vidx in range (0, len(acv_points[sel_range])):
            print ("Voltage change")
            for fidx in range (0, len(freq_low_points) ):
		if (acv_points[sel_range][vidx] * freq_low_points[fidx] > 2.2e7):
        	    print ("\033[2;2H Skip point %d at %d Hz due to VF limit" % (acv_points[sel_range][vidx], freq_mid_points[fidx]) )
		    log ("Skip point %d at %d Hz due to VF limit" % (acv_points[sel_range][vidx], freq_mid_points[fidx]) )
		    continue
                if (acv_points[sel_range][vidx] > 219) and (freq_low_points[fidx] > 1e3):
        	    print ("\033[2;2H Skip point %d at %d Hz due to VF limit, unboosted" % (acv_points[sel_range][vidx], freq_mid_points[fidx]) )
		    log ("Skip point %d at %d Hz due to VF limit, unboosted" % (acv_points[sel_range][vidx], freq_mid_points[fidx]) )
		    continue
                dc_ref, dstdp, dstdn, udc_ref, udstdp, udstdn = measure_dc_refdut( acv_points[sel_range][vidx] )

                print ("\033[0;80H\033[44;1m POINT %d, Volt %.3g V at freq %.6g Hz      \033[49;0m" % (fidx, acv_points[sel_range][vidx], freq_low_points[fidx]))
		ac_result, acsdev, mfc_unc, acu_result, acsudev = measure_acv_detdut(acv_points[sel_range][vidx], freq_low_points[fidx])
                acdc_diff_ppm = (dc_ref - ac_result) / dc_ref
                acdc_diff_dut_ppm = (udc_ref - acu_result) / udc_ref
		flatness_res.append(["ACV",acv_points[sel_range][vidx],"FREQ", freq_low_points[fidx],"DCM","%.9g, STD P %.3e,N %.3e" % (dc_ref, dstdp, dstdn),\
 "ACM", "%.9g, STD, %.3e" % (ac_result, acsdev), "XFER", "%.3e" % acdc_diff_ppm, "H2U=%s" % (mfc_unc),\
 "DUT DC", "%.9g, DSP %.3e,N %.3e" % (udc_ref, udstdp, udstdn), "ACDUT", "%.9g, STD, %.3e" % (acu_result, acsudev), "XFER_DUT", "%.3e" % acdc_diff_dut_ppm ])
		print ("\033[35;1m\033[%d;0H " % (testid + 34)),
		print (flatness_res[testid]),
		print ("\033[39;9m\033[0;0H"),
		testid = testid + 1
	    testid = 0
    mfc.mfc_stby()
    
    return flatness_res

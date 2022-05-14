# -*- coding: utf-8 -*-
# $Id: main3_dcc_tcr.py | Rev 58  | 2022/04/14 15:34:16 TiNw $
# xDevs.com TEC Experiment app 
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 3.x | RPi3 
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
import imp 
from tools import *

import six
if six.PY2:
    import ConfigParser as ConfigParser
    cfg = ConfigParser.ConfigParser()
else:
    import configparser
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';','#',))
    
sys.path.append('devices')

cfg.read('teckit.conf')
cfg.sections()

print ("\033[2J")
# Device modules 
ext_temp     = 0.0                                                      # Ambient BME280 temperature
ext_rh       = 0.0                                                      # Ambient relative humidity
ext_pressure = 0.0                                                      # Ambient pressure
irc_en = 0                                                              # IRC bot activation flag
acv_xfers = 0
root_dir = ''
fileName4 = root_dir + cfg.get('teckit', 'data_file')

plot_ui()
#create_local_file(fileName4)
if (cfg.get('acv_xfer', 'mode') == 'f792a'):
    create_acv_test_file(fileName4)
    acv_xfers = 1
    from f792a import init_source_acvxfer
    from f792a import run_flatness_test
else:
    create_nvs_local_file(fileName4)

iserver = cfg.get('chatbot', 'irc_server')
ichannel = cfg.get('chatbot', 'irc_channel') 
inick = cfg.get('chatbot', 'irc_nick')
ipasswd = cfg.get('chatbot', 'irc_passwd')

if cfg.get('teckit', 'if_debug') == 'true':
    debug_en = 1
else:
    debug_en = 0
    
if cfg.get('testset', 'slope_shape') == 'lymex_step':
    slope_shape = 10 # Multi-step stage with middle point dwell from lymex idea
elif cfg.get('testset', 'slope_shape') == 'xdevs_step':
    slope_shape = 20 # Multi-step stage with middle point dwell from lymex idea
else:
    slope_shape = 0 # Simple ramp up/down operation

if cfg.get('chatbot', 'irc_bot_enabled') == 'true':
    irc_active = 1
    print ("IRC bot active")
    ircbot = imp.load_source('irc' , 'ircbot/irc.py')                   # Load IRC bot logger
    irc = ircbot.IRC()
    irc.connect(iserver, ichannel, inick, ipasswd)
    itext = irc.get_text() 
    irc.write_text(ichannel, "TECkit Robot, Rev0.01.\n")
else:
    irc_active = 0
    
if cfg.get('teckit', 'env_sensor') == 'bme280':
    from Adafruit_BME280 import *
    env_sensor = BME280(mode=BME280_OSAMPLE_8)
    def read_environment():
        global ext_temp, ext_rh, ext_pressure
        ext_temp     = env_sensor.read_temperature() - 1.0
        ext_rh       = env_sensor.read_humidity()
        ext_pressure = env_sensor.read_pressure() / 100
elif (cfg.get('teckit', 'env_sensor') == "f1620") and (debug_en == 0):
    thp = imp.load_source('f1620' , 'devices/thp_client.py')              # Load Fluke 1620 support
    env_sensor = thp.THP_socket(cfg.get('teckit', 'env_1620_ip'), int(cfg.get('teckit', 'env_1620_port')) )
    def read_environment():
        global ext_temp, ext_rh, ext_pressure
        error, ext_temp, ext_rh, ext_pressure = env_sensor.getTHP()
else:
    def read_environment():                                             # Dummy placeholder if no BME280 configured
        global ext_temp, ext_rh, ext_pressure
        ext_temp     = 0
        ext_rh       = 0
        ext_pressure = 0    

b_temp = 0 
b_rh = 0 
b_pressure = 0

#box = imp.load_source('f1620' , 'devices/thp_client.py')              # Load Fluke 1620 support
#box_sensor = box.THP_socket(cfg.get('teckit', 'env_1620_ip'), int(cfg.get('teckit', 'env_1620_port')) )
def box_environment():
    global b_temp, b_rh, b_pressure
    error, b_temp, b_rh, b_pressure = 0,0,0,0#box_sensor.getTHP()


if (cfg.get('mode', 'no_thermal') == "false") and (debug_en == 0):
    k2510  = imp.load_source('k2510' , 'devices/k2510.py')              # Load Keithley 2510 support
    trm1   = imp.load_source('chub', 'devices/f1529.py')                    # Load Fluke 1529 support
    trm1 = trm1.chub_meter(17,0,"1529")  # GPIB 17


if ((debug_en == 0) and (acv_xfers == 0)):
    trm1   = imp.load_source('chub', 'devices/f1529.py')                    # Load Fluke 1529 support
    trm1 = trm1.chub_meter(17,0,"1529")  # GPIB 17

    #scan1   = imp.load_source('k7168_client', 'devices/k7168_client.py')                 # Load Keysight 3458A support
    #acse    = imp.load_source('c61604', 'devices/c61604.py')                 # Load Keysight 3458A support
    dmm1   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
    dmm2   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
    dmm3   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
    dmm4   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
    #dmm4   = imp.load_source('k2002' , 'devices/k2002.py')                  # Load Keithley 2002 support
    #dmm6   = imp.load_source('k2002' , 'devices/k2002.py')                  # Load Keithley 2002 support
    #dmm5   = imp.load_source('f8508a' , 'devices/f8508a.py')                # Load Fluke 8508A support
    #dmm5   = imp.load_source('hp34420a' , 'devices/hp34420.py')                # Load Fluke 8508A support
    dmm7   = imp.load_source('d1281' , 'devices/d1281.py')                # Load Datron 1281 support
    #em1    = imp.load_source('hp53131' , 'devices/hp53131a.py')             # Load support for K6517
    #dmm5   = imp.load_source('r6581t' , 'devices/r6581t.py')                # Load support for R6581T
    #ilx5910= imp.load_source('ilx5910', 'devices/ilx.py')                   # Load support for ILX 5910B
    #dmm8   = imp.load_source('k2182' , 'devices/k2182.py')                  # Load support for K2002
    #dmm8   = imp.load_source('k2182' , 'devices/k2182.py')                  # Load support for K2002
    #em1     = imp.load_source('b2980' , 'devices/b2987a.py')                  # Load support for K2002
    dcc1      = imp.load_source('mi6010', 'devices/mi6010.py')

    #dmm6   = imp.load_source('k2182' , 'devices/k2182.py')                  # Load support for K2002
    #dmm7   = imp.load_source('k182m' , 'devices/k182m.py')                  # Load support for K182M
    #mfc    = imp.load_source('f5700', 'devices/f5700a.py')                  # Load support for F5700A
    #scan = k7168_client.THP_socket('192.168.1.119',10001)                  # External scanner

    dmm1 = dmm1.dmm_meter (1,0,"3458B")  # GPIB 
    dmm2 = dmm2.dmm_meter (3,0,"3458A") # GPIB 
    dmm3 = dmm3.dmm_meter (11,0,"3458C")  # GPIB 
    dmm4 = dmm4.dmm_meter (23,0,"3458C")  # GPIB 

    #acs    = acse.source (7,0,"C61604")
    #dmm2 = dmm2.dmm_meter (5,0,"3458ABE")  # GPIB 2
    #em1 = em1.em_meter(23,0,"B2987A") 
    #dmm2 = dmm2.dmm_meter (2,0,"3458V")  # GPIB 3
    #dmm3 = dmm3.dmm_meter (2,0,"3458B") # GPIB 
    #trm1 = trm1.chub_meter(17,0,"1529")  # GPIB 17
    #dmm1 = dmm1.dmm_meter (5,0,"3458M")  # GPIB 
    #dmm4 = dmm4.dmm_meter (11,0,"3458C") # GPIB
    #dmm6 = dmm6.scpi_meter(6,0,"2002-6") # GPIB  
    #dmm8 = dmm8.scpi_meter(19,0,"2182A") # GPIB 
    #dmm4 = dmm4.scpi_meter(4,0,"2002-4") # GPIB 
    #dmm7 = dmm7.k182m_meter(16,0,"182M")
    #dmm5 = dmm5.flk_meter(15,0,"8508")
    #dmm5 = dmm5.scpi_meter(5,0,"34420")
    dmm7 = dmm7.dat_meter(8,0,"1281")
    #dmm6 = dmm6.scpi_meter(6,0,"2002-6") # GPIB 
    #dmm8 = dmm8.flk_meter(15,0,"8508")
    dcc   = dcc1.dcc_bridge(15,0,"6010B")
    dcc.measure_init()
    #dmm1.set_dci_range(1e-3)                                                # 3458A function/range config
    #em1.set_curr_range(1e-6)                                                # 3458A function/range config
    dmm1.set_dcv_range(0.1)                                                # 3458B function/range config
    dmm2.set_dcv_range(0.1)                                                # 3458B function/range config
    dmm3.set_dcv_range(0.1)                                                # 3458B function/range config
    dmm4.set_dcv_range(0.1)                                                # 3458B function/range config
    #dmm2.set_ohmf_range(100)                                                # 3458B function/range config
    #dmm3.set_ohmf_range(1e3)                                                # 3458B function/range config
    #dmm1.set_ohmf_range(1e3)                                                # 3458B function/range config
    #dmm3.set_dcv_range(1)                                                # 3458B function/range config

    # Some unused configuration code for other meters
    #dmm4.set_dcv_range(10)                                                # 3458C function/range config
    #dmm6.set_dcv_range(10)                                                # 3458D function/range config
    #dmm7.set_dci_range(1e-3)                                                # 182M function/range config
    #dmm7.dis_rel()
    #dmm3.set_ohmf_range(10000)                                                # 3458D function/range config
    #dmm4.set_zero(1)
    #dmm6.set_dci_range(1e-3)                                                # K2002-6 function/range config
    dmm7.set_tohmf_range(190e3)                                                # 3458D function/range config
    dmm7.set_input("CH_A")               # Select front terminals, 5720A H1 10k
    #dmm6.set_dcv_range(10)                                                # K2002-4 function/range config
    #dmm7.set_dcv_range(10)                                                # K2002-4 function/range config
    #dmm8.set_ohmf_range(10e3)                                                # D1281 function/range config
    #dmm1.set_dcv_range(10)                                                # 3458A function/range config
    #dmm5.set_ohmf_range(1)                                                # 3458B function/range config
    #dmm5.set_dcv_nrange(0.010,1)                                                # 3458C function/range config
    #dmm5.set_dcv_nrange(0.10,2)                                                # 3458D function/range config
    #dmm6.set_dcv_range(10)                                                # K2002-6 function/range config
    #dmm8.set_dcv_nrange(1,1)                                                # 3458D function/range config
    #dmm4.set_ohmf_range(100e3) # 6581T
    #dmm1.set_ohmf_fast_range(10e3) #2
    #dmm3.set_ohm_range(200e3) #6
    #dmm2.set_tohm_rel_range(10000) #3458-3
    #dmm2.set_dcv4w_range(10) # 3459b
    #dmm4.set_pt1000_rtd() #4
    #dmm1.set_d_range(10) #4
    #dmm2.set_dcv_range(10) #4

# Module support for Delta-resistance measurement modes
if cfg.get('testset', 'mode') == 'delta3':
    delta_res = 3
    from delta3 import *
else:
    delta_res = 0

if cfg.get('testset', 'mode') == 'delta4':
    delta_res = 4
    print ("DELTA")
    from delta4_1281 import *
else:
    delta_res = 0

if cfg.get('testset', 'mode') == 'deltan':
    delta_res = 5
    from deltan import *
else:
    delta_res = 0

# Example experiment ramp sweep settings
'''
               Peak_temp
               ______
              /      \
             | Step   \
            /          \
   Slope_pos            \ Slope_neg
          /              \
time_start Speed_pos / neg\  time_end
  ------/                  \--------- TEC temp
 Sv_start                    Sv_end
       2h     9h    2h    9h       2h
'''

cur1                = float(cfg.get('testset', 'delta_ipos'))        # Positive current level for Delta-resistance mode
cur2                = float(cfg.get('testset', 'delta_ineg'))        # Negative current level for Delta-resistance mode

tps                 = 1.0                                               # Time per step calculation variable
sv_start            = float(cfg.get('testset', 'sv_start'))          # Chamber start temperature
sv_end              = float(cfg.get('testset', 'sv_end'))            # Chamber end temperature
peak_temp           = float(cfg.get('testset', 'peak_temp'))         # Top soak temperature
min_temp            = float(cfg.get('testset', 'min_temp'))          # Chamber min temp plateau
max_temp            = float(cfg.get('testset', 'max_temp'))          # Chamber max temp plateau
base_temp           = float(cfg.get('testset', 'base_temp'))         # Base temperature for xDevs slope
slope_pos           = float(cfg.get('testset', 'slope')) * 3600      # Steps for the positive slope
slope_neg           = float(cfg.get('testset', 'slope')) * 3600      # Steps for the negative slope
time_start          = float(cfg.get('testset', 'time_start')) * 3600 # Initial hold temperature time, before positive slope starts
time_hold           = float(cfg.get('testset', 'time_hold')) * 3600  # Hold temperature for peak value
time_end            = float(cfg.get('testset', 'time_end')) * 3600   # Hold temperature once rampdown finished
if (cfg.get('testset', 'slope_shape') == 'lymex_step'):
    time_dwell          = float(cfg.get('testset', 'time_dwell')) * 3600 # Dwell temperature duration once reached peak_temp soak
    total_time          = time_start + time_hold + time_dwell + time_dwell + time_end + slope_pos + slope_neg # Test time, in seconds
elif (cfg.get('testset', 'slope_shape') == 'xdevs_step'):
    time_dwell          = float(cfg.get('testset', 'time_dwell')) * 3600 # Dwell temperature duration once reached peak_temp soak
    total_time          = time_start + time_hold + time_dwell + time_dwell + time_end + slope_pos + slope_pos + slope_neg + slope_neg # Test time, in seconds
else:
    time_dwell          = 0 # No dwell step in simple setup
    total_time          = time_start + time_hold + time_dwell + time_dwell + time_end + slope_pos + slope_neg # Test time, in seconds

reference1          = float(cfg.get('dut', 'reference1'))            # Reference value 1
reference2          = float(cfg.get('dut', 'reference2'))            # Reference value 2
reference3          = float(cfg.get('dut', 'reference3'))            # Reference value 3
reference4          = float(cfg.get('dut', 'reference4'))            # Reference value 4
reference5          = float(cfg.get('dut', 'reference5'))            # Reference value 5
reference6          = float(cfg.get('dut', 'reference6'))            # Reference value 6
reference7          = float(cfg.get('dut', 'reference7'))            # Reference value 7
reference8          = float(cfg.get('dut', 'reference8'))            # Reference value 8
ppm_delta           = 0.0
ppm_delta2          = 0.0

pid_kp              = float(cfg.get('pid', 'kp'))                    # P coefficient for thermostat controller
pid_ki              = float(cfg.get('pid', 'ki'))                    # I coefficient for thermostat controller
pid_kd              = float(cfg.get('pid', 'kd'))                    # D coefficient for thermostat controller

if (cfg.get('mode', 'no_thermal') == "false") and (debug_en == 0):
    # If thermal control activated, perform initialization for PID hardware
    tecsmu = k2510.tec_meter(25,0,"2510")
    tecsmu.set_tmp("%5.3f" % sv_start)
    tecsmu.set_gain(pid_kp)
    tecsmu.set_intg(pid_ki)
    tecsmu.set_derv(pid_kd)
    tecsmu.on_temp()

elapsed_time        = 0
remaining_time      = 0
idx                 = 0                                                 # Sample index
sv_temp             = sv_start                                          # Set value temperature
pv_temp             = 0.0                                               # Process temperature value
tec_curr            = 0.0                                               # TEC current monitoring
tread               = 23                                                # Interval for reading 3458A's TEMP?
meas_val            = 0.0                                              # DUT1 reading
meas_val2           = 0.0                                               # DUT2 reading
meas_val3           = 0.0                                               # DUT3 reading
meas_val4           = 0.0                                               # DUT4 reading
meas_val5           = 0.0                                               # DUT5 reading
meas_val6           = 0.0                                               # DUT6 reading
meas_val7           = 0.0                                               # DUT7 reading
meas_val8           = 0.0                                               # DUT8 reading
meas_vbl            = 0.0                                               # DUT1 reading
meas_vbl2           = 0.0                                               # DUT2 reading
meas_vbl3           = 0.0                                               # DUT3 reading
meas_vbl4           = 0.0                                               # DUT4 reading
meas_vbl5           = 0.0                                               # DUT5 reading
meas_vbl6           = 0.0                                               # DUT6 reading
meas_vbl7           = 0.0                                               # DUT7 reading
meas_vbl8           = 0.0                                               # DUT8 reading
meas_k4             = 0.0                                               # DUT8 reading
meas_k6             = 0.0                                               # DUT8 reading
meas_vsv            = 0.0                                               # DUT8 reading
meas_sza            = 0.0                                               # DUT8 reading
dmm1_temp           = 26                                                # DMM1 TEMP? value
dmm2_temp           = 26                                                # DMM2 TEMP? value
dmm3_temp           = 26                                                # DMM3 TEMP? value
dmm4_temp           = 26                                                # DMM4 TEMP? value
acv_curr_rms        = 0.0
acv_curr_cres       = 0.0
acv_curr_inr        = 0.0
acv_freq            = 0.0
acv_pow_ac_real     = 0.0
acv_pow_ac_app      = 0.0
acv_pow_ac_reac     = 0.0
acv_pow_ac_pfac     = 0.0
acv_volt_rms        = 0.0

if irc_active:
    itext = irc.get_text() 
    irc.write_text(ichannel, "TECkit settings: Start %.3f C, Dwell %.3f C, End %.3f C, time = %d s" % (sv_start, peak_temp, sv_end, total_time))
    
w, h = 8, 1000;
ch_data = [[0 for x in range(w)] for y in range(h)] 
ew, eh, ech = 3, 1000, 8;
env_data = [[[0 for x in range(ew)] for y in range(eh)] for z in range(ech)] 
dc, dh = 8, 1000;
tsp_data = [[0 for x in range(dc)] for y in range(dh)] 

delay_start = int(cfg.get('testset', 'delay_start'))                 # Hold delay in seconds
if (delay_start != 0):
    print ("\033[1;1H-i- Waiting for delayed start %d seconds" % delay_start)
    dormant(delay_start)

if irc_active:
    itext = irc.get_text() 
    irc.write_text(ichannel, "Created file %s" % (fileName4))

if (cfg.get('mode', 'no_thermal') == "false"):
    print ("\033[9;72H \033[0;32mSet Temp     : %2.3f %cC\033[0;39m" % (25.0, u"\u00b0"))
    print ("\033[10;72H \033[1;32mProcess Temp : %2.3f %cC\033[0;39m" % (25.0, u"\u00b0"))
    print ("\033[11;72H \033[1;35mTEC Current  : %5.4f  A\033[0;39m" % (25.0))
    print ("\033[12;72H \033[1;33mStatus       : %s\033[0;39m" % (tec_status[5]) )
    print ("\033[13;72H \033[0;33mGain         : %9.4f \033[0;39m" % (pid_kp))
    print ("\033[14;72H \033[0;36mIntergal     : %9.4f \033[0;39m" % (pid_ki))
    print ("\033[15;72H \033[0;31mDerivative   : %9.4f \033[0;39m" % (pid_kd))

#print "\033[9;40H \033[1;34mMeter mode   : %s \033[0;39m" % (dmm_mode[0])
print ("\033[10;40H \033[1;38mMeasured val :%11.8g\033[0;39m" % (1000.04323))
print ("\033[11;40H \033[0;32mOCOMP/DELAY  : %d, %d sec\033[0;39m" % (1, 0))
#print "\033[12;40H \033[0;32mFixed range  : %s\033[0;39m" % (dmm_status[0])
print ("\033[13;40H \033[0;36mNPLC         : %9.4f \033[0;39m" % (100))
#print "\033[14;40H \033[0;37mTerminals    : %s \033[0;39m" % (dmm_terminal[0])
#print "\033[15;40H \033[0;37mREL Value    :%11.8G \033[0;39m" % (1e-6)
print ("\033[11;2H \033[1;32mMin temp     : %.3f %cC\033[0;39m" % (sv_start, u"\u00b0"))
print ("\033[12;2H \033[1;32mPeak temp    : %.3f %cC\033[0;39m" % (peak_temp, u"\u00b0"))

def read_all_dmm_temps():
    dvm_t1 = dmm1.get_temp()     # Read TEMP? from 3458A 1
    dvm_t2 = dmm2.get_temp()     # Read TEMP? from 3458A 2
    dvm_t3 = dmm3.get_temp()     # Read TEMP? from 3458A 3
    dvm_t4 = dmm4.get_temp()     # Read TEMP? from 3458A 4
    return dvm_t1, dvm_t2, dvm_t3, dvm_t4

icnt = 0
if ((debug_en == 0) and (acv_xfers == 0)):
    dmm1_temp, dmm2_temp, dmm3_temp, dmm4_temp = read_all_dmm_temps()
tread = int(cfg.get('dmm', 'readtemp_period'))

if (cfg.get('mode', 'run_acal') == "true") and (debug_en == 0):
    dmm1.inst.write("ACAL ALL") # Start ACAL sequence for 3458A
    dmm2.inst.write("ACAL ALL") # Start ACAL sequence for 3458A
    dmm3.inst.write("ACAL ALL") # Start ACAL sequence for 3458A
    dmm4.inst.write("ACAL ALL") # Start ACAL sequence for 3458A
    print ("\033[18;3H-i- Started ACAL ALL for 860 seconds")
    dormant(860)
    total_time = total_time + 860

if (cfg.get('mode', 'run_acal_dcv') == "true") and (debug_en == 0):
    dmm1.inst.write("ACAL DCV") # Start ACAL sequence for 3458A
    dmm2.inst.write("ACAL DCV") # Start ACAL sequence for 3458A
    dmm3.inst.write("ACAL DCV") # Start ACAL sequence for 3458A
    dmm4.inst.write("ACAL DCV") # Start ACAL sequence for 3458A
    print ("\033[18;3H-i- Started ACAL DCV for 150 seconds")
    total_time = total_time + 150

tread = int(cfg.get('dmm', 'readtemp_period'))

if (acv_xfers == 1):
    # Perform ACV 792 Transfer suite
    print ("\033[2J") # Clear screen
    init_source_acvxfer()
    test_start_time = time.strftime("%d/%m/%Y-%H:%M:%S;")
    ac_data = run_flatness_test( cfg.get('acv_xfer', 'range') )
    with open(fileName4, 'a') as o1:  # Open file handles for storing values
        o1.write ("%s" % test_start_time)
        o1.write ("\r\n%s\r\n" % ac_data)
        sys.stdout.flush()
        o1.write (time.strftime("%d/%m/%Y-%H:%M:%S;"))
        o1.close()
    quit()

sdev_arr1 = []
sdev_arr2 = []
sdev_arr3 = []
sdev_arr4 = []
sdev_arr5 = []
sdev_arr6 = []
sdev_arr7 = []
sdev_arr8 = []

timing_init   = time.time()
timing_step   = 1.0

print ("\033[30;5H \033[0;35mREF    A:%11.6G  B:%11.6G  C:%11.6G  D:%11.6G  E:%11.6G \033[0;39m" % (reference1, reference2, reference3, reference4, reference5))
print ("\033[36;0H")

meas_val4 = dcc.measure() # Read first dummy value from 6010B

# Main ramp loop
while (idx <= (total_time / tps) ):

    if (idx == 1):
        timing_init   = float(time.time())

    if cfg.get('teckit', 'env_sensor') == 'bme280':
        ext_temp     = env_sensor.read_temperature()
        ext_rh       = env_sensor.read_humidity()
        ext_pressure = env_sensor.read_pressure() / 100
        print ("\033[34;67H \033[1;31m%2.3f%cC  \033[1;32m%3.1f%%RH  \033[1;33m%4.1f hPa\033[0;39m" % (ext_temp, u"\u00b0", ext_rh, ext_pressure))
    elif (cfg.get('teckit', 'env_sensor') == "f1620") and (debug_en == 0):
        error, ext_temp, ext_rh, ext_pressure = env_sensor.getTHP()
        print ("\033[34;67H \033[1;31m%2.3f%cC  \033[1;32m%3.1f%%RH  \033[1;33m%4.1f hPa\033[0;39m" % (float(ext_temp), u"\u00b0", float(ext_rh), float(ext_pressure)))
    else:
        ext_temp     = 24.0
        ext_rh       = 0
        ext_pressure = 0

    print ("\033[9;2H \033[44;32m\033[1mSample       : %8d   \033[0;39m" % (idx))
    print ("\033[10;2H \033[1;38mNext temp    : %.3f %cC\033[0;39m" % (sv_temp, u"\u00b0"))

    if (idx == 2):
        #print tps, timing_step, timing_init
        tps = abs(float(timing_step))
        #print tps, timing_step, time.time()
    rm, rs = divmod((total_time - (idx * tps)), 60)
    rh, rm = divmod(rm, 60)
    print ("\033[13;2H \033[1;35mRemaining    : %2dh %02dm %02ds \033[0;39m" % (rh, rm, rs))
    em, es = divmod((idx * tps), 60)
    eh, em = divmod(em, 60)
    print ("\033[14;2H \033[1;35mElapsed time : %2dh %02dm %02ds \033[0;39m" % (eh, em, es))
    print ("\033[15;2H \033[1;35mSample period: %.2f sec \033[0;39m" % (tps))
    print ("\033[5;72H \033[1;35mTotal points : %6d   \033[0;39m" % (total_time / tps))
    print ("\033[4;72H \033[0;30m\033[42mProgress     : %3.2f%% \033[49m\033[0;39m" % ((float(idx) / float(total_time / tps) ) * 100))

    if slope_shape == 10:
        temp_dwell   = sv_start + ((peak_temp - sv_start) / 2) # Dwell temperature point
        temp_nslope1 = peak_temp - temp_dwell                  # Negative slope peak to dwell ramp delta
        temp_nslope2 = temp_dwell - sv_end                     # Negative slope dwell to end ramp delta
        time_slopep = slope_pos / 2
        time_slopen = slope_neg / 2
    if slope_shape == 20:
        # xDevs steps
        temp_dwell   = base_temp                                # Dwell temperature point
        temp_nslope1 = base_temp - min_temp                     # Negative slope peak to dwell ramp delta
        temp_nslope2 = max_temp - base_temp                     # Negative slope dwell to end ramp delta
        time_slopep = slope_pos
        time_slopen = slope_neg
    
    dur_start  = float(time_start) / tps
    dur_ramp1  = float(time_start + time_slopep) / tps
    dur_dwellp = float(time_start + time_slopep + time_dwell) / tps
    dur_ramp2  = float(time_start + slope_pos + time_dwell + slope_pos) / tps
    dur_peak   = float(time_start + slope_pos + time_dwell + slope_pos + time_hold) / tps
    dur_ramn1  = float(time_start + slope_pos + time_dwell + slope_pos + time_hold + time_slopen) / tps
    dur_dwelln = float(time_start + slope_pos + time_dwell + slope_pos + time_hold + time_slopen + time_dwell) / tps
    dur_ramn2  = float(time_start + slope_pos + time_dwell + slope_pos + slope_pos + time_hold + slope_neg + time_dwell) / tps
    dur_end    = float(total_time + slope_pos + slope_pos) / tps
        
    dur_ramp = float((time_start + slope_pos) / tps)
    dur_ramn = float((time_start + slope_pos + time_dwell + time_hold + slope_neg) / tps)
        
    #print (dur_start ,dur_ramp1 ,dur_dwellp,dur_ramp2 ,dur_peak  ,dur_ramn1 ,dur_dwelln,dur_ramn2 ,dur_end, dur_ramp, dur_ramn)
    #quit()
    
    if slope_shape == 10:
    # Lymex slope generator
        # Sample and mode sequencer
        if (idx <= dur_start):
            # Holding for start
            sv_temp = sv_start
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[0]))
        elif (idx >= dur_start ) and (idx < dur_ramp1):
            # Start positive slope ramp
            temp_pslope = temp_dwell - sv_start                   # Positive slope to dwell ramp delta
            dur_pslope = dur_ramp1 - dur_start
            sv_temp = sv_start + ( (temp_pslope / dur_pslope) * (idx - dur_start ) )
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[1]))
        elif (idx >= dur_ramp1) and (idx < dur_dwellp):
            # Dwell step
            sv_temp = temp_dwell
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[2]))
        elif (idx >= dur_dwellp ) and (idx < dur_ramp2):
            # Continue positive slope ramp
            temp_pslope = peak_temp - temp_dwell                  # Positive slope dwell to peak ramp delta
            dur_pslope = dur_dwellp - dur_ramp2
            sv_temp = peak_temp - ( (temp_pslope / dur_pslope) * (idx - ((time_start + slope_pos + time_dwell) / tps ) ) )
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[3]))
        elif (idx >= dur_ramp2) and (idx < dur_peak):
            # Keep peak hold temp
            sv_temp = peak_temp
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[4]))
        elif (idx >= dur_peak) and (idx < dur_ramn1):
            # Ramp down from peak to dwell
            temp_nslope = peak_temp - temp_dwell               # Negative slope 1
            dur_nslope = dur_peak - dur_ramn1
            sv_temp = peak_temp + ( (float(idx) - dur_peak) * (temp_nslope / dur_nslope) )
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[5]))
        elif (idx >= dur_ramn1) and (idx < dur_dwelln):
            # Dwell step
            sv_temp = temp_dwell
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[6]))
        elif (idx >= dur_dwelln) and (idx < dur_ramn2):
            # Ramp from dwell to end
            temp_nslope = temp_dwell - sv_end                  # Negative slope 2
            dur_nslope = dur_dwelln - dur_ramn2
            sv_temp = temp_dwell + ( (float(idx) - dur_dwelln) * (temp_nslope / dur_nslope) )
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[7]))
        elif (idx >= dur_ramn2) and (idx < dur_end):
            # Hold end
            sv_temp = sv_end
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[8]))
        elif (idx >= dur_end):
            sv_temp = sv_start
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[9]))
            print ("\033[36;1H\r\n")
            if (cfg.get('mode', 'no_thermal') == "false"):
                if (cfg.get('teckit', 'if_debug') == "false"):
                    tecsmu.off_temp()
                print ("\033[2J TECKit run complete.")
                quit()
    elif slope_shape == 20:
    # xDevs slope generator
        # Sample and mode sequencer
        if (idx <= dur_start):
            # Holding for start
            sv_temp = base_temp
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[0]))
        elif (idx >= dur_start ) and (idx < dur_ramp1):
            # Start positive slope ramp
            temp_pslope = max_temp - base_temp                   # Positive slope to dwell ramp delta
            dur_pslope = dur_ramp1 - dur_start
            sv_temp = base_temp + ( (temp_pslope / dur_pslope) * (idx - dur_start ) )
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[1]))
        elif (idx >= dur_ramp1) and (idx < dur_dwellp):
            # Dwell step
            sv_temp = max_temp
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[2]))
        elif (idx >= dur_dwellp ) and (idx < dur_ramp2):
            # Reverse positive slope ramp
            temp_pslope = base_temp - max_temp                 # Positive slope dwell to peak ramp delta
            dur_pslope = dur_dwellp - dur_ramp2
            sv_temp = max_temp - ( (temp_pslope / dur_pslope) * (idx - ((time_start + slope_pos + time_dwell) / tps ) ) )
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[3]))
        elif (idx >= dur_ramp2) and (idx < dur_peak):
            # Keep median hold temp
            sv_temp = base_temp
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[4]))
        elif (idx >= dur_peak) and (idx < dur_ramn1):
            # Ramp down from peak to dwell
            temp_nslope = min_temp - base_temp                # Negative slope 1
            dur_nslope = dur_peak - dur_ramn1
            sv_temp = base_temp - ( (float(idx) - dur_peak) * (temp_nslope / dur_nslope) )
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[5]))
        elif (idx >= dur_ramn1) and (idx < dur_dwelln):
            # Dwell step
            sv_temp = min_temp
            print ("\033[12;88H \033[1;34m%s\033[0;39m" % (tec_status[6]))
        elif (idx >= dur_dwelln) and (idx < dur_ramn2):
            # Ramp from dwell to end
            temp_nslope = base_temp - min_temp                 # Negative slope 2
            dur_nslope = dur_dwelln - dur_ramn2
            sv_temp = min_temp - ( (float(idx) - dur_dwelln) * (temp_nslope / dur_nslope) )
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[7]))
        elif (idx >= dur_ramn2) and (idx < dur_end):
            # Hold end
            sv_temp = base_temp
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[8]))
        elif (idx >= dur_end):
            sv_temp = base_temp
            print ("\033[12;88H \033[1;33m%s\033[0;39m" % (tec_status[9]))
            print ("\033[36;1H\r\n")
            if (cfg.get('mode', 'no_thermal') == "false"):
                #if (cfg.get('teckit', 'if_debug') == "false"):
                #    tecsmu.off_temp()
                print ("\033[2J TECKit run complete.")
                quit()
                
    #box_environment()

    #Measurement logic goes here
    if (cfg.get('mode', 'no_thermal') == "false") and (debug_en == 0):
        tecsmu.set_tmp("%5.3f" % sv_temp)
        tecsmu.set_tmp("%5.3f" % sv_temp) # Workaround for programming issue
        tecsmu.set_tmp("%5.3f" % sv_temp) # Workaround for programming issue
        pv_temp, tec_curr = tecsmu.get_data()
        nvm_temp = trm1.get_data_channel(2) #CHUB
        meas_sza = trm1.get_data_channel(1) #CHUB
        meas_k6  = trm1.get_data_channel(3) #CHUB
    else:
        pv_temp = 0.0
        tec_curr = 0.0
        nvm_temp = trm1.get_data_channel(2) #CHUB
        meas_sza = trm1.get_data_channel(1) #CHUB
        meas_k6  = trm1.get_data_channel(3) #CHUB
    
    # Trigger instruments to start conversion in normal mode
    if ((delta_res == 0) and (debug_en == 0)):
        # Collect measurement results
        #dmm1.trigger()
        #dmm2.trigger()
        #dmm3.trigger()
        #dmm4.trigger()
        meas_val  = float(cfg.get('testset', 'dcc_ix')) #dmm5.get_data()
        meas_val2 = float(cfg.get('testset', 'dcc_rs')) #dmm2.read_val()[1] #read_cell(2)
        # RS
        meas_val3 = float(cfg.get('testset', 'dcc_settle_time')) #dmm1.read_val()[1]
        meas_val4 = dcc.measure() #dmm4.get_data() #dmm4.read_val()[1]#read_cell(4)
        #$dmm8.set_tohmf_range(10e3)            # Reconfigure D1281 for 6.5d mode, 1V
        meas_val5 = (meas_val2 * meas_val4) #dmm5.get_data()
        #dmm7.set_tohmf_range(10e3)                # Reconfigure D1281 for 8.5d mode, 10V
        meas_val6 = ((reference5 / meas_val5) - 1) * 1e6   #dmm6.get_data() #dmm8.get_data()
        #dmm7.set_input("CH_A")               # Select front terminals, SR104 10k
        meas_val7 = 0 #
        #dmm7.set_input("CH_B")               # Select front terminals, 5450A 10k
        meas_val8 = 0#dmm8.get_adata() #dmm8.get_data()
        meas_vbl  = 0#dmm1.read_val()[1] #dmm1.read_val()[1] #em1.get_curr() #read_cell(5)
        meas_vbl2 = 0#dmm2.read_val()[1] #dmm1.read_val()[1]#em1.get_volt() #read_cell(6)
        meas_vbl3 = 0#dmm3.read_val()[1] #em1.get_ohm() #read_cell(7)
        meas_vbl4 = 0#dmm4.read_val()[1] #em1.get_ohm() #read_cell(7)
        #meas_vbl4 = 0
        meas_vbl5 = 0#dmm7.get_data()
        #meas_vbl6 = 0
        #meas_vbl7 = 0
        #meas_vbl8 = 0
        #acv_curr_rms        = acs.get_data("CURR:AC")
        #acv_curr_cres       = acs.get_data("CURR:CRES")
        #acv_curr_inr        = acs.get_data("CURR:INR")
        #acv_freq            = acs.get_data("FREQ")
        #acv_pow_ac_real     = acs.get_data("POW:AC:REAL")
        #acv_pow_ac_app      = acs.get_data("POW:AC:APP")
        #acv_pow_ac_reac     = acs.get_data("POW:AC:REAC")
        #acv_pow_ac_pfac     = acs.get_data("POW:AC:FPAC")
        #acv_volt_rms        = acs.get_data("VOLT:ACDC")
        #print ("\033[25;5H %3.4f VRMS %3.3f IRMS %3.3f PRMS %3.3f FREQ" % (acv_volt_rms, acv_curr_rms, acv_pow_ac_real, acv_freq) )

    elif (debug_en == 1):
        #Debug TECKit samples
        meas_val  = idx
        meas_val2 = sv_temp
        meas_val3 = pv_temp
        meas_val4 = tps
        meas_val5 = 0 # dmm5.get_data()
        meas_val6 = (total_time / tps)
        meas_val7 = 0 #
        meas_val8 = 0 #
        
    elif ((delta_res == 3) or (delta_res == 4)) and (debug_en == 0):
        # Collect delta measurement
        print ("DELTARES")
        meas_val, meas_val2, meas_val3, meas_val4, meas_val5, meas_val6, meas_val7 = delta_sample() 
        nvm_temp = trm1.get_data() #CHUB
        #dmm1.trigger()
        #dmm2.trigger()
        #dmm3.trigger()
        #meas_val2 = dmm1.read_val()[1]
        #meas_val3 = dmm2.read_val()[1]
        #meas_val4 = dmm3.read_val()[1]
        meas_vbl = 0#dmm1.read_val()[1]
        meas_vbl2 = 0#dmm2.read_val()[1]
        meas_vbl3 = 0#dmm3.read_val()[1]
        meas_vbl4 = 0#dmm4.get_data()
        meas_vbl5 = 0#dmm5.get_data()
        meas_vbl6 = 0#dmm6.get_data()
        #dmm7.set_input("FRONT")
        #dmm7.set_dcv_range(10)
        meas_vbl7 = 0#dmm7.get_data()
        meas_vbl8 = 0#dmm7.get_data()

    if (delta_res == 5) and (debug_en == 0):
        # Collect delta measurement
        print ("DELTAN")
        meas_val, meas_val2, meas_val3, meas_val4, meas_val5, meas_val6, meas_val7, meas_val8, meas_vbl4, meas_vbl5, meas_vbl6, meas_vbl7, meas_vbl8 = delta_sample()
        meas_vbl = 0#b_temp
        meas_vbl2 = 0#dmm5.get_adata()
        meas_vbl3 = 0#dmm5.get_bdata()
        meas_k4 = 0#dmm4.get_data()
        meas_k6 = 0#dmm6.get_data()
        meas_sza = 0#dmm1.get_data()
        meas_vsv = 0#dmm2.get_data()

    # Add results to array for stats math
    sdev_arr1.extend([meas_val])
    sdev_arr2.extend([meas_val2])
    sdev_arr3.extend([meas_val3])
    sdev_arr4.extend([meas_val4])
    sdev_arr5.extend([meas_val5])
    sdev_arr6.extend([meas_val6])
    sdev_arr7.extend([meas_val7])

    tread = tread - 1
    if (tread == 0) and (debug_en == 0):
        dmm1_temp, dmm2_temp, dmm3_temp, dmm4_temp = read_all_dmm_temps()
        tread = int(cfg.get('dmm', 'readtemp_period'))

    print ("\033[9;88H \033[0;32m%2.3f %cC\033[0;39m" % (sv_temp, u"\u00b0"))
    print ("\033[10;88H \033[1;32m%2.3f %cC\033[0;39m" % (pv_temp, u"\u00b0"))
    print ("\033[11;88H \033[1;35m%5.4f \033[0;39m" % (tec_curr))
    print ("\033[10;55H \033[1;38m%11.8f\033[0;39m" % (meas_val))
    print ("\033[31;3H \033[1;32mMedian A= %.9e      " % np.median(sdev_arr1) )
    print ("\033[32;3H \033[1;32m Sdev A = %.4G     " % ( np.std(sdev_arr1) ) )

    print ("\033[31;28H\033[1;33mB=%.9e " % np.median(sdev_arr3) )
    print ("\033[31;45H\033[1;34mC=%.9e " % np.median(sdev_arr4) )
    print ("\033[31;62H\033[1;35mD=%.9e " % np.median(sdev_arr5) )
    print ("\033[31;79H\033[1;36mE=%.9e " % np.median(sdev_arr6) )
    print ("\033[32;28H\033[1;33mB=%.4G " % ( np.std(sdev_arr3) ) )
    print ("\033[32;45H\033[1;34mC=%.4G " % ( np.std(sdev_arr4) ) )
    print ("\033[32;62H\033[1;35mD=%.6G " % ( np.std(sdev_arr5) ) )
    print ("\033[32;79H\033[1;36mE=%.6G " % ( np.std(sdev_arr6) ) )


    ppm_delta  = ((meas_val / reference1) - 1) * 1e6
    ppm_delta2 = ((meas_val2 / reference2) - 1) * 1e6
    ppm_delta3 = ((meas_val3 / reference3) - 1) * 1e6
    ppm_delta4 = ((meas_val4 / reference4) - 1) * 1e6
    ppm_delta5 = ((meas_val5 / reference5) - 1) * 1e6
    ppm_delta6 = ((meas_val6 / reference6) - 1) * 1e6
    ppm_delta7 = ((meas_val7 / reference7) - 1) * 1e6
    ppm_delta8 = ((meas_val8 / reference8) - 1) * 1e6
    print ("\033[33;13H\033[1;32m %9.3f\033[0;39m" % (ppm_delta))
    print ("\033[33;30H\033[1;33m %9.3f\033[0;39m" % (ppm_delta3))
    print ("\033[33;47H\033[1;34m %9.3f\033[0;39m" % (ppm_delta4))
    print ("\033[33;66H\033[1;35m %9.3f\033[0;39m" % (ppm_delta5))
    print ("\033[33;81H\033[1;36m %9.3f ppm\033[0;39m" % (ppm_delta6))
    
    # Data storage logic goes here
    if (icnt >= 12):
        icnt = 0
    print ("\033[%d;3H[%6d] S%5.3f P%5.3f T%5.3f \033[1;34m A%12.9e \033[0;32mB%12.9e \033[0;33mC%12.9e R\033[0;39m" % (icnt+17, idx, sv_temp, pv_temp, nvm_temp, meas_val, meas_val4, meas_val5) ) 
    icnt = icnt + 1
    if irc_active:
        itext = irc.get_text() 
        irc.write_text(ichannel, "Data: %.8f %.8f %9g %9g %9g F1529: %.3f Ambient: %.2fC" % (meas_val, meas_val2, meas_val3, meas_val4, meas_val6, float(nvm_temp), ext_temp ) )

    with open(fileName4, 'a') as o1:  # Open file handles for storing values
        o1.write (time.strftime("%d/%m/%Y-%H:%M:%S;") \
+ ("%2.12e;%2.12e;%2.12e;%2.12e;%2.12e;%2.12e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%2.9e;%3.1f;%3.1f;%3.1f;%3.1f;%3.3f;%3.1f;%4.1f;%3.3f;%3.3f;%5.3f;%3.3f;\n" \
 % (float(meas_val),float(meas_val2),float(meas_val3),float(meas_val4),float(meas_val5),float(meas_val6),float(meas_val7),float(meas_val8),\
 float(meas_vbl),float(meas_vbl2),float(meas_vbl3),float(meas_vbl4),float(meas_vbl5),float(meas_vbl6),float(meas_vbl7),float(meas_vbl8),float(meas_sza),\
float(meas_vsv),float(meas_k4),float(meas_k6),\
float(dmm1_temp),float(dmm2_temp),float(dmm3_temp),float(dmm4_temp),float(ext_temp),float(ext_rh),float(ext_pressure),pv_temp, float(nvm_temp), tec_curr, sv_temp ) ) )
        sys.stdout.flush()
        o1.close()
    
    #global timing_init
    #global timing_step
    if (idx == 1):
        timing_step  = float(timing_init) - float(time.time())  # Determine duration of one data sample step
    idx+=1                  # Sample index increment

#if (cfg.get('mode', 'no_thermal') == "false") and (debug_en == 0):
#    tecsmu.off_temp()

print ("\033[2J TECKit run complete.")
#mfc    = imp.load_source('f5720', 'devices/f5720a.py')                  # Load support for F5700A
quit()

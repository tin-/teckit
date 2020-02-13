# -*- coding: utf-8 -*-
# $Id: devices/hp4142b.py | Rev 44  | 2020/02/13 19:28:25 tin_fpga $
# xDevs.com Keithley 6221 module
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
import ConfigParser
cfg = ConfigParser.ConfigParser()
cfg.read('teckit.conf')
cfg.sections()

if cfg.get('teckit', 'interface', 1) == 'gpib':
    import Gpib
elif cfg.get('teckit', 'interface', 1) == 'vxi':
    import vxi11
else:
    print "No interface defined!"
    quit()

cnt = 0
tread = 20
temp = 18
cnt = 0
tread = 20
reflevel = 10E3
refhp = 10000.406
res_delta = 0.0
curr1 = 0.0000
curr2 = 0.0000
curr3 = 0.0000
curr4 = 0.0000
volt1 = 1.00000
volt2 = 1.00000
volt3 = 1.00000
volt4 = 1.00000
volt_p1  = 15.000
volt_p2 = -15.000
vmeas1 = 0
vmeas2 = 0

tec_start = 24
tec_stop = 50
tec_step = 0.1
tec_time = 50

tec_rtd = 0.3
temp = 18.0
res_rtd = 0.3
exttemp = 25.0
rh = 50.0
pascals = 100000.00
hectopascals = 1000.00
tset = 18.0
dline = 0

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

class smu_src():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
	print "\033[6;5H \033[0;31mGPIB[\033[1m%2d\033[0;36m] : Agilent 4142B\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        self.reflevel = reflevel
        self.name = name
        self.init_inst_dummy()

    def init_inst_dummy(self):
        # Setup SCPI DMM
        nplc = 1
        #self.inst.write("*rst\n") #reset TEC controller
        #self.inst.write("CM 1\n")
        #self.inst.write("CL 2\n")
        #self.inst.write("CL 4\n")
        self.inst.write("CL 5\n")
        self.inst.write("CL 7\n")
	self.inst.write("AV-%d,1\n" % nplc)
        #print ("\033[2J\033[1;1HNPLC %d" % (nplc)),

    def self_cal(self,ch):
        self.inst.write("CL%d\n" % ch)
        self.inst.write("CA%d\n" % ch)
        print ("\033[1;18H \033[43;31m SELF_CAL CH%d \033[49;39m" % (ch))
        time.sleep(10)
        self.inst.write("CN%d\n" % ch)
        print ("\033[1;18H \033[49;39m              \033[49;39m")

    def src_on(self,ch):
    #    self.inst.write("DZ%d\n" % ch)
        self.inst.write("CN %d\n" % ch)

    def src_meas_mode(self,ch,mode):
        self.inst.write("MM %d,%d\n" % (mode, ch))
    
    def src_off(self,ch):
    #    self.inst.write("DZ%d\n" % ch)
        self.inst.write("CL %d\n" % ch)

    def src_curr(self, ch, value, rang, cmpl):
        rng_str = ["AUTO-IRNG", "", "", "", "", "", "", "", "", "", "", "  1 nADC ", " 10 nADC ", " 100 nADC", "  1 uADC ", " 10 uADC ", "100 uADC ", "  1 mADC ", " 10 mADC ", "100 mADC ", "  1 ADC  "]
        # 0 - autorange, 11 - 1nA, 12 - 10nA, 13 - 100nA, 14 - 1ua, 15 - 10ua, 16 - 100ua, 17 - 1ma, 18 - 10ma, 19 - 100ma, 20 - 1A
        # cmpl           0 - 200v                                                                                 100v        14v
        #print ("\033[%d;40H \033[%d;1mIset = %9.6E A, %s Vcmpl = %E VDC\033[39;0m" % (ch+1, ch+30, value, rng_str[rang], cmpl))
        self.inst.write("DI %d,%d,%9.6e,%.4e\n" % (ch, rang, value, cmpl))

    def src_volt(self, ch, value, rang, cmpl):
        rng_str = ["AUTO-VRNG", "", "", "", "", "", "", "", "", "", "", "  2 VDC  ", " 20 VDC  ", " 40 VDC  ", "100 VDC  ", "200 VDC  "]
        # 0 - autorange, 11 - 2V, 12 - 20V, 13 - 40V, 14 - 100V, 15 - 200V
        # cmpl                     1A       350mA     125mA         50mA
        #print ("\033[%d;40H \033[%d;1mVset = %9.6E V, %s Icmpl = %E ADC\033[39;0m" % (ch+1, ch+30, value, rng_str[rang], cmpl))
	#print ("DV %d,%d,%9.6e,%.5E" % (ch, rang, value, cmpl))
        self.inst.write("DV %d,%d,%9.6e,%.5E\n" % (ch, rang, value, cmpl))

    def vs_volt(self, ch, value, rang):
        rng_str = ["AUTO-VRNG", "", "", "", "", "", "", "", "", "", "", "         ", " 20 VDC  ", " 40 VDC  "]
        # 0 - autorange, 11 - 2V, 12 - 20V, 13 - 40V, 14 - 100V, 15 - 200V
        # cmpl                     1A       350mA     125mA         50mA
        if (ch == 28):
            print ("\033[%d;40H \033[%d;1mVset2 = %3.5E V, %s ILIM = 20 mA\033[39;0m" % (12, 33, value, rng_str[rang]))
        elif (ch == 18):
            print ("\033[%d;40H \033[%d;1mVset1 =  %3.5E V, %s ILIM = 20 mA\033[39;0m" % (11, 33, value, rng_str[rang]))
        self.inst.write("DV %d,%d,%9.6e\n" % (ch, rang, value))

    def vm_mode(self, ch, mode):
        self.inst.write("VM%d,%d\n" % (ch, mode))

    def src_zero(self, ch):
        self.inst.write("DZ%d\n" % (ch))

    def read_data(self,cmd,ch):
        data_float = 0.0
        data_str = ""
        self.inst.write(cmd)
        try:
            with Timeout(90):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            #print("\033[%d;130H %s read_data() - Value = %s" % (ch+1,self.name,data_str))
            data_float = float(data_str[3:])
            #print ("\033[20;20H %s" % data_str[2:3])
            if (data_str[2:3] == "I"):
                print ("\033[%d;28H\033[44;36m Imeas \033[49;39m" % (ch+1))
            elif (data_str[2:3] == "V"):
                print ("\033[%d;28H\033[44;36m Vmeas \033[49;39m" % (ch+1))

            if (data_str[0:1] == "N"):
                print ("\033[%d;14H\033[42;30m\033[5m OPERATING \033[49;39m\033[0m" % (ch+1))
            elif (data_str[0:1] == "T"):
                print ("\033[%d;14H\033[40;37m\033[5m SYS COMPL \033[49;39m\033[0m" % (ch+1))
            elif (data_str[0:1] == "C"):
                print ("\033[%d;14H\033[46;30m\033[5m CHA COMPL \033[49;39m\033[0m" % (ch+1))
            elif (data_str[0:1] == "V"):
                print ("\033[%d;14H\033[41;33m OVERRANGE \033[49;39m" % (ch+1))
	        self.inst.write("CL 2\n")
    		self.inst.write("CL 4\n")
	        self.inst.write("CL 5\n")
	        self.inst.write("CL 7\n")
		quit()
            elif (data_str[0:1] == "X"):
                print ("\033[%d;14H\033[41;33m UNSTABLE  \033[49;39m" % (ch+1))
	        self.inst.write("CL 2\n")
    		self.inst.write("CL 4\n")
	        self.inst.write("CL 5\n")
	        self.inst.write("CL 7\n")
		quit()
            elif (data_str[0:1] == "F"):
                print ("\033[%d;14H\033[41;33m NOT SETTL \033[49;39m" % (ch+1))
	        self.inst.write("CL 2\n")
    		self.inst.write("CL 4\n")
	        self.inst.write("CL 5\n")
	        self.inst.write("CL 7\n")
		quit()
            elif (data_str[0:1] == "W"):
                print ("\033[%d;14H\033[46;34m SWEEP STA \033[49;39m" % (ch+1))
            elif (data_str[0:1] == "E"):
                print ("\033[%d;14H\033[46;34m SWEEP END \033[49;39m" % (ch+1))
            elif (data_str[0:1] == "S"):
                print ("\033[%d;14H\033[45;31m AFU-TOFAS \033[49;39m" % (ch+1))

            return (0,data_str[3:]) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self,ch):
        self.src_meas_mode(ch, 1)
        self.status_flag,data = self.read_data("XE\n",ch)
        #if (self.status_flag):
        self.data = float(data)
        print ("\033[%d;100H Value = %9.8G          " % ((ch+1), self.data) )
        return self.data

    def get_vdata(self,ch):
        self.src_meas_mode(ch, 1)
        self.inst.write("XE\n")
        if (ch == 18):
            chx = 11
        if (ch == 28):
            chx = 12
        try:
            with Timeout(90):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("\033[%d;130H %s read_data() - Value = %s" % (chx,self.name,data_str))
            data_float = float(data_str[3:])
            print ("\033[%d;90H %sMEAS %e" % (chx,data_str[2:3], data_float))
            if (data_str[2:3] == "I"):
                print ("\033[%d;28H\033[44;36m Imeas \033[49;39m" % (chx))
            elif (data_str[2:3] == "V"):
                print ("\033[%d;28H\033[44;36m Vmeas \033[49;39m" % (chx))

            if (data_str[0:1] == "N"):
                print ("\033[%d;14H\033[42;30m\033[5m OPERATING \033[49;39m\033[0m" % (chx))
            elif (data_str[0:1] == "V"):
                print ("\033[%d;14H\033[41;33m OVERRANGE \033[49;39m" % (chx))

            return (0,data_float) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

        self.data = float(data)
        print ("\033[%d;100H Value = %9.8G          " % ((chx), self.data) )
        return data_float

    def get_err(self):
        self.inst.write("ERR?\n")
        try:
            with Timeout(90):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("\033[1;20H ERR %18s             " % (data_str))
        return self.data

    def write_data(self,fileHandle):
        global vmeas1,vmeas2
        global curr1,curr2,curr3,curr4,volt1,volt2,volt3,volt4
        global res_delta
        print ("\033[%d;0H" % (dline + 16)) + time.strftime("%d/%m/%Y-%H:%M:%S;") + ("\033[0;33m[%8d]: \033[32;1m%12.6G \033[34;1m%12.6G \033[35;1m%12.6G \033[37;1m%12.6G V=\033[32;1m%12.6G \033[34;1m%12.6G \033[35;1m%12.6G \033[37;1m%12.6G" % (cnt, curr1, curr2, curr3, curr4, volt1,volt2,volt3,volt4  ) ),
        print ("\033[10;50H \033[33;1mEXT_T:%3.2f , RH:%3.2f , Press:%4.2f hPa\033[39;0m" % (float(exttemp),float(rh),float(hectopascals)))
        fileHandle.write (time.strftime("%d/%m/%Y-%H:%M:%S;") + ("%16.6e;%16.6e;%16.6e;%16.6e;%16.6e;%16.6e;%16.6e;%16.6e;%3.2f;%3.2f;%4.2f;\r\n" % (curr1,curr2,curr3,curr4,volt1,volt2,volt3,volt4,float(exttemp),float(rh),float(hectopascals) ) ))

'''
csrc = smu_src(14, refhp, "4142") # GPIB 14 A4142B # 12 Keithley 6221
print ("\033[1;70H"),
create_local_file(fileName4)
for chi in range (1,8):
    print ("\033[%d;2H\033[1;%dm SMU%d\033[39;0m" % (chi+1, chi+30, chi))

volt1 = 0.00000
volt2 = 0.00000
volt3 = 0.00000
volt4 = 0.00000

csrc.src_off(2) # Turn off SMU1
csrc.src_off(4) # Turn off SMU2
csrc.src_off(5) # Turn off SMU3
csrc.src_off(7) # Turn off SMU4
csrc.get_err()
csrc.get_err()

get_THP() # Read Temp, RH, Pressure from sensor

temp = 29.0

start_gs = -100

tread = 100
cnt = start_gs

csrc.src_on(2) # Turn off SMU1
csrc.src_on(4) # Turn off SMU2
csrc.src_on(5) # Turn off SMU2
csrc.src_on(7) # Turn off SMU2

#I 0 - autorange, 11 - 1nA, 12 - 10nA, 13 - 100nA, 14 - 1ua, 15 - 10ua, 16 - 100ua, 17 - 1ma, 18 - 10ma, 19 - 100ma, 20 - 1A
#V 0 - autorange, 11 - 2V, 12 - 20V, 13 - 40V, 14 - 100V, 15 - 200V

csrc.inst.write("RI2,-14\n") #-15 G1
csrc.inst.write("RI4,-18\n") #-19
csrc.inst.write("RI5,-16\n") #-15 G2
csrc.inst.write("RI7,-18\n") #-19

precision = 0.2 # 0.1V per step
gprecision = 0.2
d1step = 126 # -15 to 15V
g1step = 2 # -15 to 15V

arr1 = np.zeros((d1step, g1step))
arr2 = np.zeros((d1step, g1step))
arr1g = np.zeros((d1step, g1step))
arr2g = np.zeros((d1step, g1step))

g1volt_start = 0.0
g1volt_end = +0.2
d1volt_start = -0.0
d1volt_end = -25.0

g1volt = g1volt_start
d1volt = d1volt_start

strhdr = 'vgs;'
for xi in range (0, g1step):
    strhdr = strhdr + ('vds%1.2f;' % (g1volt_start + (xi * precision)))

d1step = 0
g1step = 0
cnt = 0

#SMU1 - 2, SMU2 = 4, SMU3 = 5, SMU4 = 7
while (1):
    cnt+= 1
    
    csrc.src_on(4)
    csrc.src_on(7)
    csrc.src_volt(2, g1volt, 12, 1e-6) #GATE CH, voltage, 20V range, icmpl
    csrc.src_volt(4, d1volt, 12, 2e-3) #DRAIN CH
    csrc.src_volt(5, g1volt, 12, 100e-6) #GATE CH, voltage, 20V range, icmpl
    csrc.src_volt(7, d1volt, 12, 2e-3) #DRAIN CH
    time.sleep(0.05)
    arr1g[d1step, g1step] = csrc.get_data(2)
    arr1[d1step, g1step] = csrc.get_data(4)
    arr2g[d1step, g1step] = csrc.get_data(5)
    arr2[d1step, g1step] = csrc.get_data(7)
    print '#%d D%.2f %.6e G%.2f %.6e; SD%d SG%d , matching %.3f %%     ' % (cnt, d1volt, arr1[d1step, g1step], g1volt, arr1g[d1step, g1step], d1step, g1step, (((arr1[d1step, g1step] / arr2[d1step, g1step]) - 1) * 100) )

    d1volt = d1volt - precision
    d1step+= 1
    csrc.src_off(4)
    csrc.src_off(7)

    if (g1volt >= g1volt_end):
	csrc.src_off(2) # Turn off SMU1
	csrc.src_off(4) # Turn off SMU2
	csrc.src_off(5) # Turn off SMU3
	csrc.src_off(7) # Turn off SMU4

        
	csrc.src_volt(2, ds, 12, 1e-3) #GATE CH, voltage, 20V range, icmpl
	csrc.src_volt(4, volt2, 12, 0.01) #DRAIN CH
	
	#csrc.src_volt(2, ds, 12, 15e-3) #DRAIN CH, voltage, 20V range, icmpl
        curr1 = csrc.get_data(2)
	curr2 = csrc.get_data(4)

	if (cnt == 550):
	    cnt = start_gs
	    volt2 = volt2 + 1.0

	if (volt2 > 13.0):
	    csrc.src_off(2) # Turn off SMU2
	    csrc.src_off(4) # Turn off SMU2
	    print "JOB DONE"
	    quit()

        global vmeas1,vmeas2
        csrc.write_data(o1)
        
        o1.close()

'''
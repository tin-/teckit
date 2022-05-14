# -*- coding: utf-8 -*-
# $Id: devices/ilx.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
# xDevs.com ILX 5910B module
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
import ftplib
import numbers
import signal
#from Adafruit_BME280 import *
import ConfigParser
cfg = ConfigParser.ConfigParser()
cfg.read('teckit.conf')
cfg.sections()

if cfg.get('teckit', 'interface', 1) == 'gpib':
    import Gpib
elif cfg.get('teckit', 'interface', 1) == 'vxi':
    import vxi11
elif cfg.get('teckit', 'interface', 1) == 'visa':
    import visa
    rm = visa.ResourceManager()
else:
    print "No interface defined!"
    quit()


val2 = 0.0
cnt = 0
tread = 20
rtd_temp = 0.0
tec_rtd = 0.3
tec_curr = 0.0
prev_t = 0
temp = 18
res_rtd = 0.3
tset = 18.0

#time.sleep(1)
#error,data = scan.send("*IDN?")
#print 'ID scanner... Error = ' + str(error) + ' : String = ' + str(data)
    
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

class tec_meter():
    temp = 38.5
    data = ""
    ppm = 0.0
    status_flag = 1
    temp_status_flag = 1
    global exttemp
    global rh
    global hectopascals
    global tec_rtd

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
        print "\033[4;5H \033[0;32mGPIB[\033[1m%2d\033[0;32m] : ILX 5910B\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        elif cfg.get('teckit', 'interface', 1) == 'visa':
            self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
            self.inst.timeout = 300000 # timeout delay in ms

        self.reflevel = reflevel
        self.name = name
        self.tec_rtd = tec_rtd
        self.init_inst()
        
    def init_inst(self):
        # Setup ILX for YSI 44007
        #self.inst.write("*rst") #reset TEC controller
        #self.inst.write("*CLR")
        #Set temperature transducer to thermistor and 4-wire sense mode
        self.inst.write("MODE:T")
        self.inst.write("CONST 1.125,2.347,0.855")      #select thermistor
        self.inst.write("R 10.000") #5 kOhm thermistor
	self.inst.write("LIMIT:ITE 2") #TEC Limiter

        self.inst.write("GAIN 120")            # P
	
        self.inst.write("Limit:Thi 65")  #75C max temp
        self.inst.write("Limit:Tlo 5")   #15C min temp
        self.inst.write("T 20") #enable temp #protection (default)

    def set_gain(self, gain):
        self.inst.write("GAIN %6.4f" % gain)         # P

    def set_intg(self, intgr):
        time.sleep(0.1)
	#self.inst.write(":sour:temp:lcon:INT %5.4f" % intgr)          # I

    def set_derv(self, derv):
        time.sleep(0.1)        
	#self.inst.write(":sour:temp:lcon:DER %5.4f" % derv)          # D

    def cfg_temp(self):
        self.inst.write("T 20.0") #set temp
        self.inst.write("Output 1")
        tec_rtd = 20.0

    def off_temp(self):
        self.inst.write("Output 0")

    def on_temp(self):
        self.inst.write("Output 1")

    def set_tmp(self,tmp):
        string = float(tmp)
        global cnt
        #self.inst.write(":DISP:WIND2:TEXT:DATA \"SV %5.3f C, STEP %6d \";STAT ON;" % (tmp, cnt))
        #print ("Setting %2.1f" % string)
        self.inst.write("T %2.1f" % string) 
#        self.inst.write(":OUTP ON")

    def read_data(self,cmd):
        data_float = 0.0
        data_str = ""
        self.inst.write(cmd)
        try:
            with Timeout(20):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("\033[4;36H\033[31;1mException %s on read_data, ValueError = %s\n\033[39;1m" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        global tec_rtd
        global tec_curr
	#self.inst.clear()
        time.sleep(0.1)
        self.status_flag,data = self.read_data("ITE?")
        tec_curr = float(data)
        if (self.status_flag):
            self.data = data
        time.sleep(0.1)
        self.status_flag,data = self.read_data("T?")
        if (self.status_flag):
            self.data = data
        tec_rtd = float(data)
        return tec_rtd,tec_curr

    def get_data_status(self):
        return self.status_flag

    def write_data(self,fileHandle):
        #print ("TEC TC:%2.3f " % (float(self.data) ) )
        tec_rtd = float(self.data)
        fileHandle.write(";%2.3f;\r\n" % tec_rtd);
        #print time.strftime("%d/%m/%Y-%H:%M:%S;") + ("\033[1;31m[%8d]: %2.8f , dev %4.2f ppm,\033[1;39m  EXT_T:%3.2f , RH:%3.2f , Press:%4.2f hPa" % (cnt, float(self.data),float(self.ppm),float(exttemp),float(rh),float(hectopascals) ) )
        #fileHandle.write (time.strftime("%d/%m/%Y-%H:%M:%S;") + ("%16.8f;%16.8f;%3.1f;%3.2f;%3.2f;%4.2f;\r\n" % (float(self.data),float(self.reflevel),float(self.ppm),float(exttemp),float(rh),float(hectopascals) ) ))

    def print_ppm(self):
        #self.inst.write(":DISP:WIND2:TEXT:DATA \"%3.3f ppm\"" % float(self.ppm))
        tec_rtd = float(self.data)
        #print ("%2.3f" % tec_rtd )
        #self.inst.write(":DISP:WIND2:TEXT:DATA \"  \"")

# -*- coding: utf-8 -*-
# $Id: devices/g9540.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
# xDevs.com Fluke 1529 Chub-E4 Thermometer module
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

class temp_meter():
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
        print "\033[8;5H \033[0;33mGPIB[\033[1m%2d\033[0;33m] : Guildline 9540\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxib_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        elif cfg.get('teckit', 'interface', 1) == 'visa':
            self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
            self.inst.timeout = 300000 # timeout delay in ms
        self.name = name
        self.tec_rtd = tec_rtd
        self.init_inst()
        
    def init_inst(self):
        # Setup ILX for YSI 44007
        #self.inst.write("*rst") #reset TEC controller
        time.sleep(0.1)
	#self.inst.write("*CLR")
        #Set temperature transducer to thermistor and 4-wire sense mode
        #self.inst.write("T 20") #enable temp #protection (default)

    def read_data(self,cmd):
        data_float = 0.0
        data_str = ""
        #self.inst.write(cmd)
        try:
            with Timeout(20):
                data_str = self.inst.read(15)
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float((data_str.split(" "))[1])
        except ValueError:
            print("\033[4;36H\033[31;1mException %s on read_data, ValueError = %s\n\033[39;1m" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        global tec_rtd
	#self.inst.clear()
        time.sleep(0.1)
        self.status_flag,data = self.read_data(" ")
        if (self.status_flag):
            self.data = data
        tec_rtd = float(data)
        return tec_rtd

    def get_data_status(self):
        return self.status_flag


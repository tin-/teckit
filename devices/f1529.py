# -*- coding: utf-8 -*-
# $Id: devices/f1529.py | Rev 54  | 2022/04/13 15:12:35 tin_fpga $
# xDevs.com Fluke 1529 Chub-E4 Thermometer module
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 3 | RPi3 
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

import six
if six.PY2:
    import ConfigParser as ConfigParser
    cfg = ConfigParser.ConfigParser()
else:
    import configparser
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';','#',))

cfg.read('teckit.conf')
cfg.sections()

if cfg.get('teckit', 'interface') == 'gpib':
    import Gpib
elif cfg.get('teckit', 'interface') == 'vxi':
    import vxi11
elif cfg.get('teckit', 'interface') == 'visa':
    import visa
    rm = visa.ResourceManager()
else:
    print ("No interface defined!")
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

class chub_meter():
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
        print ("\033[7;5H \033[0;33mGPIB[\033[1m%2d\033[0;33m] : Fluke 1529\033[0;39m" % self.gpib)
        if cfg.get('teckit', 'interface') == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface') == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'trm_ip'), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        elif cfg.get('teckit', 'interface') == 'visa':
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
        #self.inst.clear()
        time.sleep(0.1)
        self.status_flag,data = self.read_data("READ? 1")
        if (self.status_flag):
            self.data = data
        tec_rtd = float(data)
        return tec_rtd

    def get_data_channel(self, channel):
        global tec_rtd
        time.sleep(0.1)
        self.status_flag,data = self.read_data("READ? %d" % channel)
        if (self.status_flag):
            self.data = data
        tec_rtd = float(data)
        return tec_rtd

    def get_data_status(self):
        return self.status_flag


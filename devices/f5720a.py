# -*- coding: utf-8 -*-
# $Id: devices/f5720a.py | Rev 44  | 2020/02/13 19:28:25 tin_fpga $
# xDevs.com Fluke 8508A module
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

class hulk():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
        print "\033[4;5H \033[0;34mGPIB[\033[1m%2d\033[0;31m] : Fluke 5720A/HLK\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument('192.168.1.118', "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        self.reflevel = reflevel
        self.name = name
        self.init_inst()

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
	self.inst.write("*RST")
	self.inst.write("STBY")
	self.inst.write("EXTGUARD OFF")

    def init_inst_dummy(self):
        # Setup SCPI DMM
	time.sleep(0.1)

    def set_pt1000_rtd(self):
	self.inst.write(":sens:temp:tran rtd")      #select thermistor
	self.inst.write(":sens:temp:rtd:type user") #10 kOhm thermistor
	self.inst.write(":sens:temp:rtd:alph 0.00375") #10 kOhm thermistor
	self.inst.write(":sens:temp:rtd:beta 0.160") #10 kOhm thermistor
	self.inst.write(":sens:temp:rtd:delt 1.605") #10 kOhm thermistor
	self.inst.write(":sens:temp:rtd:rzer 1000") #10 kOhm thermistor
        self.inst.write(":SENS:FUNC 'TEMP'")
        self.inst.write(":SENS:TEMP:DIG 7")
        self.inst.write(":SENS:TEMP:NPLC 10")

    def mfc_out(self,cmd):
        # Setup SCPI DMM
	self.inst.write("OUT %s" % cmd)

    def mfc_oper(self):
        # Setup SCPI DMM
	self.inst.write("OPER")

    def mfc_stby(self):
        # Setup SCPI DMM
	self.inst.write("STBY")

    def mfc_cmd(self,cmd):
        # Setup SCPI DMM
	self.inst.write("%s" % cmd)

    def mfc_ext_sense(self, cmd):
        # Setup SCPI DMM
	self.inst.write("EXTSENSE %d" % cmd)

    def read_data(self,cmd):
        data_float = 0.0
        data_str = ""
        self.inst.write(cmd)
        try:
            with Timeout(300):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("\033[6;36HException %s on read_data(), ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("X?")
	#print self.data
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_data_status(self):
        return self.status_flag


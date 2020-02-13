# -*- coding: utf-8 -*-
# $Id: devices/hp3245a.py | Rev 44  | 2020/02/13 19:28:25 tin_fpga $
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

class usrc():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
	print "\033[5;5H \033[0;31mGPIB[\033[1m%2d\033[0;35m] : HP 3245A\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        self.reflevel = reflevel
        self.name = name
        self.init_inst_dummy()

    def init_inst_fres(self):
        # Setup SCPI DMM
        self.inst.clear()
	self.inst.write("*RST")
	self.inst.write("*CLR")
        self.inst.write(":SYST:AZER:TYPE SYNC")
        self.inst.write(":SYST:LSYN:STAT ON")
	self.inst.write(":SENS:FUNC 'FRES'")
	self.inst.write(":SENS:FRES:DIG 9;NPLC 20;AVER:COUN 10;TCON MOV")
	self.inst.write(":SENS:FRES:AVER:STAT ON")
	self.inst.write(":SENS:FRES:OCOM ON")
	self.inst.write(":SENS:FRES:RANG 20E3")
        self.inst.write(":FORM:ELEM READ")

    def init_inst_dummy(self):
        # Setup SCPI DMM
	self.inst.write("RST")
        self.inst.write("APPLY DCV 0")
	self.inst.write("IMP 0")
	self.inst.write("DCRES HIGH")
	time.sleep(0.1)

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
	self.inst.write("*RST")
	self.inst.write("*CLR")
        self.inst.write(":SYST:AZER:TYPE SYNC")
        self.inst.write(":SYST:LSYN:STAT ON")
        #self.inst.write(":SENS:TEMP:NPLC 10")
	self.inst.write(":SENS:FUNC 'VOLT:DC'")
	self.inst.write(":SENS:VOLT:DC:DIG 9;NPLC 20;AVER:COUN 10;TCON MOV")
	self.inst.write(":SENS:VOLT:DC:AVER:STAT ON")
	self.inst.write(":SENS:VOLT:DC:RANG 20")
        self.inst.write(":FORM:ELEM READ")
#        self.inst.write(":DISP:WIND:TEXT:DATA \"               \";STAT ON;")
#        self.inst.write(":DISP:WIND2:TEXT:DATA \"               \";STAT ON;")
#        #kei.write("READ?")

    def set_range(self,cmd):
	self.inst.write(":CURR:RANG:AUTO OFF")
	self.inst.write(":CURR:RANG %.5e" % float(cmd))

    def set_output_dci(self,cmd):
        # Setup SCPI DMM
	self.inst.write("APPLY DCI %.6e" % float(cmd))

    def out_en(self):
        # Setup SCPI DMM
	#self.inst.write("OUTP ON")
	time.sleep(0.01)

    def out_dis(self):
        # Setup SCPI DMM
	time.sleep(0.01)
	#self.inst.write("OUTP OFF")

    def set_dcv_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write(":SENS:FUNC 'VOLT:DC'")
	self.inst.write(":SENS:VOLT:DC:RANG %.2f" % cmd)

    def trigger(self):
	self.inst.write("READ?")

    def read_val(self):
        data_float = 0.0
        data_str = ""
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
            print("\033[6;36HException %s on read_data(), ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception


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
            print("\033[6;36HException %s on read_data(), ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_data_status(self):
        return self.status_flag


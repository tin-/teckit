# -*- coding: utf-8 -*-
# $Id: devices/k6430.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
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
elif cfg.get('teckit', 'interface', 1) == 'visa':
    import visa
    rm = visa.ResourceManager()
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

class smu_meter():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
	print "\033[8;5H \033[0;31mGPIB[\033[1m%2d\033[0;31m] : Keithley 6430\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxib_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        elif cfg.get('teckit', 'interface', 1) == 'visa':
            self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
            self.inst.timeout = 300000 # timeout delay in ms

        self.reflevel = reflevel
        self.name = name
        self.init_inst_dont()

    def init_inst_dont(self):
        # Setup SCPI DMM
	self.inst.write(":DISP:DIG 7")
        self.inst.clear()

    def init_inst_dummy(self):
        # Setup SCPI DMM
	self.inst.write("*RST")
	self.inst.write("*CLR")
        #self.inst.write(":FORM:ELEM READ")
	self.inst.write(":SENS:MED:RANK 1")
	self.inst.write(":SENS:MED:STAT ON")
	self.inst.write(":SYST:AZER:STAT ON")
	self.inst.write(":DISP:DIG 7")
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

    def out_en(self):
        # Setup SCPI DMM
	self.inst.write(":OUTP ON")

    def out_dis(self):
        # Setup SCPI DMM
	self.inst.write(":OUTP OFF")

    def set_dci_range(self,cmd,compl):
        # Setup SCPI SMU
	self.inst.write(":SOUR:FUNC CURR")
	self.inst.write(":SENS:CURR:NPLC 10")
	self.inst.write(":SOUR:CURR:PROT:LEV %.6e" % compl)
	self.inst.write(":SOUR:CURR:LEV %.6e" % cmd)

    def set_dci(self,cmd):
	self.inst.write(":SOUR:CURR:LEV %.6e" % cmd)

    def set_dcv(self,cmd):
	self.inst.write(":SOUR:VOLT:LEV %.6e" % cmd)

    def set_dcv_range(self,cmd,compl):
        # Setup SCPI DMM
	#self.inst.write(":CONF:VOLT'")
	self.inst.write(":SENS:VOLT:DC:NPLC 10")
	self.inst.write(":SENS:CURR:RANG %.6e" % compl)
	self.inst.write(":SENS:CURR:PROT %.6e" % compl)
	self.inst.write(":SENS:VOLT:DC:RANG %.6e" % cmd)

    def set_res_man_range(self,cmd,compl):
        # Setup SCPI DMM
	#self.inst.write(":CONF:RES'")
        self.inst.write(':SENS:FUNC "RES"') # Select ohms measurement function.
        self.inst.write(":SENS:RES:MODE MAN") # Select the manual ohms measurement method.
        self.inst.write(":SOUR:FUNC CURR") # Select voltage source function.
        self.inst.write(":SOUR:CURR:MODE AUTO") # Select fixed voltage sourcing mode.
        self.inst.write(":SOUR:CURR:RANG %.6e" % cmd)# Select 2V source range.
        self.inst.write(":SOUR:CURR:LEV %.6e" % cmd) # Set source level to 2V.
        self.inst.write(":SENS:VOLT:RANG:AUTO OFF")
        self.inst.write(":SENS:VOLT:PROT %.6e" % compl) # Set current compliance to 10mA.

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


    def read_raw_data(self,cmd):
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
        #try:
        #    data_float = float(data_str)
        #except ValueError:
        #    print("\033[6;36HException %s on read_data(), ValueError = %s\n" % (self.name,data_str))
        #    return (0,float(0)) # Exception on float conversion, 0 = error
        return (0,data_str) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_volt_data(self):
        self.status_flag,data = self.read_raw_data("READ?")
	self.volts = data.split(",")[0]
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return float(self.volts)

    def get_curr_data(self):
        self.status_flag,data = self.read_raw_data("READ?")
	self.curr = data.split(",")[1]
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return float(self.curr)

    def get_res_data(self):
        self.status_flag,data = self.read_raw_data("READ?")
	self.res = data.split(",")[2]
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return float(self.res)

    def get_data_status(self):
        return self.status_flag


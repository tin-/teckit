# -*- coding: utf-8 -*-
# $Id: devices/c61604.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
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

class source():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
        print "\033[2;5H \033[0;34mGPIB[\033[1m%2d\033[0;31m] : Chroma 61604\033[0;39m" % self.gpib
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
        self.init_inst_dummy()

    def init_inst_dummy(self):
        # Setup SCPI DMM
	time.sleep(0.1)

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
	self.inst.write("*RST")
	self.inst.write("*CLR")
        self.inst.write("TRG_SRCE EXT")
        #self.inst.write("GUARD EXT")

    def set_ohmf_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("OHMS %.4f,FOUR_WR" % cmd)
	self.inst.write("OHMS FILT_OFF,RESL8,FAST_OFF")
	self.inst.write("OHMS LOI_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG OFF")

    def set_dcv4w_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("DCV %.4f,FOUR_WR" % cmd)
	self.inst.write("DCV FILT_ON,RESL8,FAST_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG OFF")

    def set_dci_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("DCI %.4f" % cmd)
	self.inst.write("DCI FILT_OFF,RESL7,FAST_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG OFF")

    def set_dcv4w_range_avg16(self,cmd):
        # Setup SCPI DMM
	self.inst.write("DCV %.4f,FOUR_WR" % cmd)
	self.inst.write("DCV FILT_ON,RESL8,FAST_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG AV16")

    def set_ohmf_rel_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("OHMS %.4f,FOUR_WR" % cmd)
	self.inst.write("OHMS FILT_OFF,RESL8,FAST_OFF")
	self.inst.write("OHMS LOI_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG OFF")
	self.inst.write("DELAY 1")

    def set_tohmf_rel_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("TRUE_OHMS %.4f,FOUR_WR" % cmd)
	self.inst.write("TRUE_OHMS RESL8,FAST_OFF")
	self.inst.write("TRUE_OHMS LOI_OFF")
	self.inst.write("INPUT SUB_REAR")
	self.inst.write("AVG OFF")
	#self.inst.write("DELAY 2")

    def set_tohm_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("TRUE_OHMS %.4f" % cmd)
	self.inst.write("TRUE_OHMS RESL8,FAST_OFF")
	self.inst.write("TRUE_OHMS LOI_OFF")
	self.inst.write("INPUT FRONT")
	self.inst.write("AVG OFF")

    def set_tohm_rel_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("TRUE_OHMS %.4f" % cmd)
	self.inst.write("TRUE_OHMS RESL8,FAST_OFF")
	self.inst.write("TRUE_OHMS LOI_OFF")
	self.inst.write("INPUT SUB_REAR")
	self.inst.write("AVG OFF")
#	self.inst.write("DELAY 2")

    def set_ohm_range(self,cmd):
        # Setup SCPI DMM

	self.inst.write(":SENS:RES:DIG 9;NPLC 10;AVER:COUN 10;TCON MOV")
	self.inst.write(":SENS:RES:OCOM OFF")
	self.inst.write(":SENS:RES:RANG %.2f" % cmd)

    def set_dcv_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("DCV %.3f,FILT_OFF,RESL8,FAST_OFF" % cmd)

    def set_dcv_fast_range(self,cmd):
        # Setup SCPI DMM
	self.inst.write("DCV %.3f,FILT_ON,RESL7,FAST_ON" % cmd)

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

    def get_data(self,cmd):
        self.status_flag,data = self.read_data("FETC:SCAL:%s?" % cmd)
	#print self.data
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return float(self.data)

    def get_data_status(self):
        return self.status_flag


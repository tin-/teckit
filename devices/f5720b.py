# -*- coding: utf-8 -*-
# $Id: devices/f5720b.py | Rev 46  | 2021/09/24 20:26:29 tin_fpga $
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
import six
if six.PY2:
    import ConfigParser as configparser
    cfg = configparser.ConfigParser()
else:
    import configparser
    cfg = configparser.configparser(inline_comment_prefixes=(';','#',))

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
        print ("No MFC interface defined!")
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
        if cfg.get('teckit', 'if_debug') == 'false':
            if cfg.get('teckit', 'interface') == 'gpib':
                self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
            elif cfg.get('teckit', 'interface') == 'vxi':
                self.inst = vxi11.Instrument(cfg.get('teckit', 'mfcb_ip'), "gpib0,%d" % self.gpib) # VXI link
                self.inst.timeout = 180
            elif cfg.get('teckit', 'interface') == 'visa':
                self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
                self.inst.timeout = 300000 # timeout delay in ms
            print ("\033[0;135H \033[0;34mGPIB[\033[1m%2d\033[0;31m] : Fluke 5720A/HLK\033[0;39m" % self.gpib)
            self.reflevel = reflevel
            self.name = name
            self.init_inst()

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
        self.inst.write("*RST")
        self.inst.write("STBY")
        self.inst.write("EXTGUARD OFF") # use ON for 22mVAC 792AXFER
        print ("\033[5;80H\033[35;1mEXTGUARD OFF\033[39;0m")
	self.mfc_ext_sense(0)
        self.inst.write("RANGELCK OFF")

    def init_inst_dummy(self):
        # Setup SCPI DMM
        time.sleep(0.1)

    def xfer(self,cmd):
        # Setup SCPI DMM
        self.inst.write("XFER %s" % cmd)
        print ("\033[4;80H\033[43;1mXFER %s  \033[49;0m" % cmd)

    def mfc_out(self,cmd):
        # Setup SCPI DMM
        self.inst.write("OUT %s;*CLS" % cmd)
        print ("\033[3;80H\033[43;1m%s OUTPUT \033[49;0m" % cmd)
        
    def mfc_out_acv(self,cmd,freq):
        # Setup SCPI DMM
        self.inst.write("OUT %.7e V,%.5f Hz" % (float(cmd),float(freq)) )
        print ("\033[3;80H\033[43;1m%.5f, %.4f Hz OUTPUT \033[49;0m" % (float(cmd),float(freq)))

    def mfc_rangelock(self,cmd):
        # Setup SCPI DMM
        #self.inst.write("STBY")
        #self.inst.write("OUT %.7e V,%f Hz" % (cmd,freq) )
        #self.inst.write("RANGELCK %d" % mode)
        print("RANGELCK %s" % cmd)

    def mfc_oper(self):
        # Setup SCPI DMM
        self.inst.write("OPER;*CLS;OPER")
        print ("\033[2;80H\033[45;1mOPERATE \033[49;0m")
        
    def mfc_stby(self):
        # Setup SCPI DMM
        self.inst.write("STBY")
        print ("\033[2;80H\033[44;1mSTANDBY \033[49;0m")

    def mfc_cmd(self,cmd):
        # Setup SCPI DMM
        self.inst.write("%s" % cmd)

    def mfc_ext_sense(self, cmd):
        # Setup SCPI DMM
        self.inst.write("EXTSENSE %s" % cmd)
        print ("\033[6;80H\033[34;1mEXTSENSE %s \033[39;0m" % cmd)

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

    def get_uncert(self):
        self.inst.write("UNCERT?")
        self.data = self.inst.read()
        print self.data
        return self.data

    def get_data_status(self):
        return self.status_flag


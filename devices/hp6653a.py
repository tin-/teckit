# -*- coding: utf-8 -*-
# $Id: devices/hp6653a.py | Rev 46  | 2021/09/24 20:26:29 tin_fpga $
# xDevs.com HP 6653A PSU module
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 2.7 | RPi3
# Python 3.x | RPi3 
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
    print "No HW interface defined!"
    quit()

val2 = 0.0
cnt = 0
tread = 20
temp2 = 0
refhp = 7
reflevel = refhp
prev_t = 0
temp = 18
res_rtd = 0.3

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

class psu_src():
    temp = 38.5
    data = ""
    ppm = 0.0
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,refhp,name):
        self.gpib = gpib

        print "\033[5;5H \033[0;36mGPIB[\033[1m%2d\033[0;36m] : HP 6653A\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxib_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 30 # timeout delay in s
        elif cfg.get('teckit', 'interface', 1) == 'visa':
            self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
            self.inst.timeout = 300000 # timeout delay in ms
        self.refhp = refhp
        self.name = name
        self.init_inst()
        #self.init_inst()

    def init_inst(self):
        # Setup Guildline 9540
        #self.inst.clear()
        self.inst.write("OUTP OFF") #Setup thermometer display in degrees C
        self.inst.write("VOLT 0") #Setup thermometer display in degrees C
        self.inst.write("CURR 0") #Setup thermometer display in degrees C
        
    def trigger(self, cmd):
        self.inst.write("MEAS:%s" % cmd)

    def read_out(self):
        data_float = 0.0
        data_str = ""
        #print "\033[2;2H" 
        try:
            with Timeout(20):
                data_str = self.inst.read()
                #print data_v[2]
        except Timeout.Timeout:
            print ("\033[5;36HException by %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("\033[5;5H Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("\033[5;36HException by %s on read_data() ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception
    
    def set_vout(self,voltage):
	self.inst.write("VOLT %.3f" % float(voltage))

    def set_cout(self,curr):
	self.inst.write("CURR %.2f" % float(curr))

    def output_en(self):
	self.inst.write("OUTP ON")

    def output_dis(self):
	self.inst.write("OUTP OFF")

    def get_data(self):
        self.status_flag,data = self.read_out()
        if (self.status_flag):
            self.data = float(data)
        #    self.ppm = ((float(self.data) / self.refhp)-1)*1E6
        return self.data

    def get_data_status(self):
        return self.status_flag
# -*- coding: utf-8 -*-
# $Id: devices/g9540.py | Rev 44  | 2020/02/13 19:28:25 tin_fpga $
# xDevs.com Guildline 9540 Thermometer module
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

class dmm_meter():
    temp = 38.5
    data = ""
    ppm = 0.0
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,refhp,name):
        self.gpib = gpib

        print "\033[5;6H \033[0;36mGPIB[\033[1m%2d\033[0;36m] : Guildline 9540\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            if (refhp == 1):
                self.inst = vxi11.Instrument(cfg.get('teckit', 'vxib_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            else:
                self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
                self.inst.timeout = 2 # timeout delay in s
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
        self.inst.write("C") #Setup thermometer display in degrees C
        
    def trigger(self):
        self.inst.write("S")

    def read_temp(self):
        data_float = 0.0
        data_str = ""
        #print "\033[2;2H" 
        try:
            with Timeout(20):
                data_str = self.inst.read(15)
                data_v = data_str.split(" ")
                #print data_v[2]
        except Timeout.Timeout:
            print ("\033[5;36HException by %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("\033[5;5H Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_v[2])
        except ValueError:
            print("\033[5;36HException by %s on read_data() ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception
    
    def get_data(self):
        self.status_flag,data = self.read_temp()
        if (self.status_flag):
            self.data = float(data)
        #    self.ppm = ((float(self.data) / self.refhp)-1)*1E6
        return self.data

    def get_data_status(self):
        return self.status_flag
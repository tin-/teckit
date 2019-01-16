# -*- coding: utf-8 -*-
# $Id: devices/hp3458.py | Rev 42  | 2019/01/10 07:31:01 clu_wrk $
# xDevs.com HP 3458A module
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

	print "\033[5;5H \033[0;36mGPIB[\033[1m%2d\033[0;36m] : Keysight 3458A\033[0;39m" % self.gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        self.refhp = refhp
        self.name = name
        self.init_inst_fres()
        #self.init_inst()

    def init_inst(self):
        # Setup HP 3458A
        self.inst.clear()
        self.inst.write("PRESET NORM")
        self.inst.write("OFORMAT ASCII")
        self.inst.write("DCV 10")
        self.inst.write("TARM HOLD")
        self.inst.write("TRIG AUTO")
        self.inst.write("NPLC 100")
        self.inst.write("AZERO ON")
	self.inst.write("OCOMP OFF")
        self.inst.write("LFILTER ON")
        self.inst.write("NRDGS 1,AUTO")
        self.inst.write("MEM OFF")
        self.inst.write("END ALWAYS")
        self.inst.write("NDIG 9")
	self.inst.write("DELAY 0") # 2 second delay to mitigate OCOMP accuracy issue due DA
	#self.inst.write('DISP OFF,"              ,"')

    def init_inst_fres(self):
        # Setup HP 3458A
        self.inst.clear()
        self.inst.write("PRESET NORM")
        self.inst.write("OFORMAT ASCII")
        self.inst.write("OHMF 10E3")
        self.inst.write("TARM HOLD")
        self.inst.write("TRIG AUTO")
        self.inst.write("NPLC 50")
        self.inst.write("AZERO ON")
	self.inst.write("OCOMP OFF")
        self.inst.write("LFILTER ON")
        self.inst.write("NRDGS 1,AUTO")
        self.inst.write("MEM OFF")
        self.inst.write("END ALWAYS")
        self.inst.write("NDIG 9")
	self.inst.write("DELAY 0") # 2 second delay to mitigate OCOMP accuracy issue due DA
#	self.inst.write('DISP OFF,"              ."')

    def set_ohmf_range(self,cmd):
	self.inst.write("OHMF %g" % cmd)
	self.inst.write("OCOMP ON")
        self.inst.write("NPLC 100")
        self.inst.write("NDIG 8")
	self.inst.write("DELAY 0.05") # 2 second delay to mitigate OCOMP accuracy issue due DA

    def set_ohmf_fast_range(self,cmd):
	self.inst.write("OHMF %g" % cmd)
	self.inst.write("OCOMP ON")
        self.inst.write("NPLC 100")
        self.inst.write("NDIG 8")
	self.inst.write("DELAY 0") # 2 second delay to mitigate OCOMP accuracy issue due DA

    def set_ohm_range(self,cmd):
	self.inst.write("OHM %g" % cmd)
	self.inst.write("OCOMP OFF")
        self.inst.write("NPLC 100")
        self.inst.write("NDIG 8")
	self.inst.write("DELAY 0") # 2 second delay to mitigate OCOMP accuracy issue due DA

    def set_dcv_range(self,cmd):
	self.inst.write("DCV %g" % cmd)
        self.inst.write("NPLC 200")
        self.inst.write("NDIG 9")
        self.inst.write("DELAY 0")

    def set_dci_range(self,cmd):
        self.inst.write("NPLC 100")
        self.inst.write("NDIG 9")
        self.inst.write("DELAY 0")
	self.inst.write("DCI %g" % cmd)
        
    def trigger(self):
	self.inst.write("TARM SGL,1")

    def read_val(self):
        data_float = 0.0
        data_str = ""
	#print "\033[2;2H" 
        try:
            with Timeout(180):
                data_str = self.inst.read()
		#print data_str
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
    
    def read_data(self,cmd):
        data_float = 0.0
        data_str = ""
        self.inst.write(cmd)
        try:
            with Timeout(180):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("\033[5;36HException by %s on read_data() inst.read()\n" % self.name)
            return (0,float(0))
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
            data_float = float(data_str)
        except ValueError:
            print("\033[5;36HException by %s on read_data() ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_temp(self):
        self.inst.write("TARM SGL,1")
	self.temp_status_flag,temp = self.read_data("TEMP?")
        if (self.temp_status_flag):
            self.temp = temp
        return self.temp

    def get_temp_status(self):
        return self.temp_status_flag

    def get_data(self):
        self.status_flag,data = self.read_data("TARM SGL,1")
        if (self.status_flag):
            self.data = float(data)
        #    self.ppm = ((float(self.data) / self.refhp)-1)*1E6
        return self.data

    def get_data_status(self):
        return self.status_flag

    def acaldcv(self):
	self.inst.write("ACAL DCV")
	time.sleep(150)
	print ("ACAL DCV complete")

    def acalall(self):
	self.inst.write("ACAL ALL")
	time.sleep(850)
	print ("ACAL ALL complete")

    def print_ppm(self):
	self.data = self.data
        #self.inst.write("DISP ON, \"   \"")
	#self.inst.write("DISP OFF, \" \"")
	#self.inst.write("DISP OFF, \"%9.8f VREF \"" % float(self.data))

# -*- coding: utf-8 -*-
# $Id: devices/k182m.py | Rev 45  | 2021/01/25 07:14:53 tin_fpga $
# xDevs.com Keithley 182 nVmeter module
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
#from Adafruit_BME280 import *
#import k7168_client
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

class k182m_meter():
    temp = 38.5
    data = ""
    ppm = 0.0
    status_flag = 1
    temp_status_flag = 1
    global exttemp
    global rh
    global hectopascals
    global res_rtd

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
        if cfg.get('teckit', 'interface', 1) == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface', 1) == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'vxi_ip', 1), "gpib0,%d" % self.gpib) # VXI link
            self.inst.timeout = 180
        elif cfg.get('teckit', 'interface', 1) == 'visa':
            self.inst = rm.open_resource('GPIB::%d::INSTR' % self.gpib)
            self.inst.timeout = 300000 # timeout delay in ms

        self.reflevel = reflevel
        self.name = name
        self.init_inst()

    def init_inst(self):
        # Setup SCPI DMM
        #self.inst.clear()
        self.inst.write("B1X")     # 6.5 digit resolution
        self.inst.write("F0G0X")   # Latest A/D reading, reading without prefix
        self.inst.write("O0P0N0W0X") # Enabled analog filter, medium dig filter, disabled
        self.inst.write("R4X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V
        self.inst.write("S2X")     # NPLC 5
        self.inst.write("T4X")     # Trigger on X multiple

    def set_dcv_range(self, rng):
	if rng <= 0.0031:
	    self.inst.write("R1X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V
	if rng > 0.0031 and rng < 0.031:
	    self.inst.write("R2X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V
	if rng > 0.031 and rng < 0.31:
	    self.inst.write("R3X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V
	if rng > 0.31 and rng < 3.1:
	    self.inst.write("R4X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V
	if rng > 3.1:
	    self.inst.write("R5X")     # Range 30mV (2), 3mV - R1, R3 - 300mV, R4 = 3V

    def en_rel(self):
	ref = self.get_data()
	self.inst.write("Z1X")		# Enable last reading as relative
	ref = self.get_data()
	print ("K182 relative enabled , REF = %f" % ref)

    def dis_rel(self):
	self.inst.write("Z0X")		# Disable relative
	print ("K182 relative disabled")

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
            print("Exception thrown by dmm %s on read_data() - ValueError = %s\n" % (self.name,data_str))
            return (0,float(0)) # Exception on float conversion, 0 = error
        return (1,data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("X")
        time.sleep(0.1)
        self.status_flag,data = self.read_data("X")
        time.sleep(0.1)
        if (self.status_flag):
            self.data = data
        return self.data

    def get_data_status(self):
        return self.status_flag


# -*- coding: utf-8 -*-
# $Id: devices/mi6010.py | Rev 57  | 2022/04/14 15:09:38 tin_fpga $
# xDevs.com MI 6010B module
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
import numbers
import signal
import six
if six.PY2:
    import ConfigParser as ConfigParser
    cfg = ConfigParser.ConfigParser()
else:
    import configparser
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';','#',))

err_cnt = 0
    
cfg.read('teckit.conf')
cfg.sections()

if cfg.get('teckit', 'interface') == 'gpib':
    import Gpib
elif cfg.get('teckit', 'interface') == 'vxi':
    import vxi11
else:
    print ("No interface defined!")
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

class dcc_bridge():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
        print ("\033[8;5H \033[0;33mGPIB[\033[1m%2d\033[0;35m] : MIL 6010B\033[0;39m" % self.gpib)
        if cfg.get('teckit', 'interface') == 'gpib':
            self.inst = Gpib.Gpib(0, self.gpib, timeout = 180) # GPIB link
        elif cfg.get('teckit', 'interface') == 'vxi':
            self.inst = vxi11.Instrument(cfg.get('teckit', 'dcc_ip'), "gpib0,%d" % self.gpib) # VXI link
        #self.inst = vxi11.Instrument("192.168.1.2", "gpib0,15") # VXI link
            self.inst.timeout = 160
        self.reflevel = reflevel
        self.name = name
        self.init_inst()

    def init_inst_dummy(self):
        # Setup SCPI DMM
        time.sleep(0.1)

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
        #self.inst.write("A\r")
        #self.wait_ready()
        #self.check_read()
        #self.inst.write("R\r")
        #self.check_stby()
        #time.sleep(2)
        #self.check_stby()
        #time.sleep(2)
        #self.check_stby()
        #time.sleep(2)
        #self.check_stby()
        #time.sleep(2)

        #self.check_stby()
        self.read_rstb()
        #self.check_stby()
        self.inst.write("S\r")
        self.check_stby()
        #time.sleep(5)
        self.inst.write("Q\r")
        data_str = self.inst.read()
        #self.wait_ready()
#        self.inst.write("L\r")
        print ("\033[s\033[5;105H Init completed, S sent\033[u")

    def check_stby(self):
        self.inst.write("Q\r")
        data_stb = self.inst.read_stb()
        data_str = self.inst.read()
	print ("\033[s\033[6;105H Q"),
        print (data_str, data_stb)
        while (data_str[1] == "s"):
            print ("\033[s\033[7;105Hwaiting for standby to go ON")
            time.sleep(1)
            data_stb = self.inst.read_stb()
	    print ("\033[s\033[7;105H Q= "),
            print (data_str, data_stb)
            #data_stb = self.inst.read_stb()
            data_str = self.inst.read()
	    print ("\033[s\033[8;105H RD: "),
            print (data_str, data_stb)

    def check_read(self):
        data_stb = self.inst.read_stb()
        data_str = self.inst.read()
	print ("\033[s\033[9;105HDG "),
        print (data_str, data_stb)
        while (data_str[1] == "s"):
            data_stb = self.inst.read_stb()
            data_str = self.inst.read()
            print ("\033[s\033[10;105HDG "),
            print (data_str, data_stb)
            time.sleep(1)

    def read_rstb(self):
        data_stb = self.inst.read_stb()
	print ("\033[s\033[11;105HSTB "),
        print (data_stb)
        time.sleep(1)

    def wait_ready(self):
        datas = self.inst.read_stb()
        while (datas == 0):
            datas = self.inst.read_stb()
            time.sleep(0.5)

    def config_dcc(self,ix,rev_time,rx,rs,meas_cnt):
        # Setup SCPI DMM

        self.check_stby()
        self.inst.write("I%.3f\r" % float(ix))
        time.sleep(2)
        self.check_stby()

        self.inst.write("T%d\r" % rev_time)
        time.sleep(2)
        self.check_stby()

        self.inst.write("A%f\r" % float(rs))
        time.sleep(2)
        self.check_stby()

        self.inst.write("B%f\r" % float(rx))
        time.sleep(2)
        self.check_stby()

        self.inst.write("M%d\r" % meas_cnt)
        time.sleep(2)
        self.check_stby()

        print ("\033[s\033[3;105HConfiguration DCC : I%.3f T%d A%f B%f M%d" % (float(ix), rev_time, float(rs), float(rx), meas_cnt ) )

    def start_meas(self,stat_cnt):
        time.sleep(2)
        self.inst.write("J%d\r" % stat_cnt)
        time.sleep(2)
        self.check_stby()
        print ("\033[s\033[4;105HStart measurements stats J%d\033[u" % stat_cnt)

    def read_data(self,cmd):
        global err_cnt
        data_float = 0.0
        data_str = ""
        #data_stb = self.inst.read_stb()
        #print (data_stb)
        try:
            with Timeout(300):
                data_str = self.inst.read()
        except Timeout.Timeout:
            print ("Timeout exception from dmm %s on read_data() inst.read()\n" % self.name)
            return (0)
        #print ("Reading from dmm %s = %s" % (self.name,data_str))
        try:
             data_float = float(data_str[1:])
        except ValueError:
            print("\033[6;36H Exception %s on read_data(), ValueError = %s\n" % (self.name,data_str))
            print ("\033[s\033[%d;105H\033[32;1m ERR: " % (22+err_cnt)),
            print (data_str),
            print ("\033[u")
            err_cnt = err_cnt + 1
            if (err_cnt >= 40):
                err_cnt = 0
            return (0) # Exception on float conversion, 0 = error
        #print data_str
        return (data_float) # Good read, 1 = converted to float w/o exception

    def get_data(self):
        self.status_flag,data = self.read_data("X?")
        #print self.data
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_data_status(self):
        return self.status_flag

    def measure_init(self):
        #print ("\033[2J")
        #dcc = dcc_bridge(15, 0, "6010B")
        samples =  80000
        self.curr_rx_ma = float(cfg.get('testset', 'dcc_ix')) * 1e3
        self.res_rx = float(cfg.get('testset', 'dcc_rx'))
        self.res_rs = float(cfg.get('testset', 'dcc_rs'))
        self.dcc_delay = float(cfg.get('testset', 'dcc_settle_time'))
        self.config_dcc("%.2f" % self.curr_rx_ma, self.dcc_delay, self.res_rx, self.res_rs, samples) # mA, reversal_rate, rx, rs, samples
        self.start_meas(samples)
        value = self.read_data(" ")
        print ("\033[s\033[19;105HMeas started with DCC")

    def measure(self):
        self.wait_ready()
        value = self.read_data(" ")
        self.wait_ready()
        value = self.read_data(" ")
        print ("\033[s\033[36;1m\033[20;105H DCC READING:"),
        print (value),
        print ("\033[u\033[39;0m")
        return value

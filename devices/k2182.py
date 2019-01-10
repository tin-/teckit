# xDevs.com Python 10V test for 3458A
# http://xdevs.com/guide/ni_gpib_rpi/
import os.path
import sys
import Gpib
import time
import numbers
import signal

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

class scpi_meter():
    temp = 38.5
    data = ""
    status_flag = 1
    temp_status_flag = 1

    def __init__(self,gpib,reflevel,name):
        self.gpib = gpib
	print "\033[7;5H \033[0;31mGPIB[\033[1m%2d\033[0;31m] : Keithley 2182\033[0;39m" % self.gpib
        self.inst = Gpib.Gpib(0,self.gpib, timeout=60) # SCPI GPIB Address = self.gpib
        self.reflevel = reflevel
        self.name = name
        self.init_inst()

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
	self.inst.write(":SENS:FRES:OCOM OFF")
	self.inst.write(":SENS:FRES:RANG 20E3")
        self.inst.write(":FORM:ELEM READ")

    def init_inst_dummy(self):
        # Setup SCPI DMM
	time.sleep(0.1)

    def init_inst(self):
        # Setup SCPI DMM
        self.inst.clear()
	self.inst.write("*RST")
	self.inst.write("*CLR")
        self.inst.write(":SYST:FAZ:STAT ON")
        self.inst.write(":SYST:AZER:STAT ON")
        self.inst.write(":SYST:LSYN ON")
	self.inst.write(":CONF:VOLT")
	self.inst.write(":SENS:FUNC 'VOLT'")
	self.inst.write(":SENS:CHAN 1")
	self.inst.write(":SENS:VOLT:DC:NPLC 5")
	self.inst.write(":SENS:VOLT:CHAN1:RANG 10")
	self.inst.write(":SENS:VOLT:CHAN1:LPAS:STAT ON")
	self.inst.write(":SENS:VOLT:CHAN1:DFIL:STAT ON")
	self.inst.write(":SENS:VOLT:CHAN2:RANG 10")
	self.inst.write(":SENS:VOLT:CHAN2:LPAS:STAT ON")
	self.inst.write(":SENS:VOLT:CHAN2:DFIL:STAT ON")
        self.inst.write(":FORM:ELEM READ")
#        self.inst.write(":DISP:WIND:TEXT:DATA \"               \";STAT ON;")
#        self.inst.write(":DISP:WIND2:TEXT:DATA \"               \";STAT ON;")
#        #kei.write("READ?")

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

    def set_dcv_nrange(self,cmd,ch):
        # Setup SCPI DMM
	if (ch == 1):
	    self.inst.write(":SENS:VOLT:CHAN1:RANG %.2f" % cmd)
	if (ch == 2):
	    self.inst.write(":SENS:VOLT:CHAN2:RANG %.2f" % cmd)

    def get_data(self):
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_adata(self):
	self.inst.write(":SENS:FUNC 'VOLT'")
	self.inst.write(":SENS:CHAN 1;")
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_bdata(self):
	self.inst.write(":SENS:FUNC 'VOLT'")
	self.inst.write(":SENS:CHAN 2;")
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_temp(self):
	self.inst.write(":SENS:FUNC 'TEMP'")
	self.inst.write(":SENS:TEMP:TRAN INT")
	self.inst.write(":SENS:CHAN 0;")
        self.status_flag,data = self.read_data("READ?")
        if (self.status_flag):
            self.data = data#(data - 0.75) / 0.01 # Preamp A = 1000
        return self.data

    def get_data_status(self):
        return self.status_flag


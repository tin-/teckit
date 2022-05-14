# -*- coding: utf-8 -*-
# $Id: tools.py | Rev 58  | 2022/04/14 15:34:16 TiNw $
# xDevs.com TEC Experiment app tools pack
# Copyright (c) 2012-2019, xDevs.com
# 
# Python 2.7 | RPi3 
# Project maintainers:
#  o Ilya T.  (@)
# https://xdevs.com/guide/teckit
#
import os
import mmap
import sys
import time
from x256 import x256
import six
if six.PY2:
    import ConfigParser as configparser
    cfg = configparser.ConfigParser()
else:
    import configparser
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';','#',))
    
cfg.read('teckit.conf')
cfg.sections()

w, h = 8, 1000;
ch_data = [[0 for x in range(w)] for y in range(h)] 
ew, eh, ech = 3, 1000, 8;
env_data = [[[0 for x in range(ew)] for y in range(eh)] for z in range(ech)] 
dc, dh = 8, 1000;
tsp_data = [[0 for x in range(dc)] for y in range(dh)] 

def dormant(sec):
    """ Delay function to wait sec time and print user feedback on remaining time """
    sys.stdout.write("\033[7;50H")
    if (cfg.get('teckit', 'no_delays', 1) == 'true'):
        print (" "),
    else:
        print ("\033[33m\033[7;50H")
        for dorm in range (0,sec):
            time.sleep(1)
            sys.stdout.write('\033[7;%dH.' % ((dorm % 10) + 50))
            if ((dorm % 5) == 0):
                sys.stdout.write('\033[7;50H *********  %d sec to go    \r' % (sec - dorm) )
            sys.stdout.flush()
    sys.stdout.write('\033[7;50H                            \r')
    sys.stdout.flush()
    print ("\033[39m")

def create_local_file(fileName):
    """ Check if file exists, if not create it and add header """
    if (os.path.isfile(fileName) == False):
        with open(fileName, 'a') as o:
            #o.write("-i- %s;\n" % cfg.get('testset', 'testname', 1))
            #o.write("-i- %s;\n" % cfg.get('testset', 'testdut', 1))            
            #o.write("-i- %s;\n" % cfg.get('testset', 'testnotes', 1))
            o.write("date;val1;val2;val3;val4;val5;val6;val7;val8;temp1;temp2;temp3;temp4;amb_temp;amb_rh;amb_pressure;box_temp;nvm_temp;tec_curr;sv_temp;\n")
            print ("\033[2;40H-i- DataFile %s does not exist\r\n" % fileName) 
    else: 
        print ("\033[2;40H-i- Datafile %s exists\r\n" % fileName)

def create_nvs_local_file(fileName):
    """ Check if file exists, if not create it and add header """
    if (os.path.isfile(fileName) == False):
        with open(fileName, 'a') as o:
            #o.write("-i- %s;\n" % cfg.get('testset', 'testname', 1))
            #o.write("-i- %s;\n" % cfg.get('testset', 'testdut', 1))            
            #o.write("-i- %s;\n" % cfg.get('testset', 'testnotes', 1))
            o.write("date;val1;val2;val3;val4;val5;val6;val7;val8;vbl1;vbl2;vbl3;vbl4;vbl5;vbl6;vbl7;vbl8;vbsv;vcsv;vk4;vk6;temp1;temp2;temp3;temp4;amb_temp;amb_rh;amb_pressure;box_temp;dut_temp;tec_curr;sv_temp;\n")
            print ("\033[2;40H-i- DataFile %s does not exist\r\n" % fileName) 
    else: 
        print ("\033[2;40H-i- Datafile %s exists\r\n" % fileName)

def create_acv_test_file(fileName):
    """ Check if file exists, if not create it and add header """
    if (os.path.isfile(fileName) == False):
        with open(fileName, 'a') as o:
            #o.write("-i- %s;\n" % cfg.get('testset', 'testname', 1))
            #o.write("-i- %s;\n" % cfg.get('testset', 'testdut', 1))            
            #o.write("-i- %s;\n" % cfg.get('testset', 'testnotes', 1))
            o.write("date;mfc;volt;freq;detector;dcpos;dcneg;acvmeas;temp1;temp2;temp3;temp4;amb_temp;amb_rh;amb_pressure;box_temp;nvm_temp;tec_curr;sv_temp;\n")
            print ("\033[2;40H-i- DataFile %s does not exist\r\n" % fileName) 
    else: 
        print ("\033[2;40H-i- Datafile %s exists\r\n" % fileName)

# Plot ASCII UI stuff
def plot_ui():
    """ Draw pretty lines """
    print ("\033[1;1H╒\033[1;100H╕\033[35;1H╘\033[35;100H╛")
    for gi in range (2,100):
        print ("\033[1;%dH═" % (gi))
        print ("\033[3;%dH─" % (gi) )
        print ("\033[8;%dH═" % gi)
        print ("\033[29;%dH═" % gi)
        print ("\033[33;%dH═" % gi)
        print ("\033[35;%dH═" % gi)
    for gy in range (2,35):
        print ("\033[%d;1H│\033[%d;100H│" % (gy, gy))
    print ("\033[33;1H╞\033[8;1H╞\033[29;1H╞\033[3;1H├\033[3;100H┤\033[8;100H╡\033[33;100H╡\033[29;100H╡")
    print ("\033[41;66H│")
    print ("\033[42;100H\r\n")
    ix = x256.from_rgb(160, 130, 10)
    print ("\033[2;3H\x1b[38;5;" + str(ix) + "m xDevs.com TEC Experiment kit \033[0;49m")
    if cfg.get('teckit', 'interface') == 'gpib':
        print ("\033[2;29H USB-GPIB")
    elif cfg.get('teckit', 'interface') == 'vxi':
        print ("\033[2;29H LAN-VXI ")
    elif cfg.get('teckit', 'interface') == 'visa':
        print ("\033[2;29H NI VISA ")
    else:
        print ("No interface defined!")
        quit()

def print_val(idx, value, x, y):
    print ("\033[%d;%dH %s = %.9g   " % (y,x,idx,value))

if (cfg.get('testset', 'slope_shape') == 'lymex_step'):
    tec_status = ["Hold start","Ramp up 1 ","Dwell Pos ","Ramp up 2 ","Hold peak ","Ramp down1","Dwell Neg ","Ramp down2","Hold end  ","\033[41;1m !ALERT! ","\033[42;1m Job done"]
elif (cfg.get('testset', 'slope_shape') == 'xdevs_step'):
    tec_status = ["Hold start","Ramp up X ","Dwell Peak","Ramp base ","Hold base ","Ramp down ","Dwell Low ","Ramp base ","Base end X","\033[41;1m !ALERT! ","\033[42;1m Job done"]
dmm_status = ["Configure ","Sample ","ACAL DCV ","ACAL ALL ","TEMP?   ","\033[41;1m !ERROR! ","\033[42;1m Job done"]
dmm_mode = ["DCV", "OHM", "OHMF", "DCI", "ACV", "ACI"]
dmm_terminal = ["\033[0;44m  FRONT  ", "\033[0;45m  REAR   "]

#print "\033[30;5H \033[0;35mREF    A:%11.6G  B:%11.6G  C:%11.6G  D:%11.6G  E:%11.6G \033[0;39m" % (reference1, reference2, reference3, reference4, reference5)
#print "\033[36;0H"


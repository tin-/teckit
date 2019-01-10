![Status: Alpha](https://img.shields.io/badge/Status-alpha-red.svg) [![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/release/python-2715/) ![Build 40](https://img.shields.io/badge/Build-40-lightgrey.svg)

# xDevs.com TECKit app
VXI/GPIB Datalogger with oven control functionality for temperature coefficient or stability measurement experiments.

For latest information and updates:
https://xdevs.com/guide/teckit

GitHub repository:
https://github.com/tin-/teckit

## Introduction

xDevs.com TECKit Python open-source application is a flexible tool for controlling measurements instruments over GPIB or Ethernet.

It's main purpose is to perform controlled thermal chamber ramps and measure various DUT using external instrumentation. This is particulary well suited for voltage reference, ADC/DAC and electronic component stability and performance evaluation.

## Supported instrumentation

* Keithley 2001 precision DMM
* [Keithley 2002](https://xdevs.com/review/k2002) precision DMM
* [HP/Agilent/Keysight 3458A](https://xdevs.com/fix/hp3458a) reference DMM
* [Fluke 8508A](https://xdevs.com/review/f8508a) reference DMM
* [Keithley 2510](https://xdevs.com/fix/kei2510) TEC SMU for temperature chamber control
* ILX 5910B TEC controller for temperature chamber control
* [Adafruit BME280](https://xdevs.com/guide/bme280) temperature/humidity/pressure environment sensor

## Hardware requirements

* Raspberry Pi or similar SoC/FPGA board running Linux OS
* I2C access for BME280 sensor support
* Agilent E5810A for VXI11-GPIB gateway support, if VXI interface is used or,
* Agilent 82357B USB-GPIB interface dongle for linux-gpib or,
* NI USB-GPIB-HS interface dongle for linux-gpib

## Software requirements

* Python 2.7.x
* Installed and configured linux-gpib for GPIB interfacing
* Installed and configured python-vxi11 for VXI interfacing
* [NumPy](http://www.numpy.org/) - median/standard deviation analysis
* [x256 0.0.3](https://pypi.org/project/x256/) - RGB color conversion for UI styling
* [configparser](https://pypi.org/project/configparser/) - configuration file parser/manager

## Disclaimer

Code or any information posted here is provided **AS IS**. In no event shall the author or any other 3rd party, including xDevs.com project be liable for any special, direct, indirect, or consequential damages or any damages whatsoever resulting from loss of use, data or profits, whether in an action of contract, negligence or other tortuous action, arising out of or in connection with the use or performance of application, code or any relevant information published here.

While reasonable effort put into making this app useful, there are zero assurances that the software will ever work for any user or use case (even documented ones).
You must agree with the above to have any right to use the software.

## Usage 

Once all dependencies and environment setup is met, TECkit can be executed to collect measurement data.

### Step 1

Extract and configure settings file *teckit.conf* using text editor (see Configuration section below).

### Step 2

Include desired modules for needed instruments in **main.py**. Current release has enabled 5 instruments for measurement and 1 temperature controller:

```
if (cfg.get('mode', 'no_thermal', 1) == "false"):
    k2510  = imp.load_source('k2510' , 'devices/k2510.py')              # Load Keithley 2510 support
dmm1   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
dmm2   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
dmm3   = imp.load_source('k2002' , 'devices/k2002.py')                  # Load Keithley 2002 support
dmm4   = imp.load_source('k2002' , 'devices/k2002.py')                  # Load Keithley 2002 support
dmm5   = imp.load_source('hp3458', 'devices/hp3458.py')                 # Load Keysight 3458A support
```

### Step 4

Initialize and configure instrument-specific settings. To initialize link instance like *dmm1* to related module class *dmm_meter* with parameters (**GPIB Bus address**, 0, \"**Name for error tracking**\")

```
dmm1 = dmm1.dmm_meter (2,0,"3458B")  # GPIB 2
dmm2 = dmm2.dmm_meter (3,0,"3458A")  # GPIB 3
dmm3 = dmm3.scpi_meter(4,0,"2002-4") # GPIB 4
dmm4 = dmm4.scpi_meter(6,0,"2002-6") # GPIB 6
dmm5 = dmm5.dmm_meter (10,0,"3458D") # GPIB 10
```

Then use required mode/range setting function from DMM class, such as *set_ohmf_range* to configure meter in 4-wire resistance measurement mode, and select desired range. See specific function in devices/hp3458.py as example how that translates into GPIB command sent to the actual equipment.

```
dmm1.set_ohmf_range(1e3)                                                # 3458B function/range config
dmm2.set_ohmf_range(1e3)                                                # 3458A function/range config
dmm3.set_ohmf_range(200)                                                # K2002-4 function/range config
dmm4.set_ohmf_range(2000)                                               # K2002-6 function/range config
dmm5.set_ohmf_range(1e3)                                                # 3458D function/range config
```

Also make sure that each meter triggered and readout is saved into *meas_val[**N**]* variable. If some variables unused, in case when less than 6 instruments used, assign them to zero instead of removing, to preserve CSV output file formatting for future use. Code related to triggering and data collection from one meter:

```
dmm1.trigger()                         # Trigger DMM1
meas_val  = dmm1.read_val()[1]         # Collect measurement result
# Add results to array for stats math
sdev_arr1.extend([meas_val])           # Add new value into array for NumPy
```

### Step 5

Run application to perform the measurement sequence

    # python ./main.py

Upon completion application will exit to console automatically. It can be also aborted at any time via usual methods like Ctrl+C.
All data is saved after each sample, so even if you abort or kill the TECkit process, it will not cause loss of previously collected samples.
    
## Configuration

Flexibility of the app is managed thru configuration file **teckit.conf**, located in same directory as main.py app.
Some key settings:

```
env_sensor     = bme280         ; none for no sensor use, or bme280 for Bosch BME280 Environment sensor (I2C)
interface      = vxi            ; gpib for linux-gpib library to use with NI USB-GPIB-HS or **vxi** for python-vxi11 bidning for LAN-GPIB gateway
vxi_ip         = 192.168.1.125  ; IP address of LAN-GPIB gateway like Agilent E5810A. Not used if interface set to gpib
data_file      = tcr_res_k46_3458abd_sweep_test12_2019.csv ; This is filename to store all measurement samples.
```

Temperature ramp settings are available in **\[testset\]** section.

```
[testset]
sv_start            = 18.000  ; Chamber start temperature, in C
sv_end              = 18.000  ; Chamber end temperature, in C
peak_temp           = 50.000  ; <b>Top</b> soak temperature, in C
delay_start         = 0       ; Delay before any operation start, seconds
slope_pos           = 9000    ; Seconds for positive slope, seconds
slope_neg           = 9000    ; Seconds for negative slope, seconds
time_start          = 7200    ; Initial hold temperature time, before positive slope starts, seconds
time_hold           = 6000    ; Hold temperature duration time once reached peak_temp, seconds
time_end            = 3600    ; Hold temperature duration once ramp down finished, seconds
```

Setting **delay_start** to non-zero value could be useful to start TECkit experiment at later time when equipment will be available. 
Start and end chamber temperature configured by first two settings *sv_start* and *sv_end*. This is required to allow thermal equilibrium once DUT is placed in chamber and thermal control is turned on. The feedback loop of the thermal control is purely hardware based, depending on used controller, there is no software control in app, other than programming desired temperature set point.

![Ramp image](https://xdevs.com/doc/xDevs.com/teckit_ramp.png)

Each ramp sequence has five stages. Speed or duration of each stage configured in seconds, as shown on example listing above. It is recommended to keep hold start and peak_temp stages at least 30 minutes or more, to allow chamber reach thermal equilibrium, or the measurement data may have additional error due to unstable conditions. Ramp up and down stages can have different duration if needed. If these settings are set to very low value, like 2-5 seconds, sequence will be transformed into step response, which can be useful for PID/thermal chamber hardware tuning.

## Usage examples

### With temperature chamber control

After successful start, app will plot simple pseudo graphics text UI to provide means of monitoring experiment progress:

    ╒══════════════════════════════════════════════════════════════════════════════════════════════════╕
    │  xDevs.com TEC Experiment kit        -i- Datafile ../teckit/measure_example_jan2019.csv exists   │
    ├──────────────────────────────────────────────────────────────────────────────────────────────────┤
    │    GPIB[25] : Keithley 2510                                           Progress     : 11.96%      │
    │    GPIB[10] : Keysight 3458A                                          Total points : 4806        │
    │    GPIB[ 6] : Keithley 2002                                                                      │
    │    GPIB[17] : Fluke 1529                                                                         │
    ╞══════════════════════════════════════════════════════════════════════════════════════════════════╡
    │ Sample       :      575               Meter mode   : DCV              Set Temp     :  18.000 °C  │
    │ Next temp    : 18.000 °C              Measured val : 1000.01778900    Process Temp :  18.000 °C  │
    │ Min temp     : 18.000 °C              OCOMP/DELAY  : 1, 0 sec         TEC Current  :  -0.3706 A  │
    │ Peak temp    : 50.000 °C              Fixed range  : Configure        Status       :  Hold start │
    │ Remaining    :  8h 43m 14s            NPLC         :  100.0000        Gain         :  140.0000   │
    │ Elapsed time :  1h 11m 05s            Terminals    :   FRONT          Integral     :    0.1000   │
    │ Sample period: 7.42 sec               REL Value    :      1E-06       Derivative   :    0.9000   │
    │         Median A= 1000.017674000 V              Median K= 1000.010953000 V                       │
    │          Sdev A = 306.714 uV                     Sdev K = 370.634 uV                             │
    │ [   572] S18.000 P18.005 I-0.368  A1.000017904e+03 B1.000010179e+03 C5.000359900e+01 C           │
    │ [   573] S18.000 P17.995 I-0.367  A1.000017625e+03 B1.000011117e+03 C5.000361000e+01 C           │
    │ [   574] S18.000 P18.000 I-0.371  A1.000017789e+03 B1.000011065e+03 C5.000358600e+01 C           │
    │ [   553] S18.000 P18.001 I-0.367  A1.000017302e+03 B1.000011216e+03 C5.000349600e+01 C           │
    │ [   554] S18.000 P18.003 I-0.367  A1.000017566e+03 B1.000010758e+03 C5.000345400e+01 C           │
    │ [   555] S18.000 P17.998 I-0.368  A1.000018004e+03 B1.000010589e+03 C5.000347600e+01 C           │
    │ [   556] S18.000 P17.999 I-0.369  A1.000017153e+03 B1.000011302e+03 C5.000346300e+01 C           │
    │ [   557] S18.000 P18.001 I-0.369  A1.000017474e+03 B1.000010560e+03 C5.000346400e+01 C           │
    │ [   558] S18.000 P17.998 I-0.370  A1.000017124e+03 B1.000010968e+03 C5.000348600e+01 C           │
    │ [   559] S18.000 P17.999 I-0.369  A1.000017873e+03 B1.000010991e+03 C5.000348200e+01 C           │
    │ [   560] S18.000 P17.998 I-0.368  A1.000017390e+03 B1.000010767e+03 C5.000347500e+01 C           │
    ╞══════════════════════════════════════════════════════════════════════════════════════════════════╡
    │ Median A=    1.017674 V  B=    1.017674 V C=    1.017674 V D=    1.017674 V E=    1.017674 V     │
    │ Sdev   A=    1.017674 V  B=    1.017674 V C=    1.017674 V D=    1.017674 V E=    1.017674 V     │
    │ REF    A=                                                                                        │
    ╞══════════════════════════════════════════════════════════════════════════════════════════════════╡
    │    REF :       2000              Delta :-499991.106  ppm       │ 25.153°C  66.8%RH  1016.8 hPa   │
    ╘══════════════════════════════════════════════════════════════════════════════════════════════════╛ 

### Without temperature control, datalog only

TECKit can be used as simple data logger as well, without running temperature controller part. For this please next setting in *teckit.conf* configuration file:

    no_thermal     = true

When *no_thermal* is true, code related to the temperature controller hardware will not be executed, and only measurement instruments will be used for sampling. 
    
All measurement values like instrument readings, ambient temperature data, meter temperatures and TEC chamber telemetry are stored in CSV-alike text file.
This file have header to identify rows, such as:

    date;hp3458a;hp3458b;k6;k4;meas5;meas6;val6;temp1;temp2;amb_temp;amb_rh;amb_pressure;box_temp;nvm_temp;

## Example data, obtained from TECkit results

![Ramp image example](https://xdevs.com/doc/xDevs.com/teckit_example.png)
[CSV-data file from this run](https://xdevs.com/doc/xDevs.com/teckit_example_2019.csv)

Four measurement instruments used : HP 3458A GPIB 2 and 3, Keithley 2002 GPIB 4 and 6.
Temperature control done by Keithley 2510 GPIB 25 with 40W TEC module and Honeywell HEL-705 platinum RTD sensor.

## Adding own measurement instrumentation support

Have instrument not listed as supported? 
It is easy to add support of new instrument, following example of existing hardware modules in /devices directory.

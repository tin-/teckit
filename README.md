# TECKit app
VXI/GPIB Datalogger for temperature coeffient/stability measurement

For latest information and updates:
https://xdevs.com/guide/teckit

GitHub repository:
https://github.com/tin-/teckit

## Introduction

TECKit Python application is a flexible tool for controlling measurements instruments over GPIB or Ethernet.
It's main purpose of operation is to perform controlled thermal chamber ramps and measure DUT using external instrumentation.

## Supported instrumentation

* Keithley 2001 precision DMM
* Keithley 2002 precision DMM
* HP/Agilent/Keysight 3458A reference DMM
* Fluke 8508A reference DMM
* Keithley 2510 TEC SMU for temperature chamber control
* ILX 5910B TECcontroller for temperature chamber control
* Adafruit BME280 temperature/humidity/pressure environment sensor

## Hardware requirements

* Raspberry Pi or similar SoC/FPGA board running Linux OS
* I2C access for BME280 sensor support
* Agilent E5810A for VXI11-GPIB gateway support, if VXI interface used

## Software requirements

* Python 2.x
* Installed and configured linux-gpib for GPIB interfing
or 
* Installed and configured python-vxi11 for VXI interfacing
* NumPy 

## Installation

Step 1:

Extract and configure settings file *teckit.conf* using text editor

Step 2:

Run application to perform the measurement sequence

    # python ./main.py

## Usage examples

TBD
#! /usr/bim/python3
# _*_ coding=utf-8 _*_
# Code to log Arran Activity AWS
#
# Intergration period : 5s
# Brooks 05/03/2020

from datetime import datetime
from socket import gethostname
import serial
import os
import busio
import board
from time import sleep

import adafruit_mpl3115a2
import adafruit_sht31d

HOSTNAME=gethostname()

# Output path
data_root = '/home/pi'

# creat serial instance for gps on uart
ser = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout=3000)

#  create I2C instance for pressure and RH\T
i2c = busio.I2C(board.SCL, board.SDA)

# Create instance of Pressure sensor
PP_sen = adafruit_mpl3115a2.MPL3115A2(i2c)

# Create instance of Sht31D RH/T sensor
SHT_sen = adafruit_sht31d.SHT31D(i2c)

#create file
today = datetime.utcnow().strftime('%Y-%m-%d')
outfile = os.path.join(data_root, HOSTNAME + '-' + today + '.csv')
f = open(outfile,'a') # append to exisiting file or creae new one
f.close

count = 0

while True:
    data = ser.readline()
    data_string = ''.join([chr(b) for b in data])
    if data_string[0:6] == '$GPGGA': #get two of thes per second
        gps_msg1 = data_string

    if data_string[0:6] == '$GPRMC': #get one of these per second
        gps_msg2 = data_string
        count =count + 1

        #only initiate other measurents after receipt of 5 GPRMC messages
        if count > 4 :
            #reset counter
            count = 0

            # get pressure from mpl3115a2
            PP = "{0:0.2f}".format((PP_sen.pressure)/100)
            PP_T = "{0:0.1f}".format(PP_sen.temperature)
            # create message
            msg_mpl3115a2 = PP + "," + PP_T

            # get temperature and Humifidty from sht15
            SHT_RH = "{0:0f}".format(SHT_sen.relative_humidity)
            SHT_T = "{0:0.1f}".format(SHT_sen.temperature)
            # create message
            msg_sht31 = SHT_RH + "," + SHT_T + '\r\n'

            # create composite message
            msg = ','.join([gps_msg1[0:len(gps_msg1)-2], gps_msg2[0:len(gps_msg2)-2], msg_mpl3115a2, msg_sht31])
            print(msg)

            # save message - open-append-close
            f = open(outfile,'a')
            f.write(msg)
            f.flush()
            f.close()
    sleep(1)

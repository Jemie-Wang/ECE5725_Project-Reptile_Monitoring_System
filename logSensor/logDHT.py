#!/usr/bin/env python
#  Capture data from a DHT11 sensor and save it on a database

import time
import sqlite3
import board
import adafruit_dht
import RPi.GPIO as GPIO
import os

dbname='../sensorData.db'
sampleFreq = 10 # time in seconds
dhtDevice = adafruit_dht.DHT11(board.D6)

# get data from DHT sensor
def getDHTdata():	
	
	# Print the values to the serial port
	temp=None
	hum =None
	
	try:
		temp = dhtDevice.temperature
		hum = dhtDevice.humidity
		if hum is not None and temp is not None:
			hum = round(hum)
			temp = round(temp, 1)
			
		print(
		"Temp:  {:.1f} C    Humidity: {}% ".format(
		temp, hum
		)
		)
		
		if temp>25 or hum<5:
			os.system('python /home/pi/project/logSensor/textMessage/sensorText.py')
		
		
	except RuntimeError as error:
		# Errors happen fairly often, DHT's are hard to read, just keep going
		time.sleep(2.0)
	except Exception as error:
		dhtDevice.exit()
		raise error
	except OverflowError as error:
		print("meet error"+ str(error))
      
	return temp, hum

# log sensor data on database
def logData (temp, hum):
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	
	curs.execute("INSERT INTO DHT_data values(datetime('now','localtime'), (?), (?))", (temp, hum))
	conn.commit()
	conn.close()

# main function
def main():
	while True:
		temp, hum = getDHTdata()
		if temp is None or hum is None:
			#print("The DHT failed to work!!!!!!!!!")
			continue
		logData (temp, hum)
		time.sleep(sampleFreq)

# ------------ Execute program 
main()

GPIO.cleanup()



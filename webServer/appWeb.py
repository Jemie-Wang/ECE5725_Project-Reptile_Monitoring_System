#!/usr/bin/env python

'''
	RPi WEb Server for DHT and motion captured data with Gage and Graph plot  
'''
import cv2
from flask import Flask, render_template, Response


from datetime import datetime

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

import os

from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)

import threading
#from threading import Thread
import sqlite3
conn=sqlite3.connect('../sensorData.db', check_same_thread=False)
curs=conn.cursor()

#os.system('python ../logSensor/logDHT.py')
#os.system('python ../logSensor/logCAM.py')

# Define the lock globally
lock = threading.Lock()

def stream(camera_index):
    cam = cv2.VideoCapture(camera_index)
    while True:
        _, frame = cam.read()
        ret, jpg = cv2.imencode('.jpg', frame)
        jpg2bytes = jpg.tobytes()
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg2bytes + b'\r\n\r\n'

# Retrieve LAST data from database
def getLastData():
	try:
		lock.acquire(True)
		for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
			time1 = str(row[0])
			temp = row[1]
			hum = row[2]
	finally:
		lock.release()
	
	return time1, temp, hum

# Get 'x' samples of historical data
def getHistData (numSamples):
	dates1 = []
	temps = []
	hums = []
	
	dates2 = []
	move = []
	#for row in reversed(data1):
	try:
		lock.acquire(True)
		for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples)):
			dates1.append(row[0])
			temps.append(row[1])
			hums.append(row[2])
			#temps, hums = testeData(temps, hums)
		
		
		
		#for row in reversed(data2):
		for row in curs.execute("SELECT * FROM CAM_data ORDER BY timestamp DESC LIMIT "+str(numSamples)):
			dates2.append(row[0])
			move.append(row[1])
	finally:
		lock.release()
		
	return dates1, temps, hums, dates2, move

# Test data for cleanning possible "out of range" values
def testeData(temps, hums):
	n = len(temps)
	for i in range(0, n-1):
		if (temps[i] < -10 or temps[i] >50):
			temps[i] = temps[i-2]
		if (hums[i] < 0 or hums[i] >100):
			hums[i] = temps[i-2]
	return temps, hums


# Get Max number of rows (table size)
def maxRowsTable():
	for row in curs.execute("select COUNT(temp) from  DHT_data"):
		maxNumberRows=row[0]
	return maxNumberRows
	
# Get Max number of rows (table size)
def maxRowsTable1():
	for row in curs.execute("select COUNT(move) from  CAM_data"):
		maxNumberRows=row[0]
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	freq=1
	return (freq)

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
global numSamples1
numSamples1 = maxRowsTable1()

if (numSamples >6):
        numSamples = 5
        
if (numSamples1 > 6):
        numSamples1 = 5

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 5
				
		
# main route 
@app.route("/")
def index():
	time1, temp, hum = getLastData()
	templateData = {
	  'time1'		: time1,
	  'temp'		: temp,
	  'hum'			: hum,
	  'freq'		: freqSamples,
	  'rangeTime'		: rangeTime
	  }
	return render_template('index.html', **templateData)


@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    global freqSamples
    global rangeTime
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time1, temp, hum = getLastData()
    
    templateData = {
	'time1'		: time1,
	'temp'		: temp,
	'hum'			: hum,
	'freq'		: freqSamples,
	'rangeTime'	: rangeTime
	}
    return render_template('index.html', **templateData)
	

@app.route('/plot/temp')
def plot_temp():
	times1, temps, hums, times2, move = getHistData(numSamples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature [°C]")
	#axis.set_xlabel("Samples")
	fig.autofmt_xdate()
	axis.grid(True)
	xs = times1
	#xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/hum')
def plot_hum():
	times1, temps, hums, times2, move = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	#axis.set_xlabel("Samples")
	fig.autofmt_xdate()
	axis.grid(True)
	xs = times1
	#xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/move')
def plot_move():
	times1, temps, hums, times2, move = getHistData(numSamples)
	ys = move
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Number of movement")
	fig.autofmt_xdate()
	#axis.set_xlabel("Data get from ")
	axis.grid(True)
	#xs = range(numSamples)
	xs = times2
	
	axis.plot(xs, ys)
	#axis.invert_xaxis()
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response


@app.route('/stream_feed')
def stream_feed():
    return Response(stream(0), mimetype='multipart/x-mixed-replace; boundary=frame')
	
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)


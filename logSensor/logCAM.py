import time
import sqlite3
import cv2
import os
#give the system sometime to warm up
time.sleep(0.2)
# Read the video file / source
cap = cv2.VideoCapture(0)

dbname='../sensorData.db'


# Set the counter
#counter=0

sampleFreq = 5 # time in seconds

# get data from pi cam
def getCAMdata():
	starttime=time.time()
	counter =0
	while (time.time()-starttime<10):
		# Capture the 1st & 2nd frames and store them in resp. variables:	
		global ret1
		global frame1

		ret1, frame1 = cap.read()
		time.sleep(0.4)
		global rect2
		global frame2
		ret2, frame2 = cap.read()
		
		# Convert the frame1 & frame2 into gray scale to calculate differences:
		frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
		frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
		# Apply the Gaussian blur onto the gray scale frames
		# Kernel size is 21*21 which applies a stronger level of blurring:
		frame1_blur = cv2.GaussianBlur(frame1_gray, (21, 21), 0)
		frame2_blur = cv2.GaussianBlur(frame2_gray, (21, 21), 0)
		
		# Calculate the difference between the two frames:
		frames_diff = cv2.absdiff(frame1_blur, frame2_blur)
		
		# Background in black and motion in white
		threshold = cv2.threshold(frames_diff, 25, 255, cv2.THRESH_BINARY)[1]
		threshold = cv2.dilate(threshold,None)
		# Calculate the average of the frame:
		average_diff = threshold.mean()
		
		if average_diff:
			counter+=1
		
		# Repeat the same for the upcoming frames in the video:
		frame1 = frame2
		time.sleep(0.4)
		ret, frame2 = cap.read()
		''' ret:
			break
		k = cv2.waitKey(10)
		if k == ord('q'):
			break'''
	if counter > 10:
		os.system('python ./textMessage/camText.py')
		#cap1=cv2.VideoCapture(0)
		#reci,img = cap1.read()
		cv2.imwrite("../webServer/static/photo/output.jpg", frame2)		
	
	return counter

# log sensor data on database
def logData (move):
	
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	
	curs.execute("INSERT INTO CAM_data VALUES(datetime('now','localtime'), (?))", (move,))
	conn.commit()
	conn.close()

# main function
def main():
	while True:
		#move=0
		move = getCAMdata()
		print("in last 10 seconds, get movement of "+ str(move))
		logData (move)
		time.sleep(sampleFreq)

# ------------ Execute program 
main()


cv2.destroyAllWindows()

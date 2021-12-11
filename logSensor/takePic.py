#!/usr/bin/env python

import cv2
cap=cv2.VideoCapture(0)
reci,img = cap.read()
cv2.imwrite("output.jpg", img)

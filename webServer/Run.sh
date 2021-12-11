#!/bin/bash
python3 /home/pi/project/logSensor/logDHT.py &
python3 /home/pi/project/logSensor/logCAM.py &
python3 /home/pi/project/webServer/appWeb.py 

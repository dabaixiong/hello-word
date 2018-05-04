import subprocess
import os
import numpy as np

print "===================="
print "Author: Yun Long"
print "Date: 02/27/2018"
print "Affiliation: Micron Technology"
print "Copyright: ISCA zhong zhong zhong!"
print " "

print "==================="
print "Brief description"
print "This is a python script to display and save video from Jetson TX2 camera module"
print "Please refer to the README.txt in the same folder for more details and instructions"
print "Feel free to ask me questions or report bugs to yunlong@gatech.edu"
print " "

print "======== mode selection ==========="
print "1, mode for display only"
print "2, mode for save mp4 only"
print "3, mode for display and save simultaneously"
print "4, I just want to see a demo, 10 seconds video with 30 FPS, 640x480 size"
mode = raw_input("Please indicate what you want to do, type a number and press enter: ")
mode = int(mode)
if mode == 4:
    os.system("gst-launch-1.0 nvcamerasrc num-buffers=300 ! 'video/x-raw(memory:NVMM),width=640, height=480, framerate=30/1, format=I420' ! nvegltransform ! nveglglessink -e")
    exit()
print " "

print "======== video length ============"
duration = raw_input("Please indicate the lenght of video in second: ")
print " "

print "======== sample rate ============="
FPS = raw_input("Please type in the sample rate in FPS: ")
print " "

print "======== video size =============="
width = raw_input("Video width: ")
height = raw_input("Video height: ")
print " "

print "=================================="
print "If you want to re-type, just kill the process with 'ctrl+c'"
print " "

duration = int(duration)
FPS = int(FPS)
width = int(width)
height = int(height)

if mode == 1:
    str = "gst-launch-1.0 nvcamerasrc num-buffers={a} ! 'video/x-raw(memory:NVMM),width={b}, height={c}, framerate={d}/1, format=I420' ! nvegltransform ! nveglglessink -e".format(a=FPS*duration,b=width,c=height,d=FPS)
    os.system(str)
    exit()

if mode == 2:
    str = "gst-launch-1.0 nvcamerasrc num-buffers={a} sensor-id=0 ! 'video/x-raw(memory:NVMM),width={b}, height={c}, framerate={d}/1, format=NV12' ! omxh264enc ! qtmux ! filesink location=test.mp4 -ev".format(a=FPS*duration,b=width,c=height,d=FPS) 
    os.system(str)
    exit()

if mode == 3:
    str = "gst-launch-1.0 nvcamerasrc num-buffers={a} ! 'video/x-raw(memory:NVMM),width={b}, height={c}, framerate={d}/1, format=I420' ! tee name=t ! queue ! omxh264enc ! qtmux ! filesink location=test.mp4 -ev t. ! queue ! nvegltransform ! nveglglessink -e".format(a=FPS*duration,b=width,c=height,d=FPS)
    os.system(str)
    exit()

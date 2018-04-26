# -*- coding: utf-8 -*-
# import the necessary packages  
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np


# -*- coding: utf-8 -*-
##import os #for os.system("command")
# initialize the camera and grab a reference to the raw camera capture  
# s


class CV:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (208, 160)
        self.camera.framerate = 50
        self.rawCapture = PiRGBArray(self.camera, size=(208, 160))
        self.redLower = np.array([170, 100, 100])
        self.redUpper = np.array([179, 255, 255])

        # allow the camera to warmup
        time.sleep(2)

        # capture frames from the camera

    def find_light(self):
        for self.frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text

            imageC = self.frame.array

            ##imageC = cv2.imread("D:\\b.jpg")
            self.hsv = cv2.cvtColor(imageC, cv2.COLOR_BGR2HSV)

            self.mask = cv2.inRange(self.hsv, self.redLower, self.redUpper)

            self.res = cv2.bitwise_and(imageC, imageC, mask=self.mask)

            retval, fixed = cv2.threshold(res, 60, 255, cv2.THRESH_BINARY)  # binarize

            cnts = cv2.findContours(fixed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            cnts = cnts[0] if imutils.is_cv2() else cnts[1]

            i = 0
            for c in cnts:
                M = cv2.moments(c)
                cX = int(M["m10"] / (M["m00"] + 1))
                cY = int(M["m01"] / (M["m00"] + 1))
                print[cX, cY]

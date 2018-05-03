# -*- coding: utf-8 -*-
# import the necessary packages  
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
import numpy as np
import picamera
import threading
import sys
import GUI


class CV(threading.Thread):
    def __init__(self, gui):
        self.fps = 0
        self.args_dict['lower_red'] = np.array([5, 120, 50])
        self.args_dict['upper_red'] = np.array([20, 255, 255])

        self.args_dict['lower_red_1'] = np.array([170, 100, 100])
        self.args_dict['upper_red_1'] = np.array([180, 255, 255])
        self.flagLightFinded = 0
        self.cx = 128
        self.cy = 128
        self.gui = gui

    def showfps(self):
        print("fps:", self.fps)
        self.fps = 0
        self.timer = threading.Timer(1, self.showfps)
        self.timer.start()
        if self.gui.args_refresh_flag:  # 感觉有bug 会被另一个程序清掉flag
            self.read_argument()
            self.gui.args_refresh_flag = 0

    def read_argument(self):
        self.gui.save_args()
        self.args_dict['lower_red'] = np.array(eval(self.gui.argument_dict['lower_red']))
        self.args_dict['upper_red'] = np.array(eval(self.gui.argument_dict['upper_red']))
        self.args_dict['lower_red_1'] = np.array(eval(self.gui.argument_dict['lower_red_1']))
        self.args_dict['upper_red_1 '] = np.array(eval(self.gui.argument_dict['upper_red_1']))

    def run(self, result):
        '''输入一个参数result传递结果（cx, cy, flagLightFinded，cnt）,cnt=(cnt++)%1000，用cnt来判断结果是否有更新'''
        with picamera.PiCamera() as camera:
            camera.resolution = (240, 160)
            camera.framerate = 30
            camera.iso = 400
            camera.awb_mode = 'off'
            camera.awb_gains = 1.0
            camera.shutter_speed = 2000
            # camera.start_recording('test.h264')
            stream = PiRGBArray(camera, size=(240, 160))
            timer = threading.Timer(1, self.showfps)
            timer.start()
            inf = 666666666
            cnt = 0
            for frame in camera.capture_continuous(stream, format="bgr", use_video_port=True):

                src = frame.array
                # cv2.imshow('Capture',src)
                # cv2.imwrite('test.jpg',src)
                hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
                # grayscaled = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
                mask = cv2.inRange(hsv, self.args_dict['lower_red'], self.args_dict['upper_red'])
                # mask_2 = cv2.inRange(hsv, lower_red_1, upper_red_1)
                # mask = cv2.bitwise_or(mask_1,mask_2)
                # blur = cv2.GaussianBlur(imageG,(5,5),0)
                # retval,fixed=cv2.threshold(imageG,150,255,cv2.THRESH_BINARY)
                kernel = np.ones((15, 15), np.uint8)
                # mask = cv2.erode(mask,kernel)
                mask = cv2.dilate(mask, kernel, 1)

                # Find the Middle of the Light Blur
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                distance = [None] * len(cnts)
                i = 0
                for c in cnts:
                    M = cv2.moments(c)
                    cX = int(M["m10"] / (M["m00"] + 1))
                    cY = int(M["m01"] / (M["m00"] + 1))

                    if [cX, cY] != [0, 0]:
                        distance[i] = (cX - 104) * (cX - 104) + (160 - cY) * (160 - cY)
                    else:
                        distance[i] = inf
                        i = i + 1
                flagLightFinded = 0
                if distance != []:
                    M = cv2.moments(cnts[distance.index(min(distance))])
                    cx = round((M["m10"] / (M["m00"] + 1)) / 240.0 * 128)
                    cy = round((M["m01"] / (M["m00"] + 1)) / 160.0 * 128)
                    flagLightFinded = 1

                    cv2.rectangle(src, (cX - 40, cY - 30), (cX + 40, cY + 30), (0, 255, 0), 4)
                # str = "A%d,%d,%dFF " % (cx, cy, flagLightFinded);
                result = [cx, cy, flagLightFinded, cnt]
                cnt = (cnt + 1) % 1000
                # ser.write('A100,100,1FF ')
                # print(str)

                if self.gui.imshow_flag:
					cv2.imshow('Mask', mask)
					# cv2.imwrite('test_1.jpg',src);
					cv2.imshow('Image', src)

                self.fps = self.fps + 1
                stream.truncate(0)

                cv2.waitKey(1)

                
if __name__ == '__main__':
    gui=GUI.GUI()
    cv=CV(gui)
    cv.run([])

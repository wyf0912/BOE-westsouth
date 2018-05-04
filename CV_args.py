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
        self.args_dict={}
        self.args_dict['lower_red'] = np.array([5, 120, 50])
        self.args_dict['upper_red'] = np.array([20, 255, 255])

        self.args_dict['lower_red_1'] = np.array([170, 100, 100])
        self.args_dict['upper_red_1'] = np.array([180, 255, 255])
        self.flagLightFinded = 0
        self.cx = 128
        self.cy = 128
        self.gui = gui

    def showfps(self):
        #print("fps:", self.fps)
        self.fps = 0
        self.timer = threading.Timer(1, self.showfps)
        self.timer.start()
       # if self.gui.args_refresh_flag:  # 赂脨戮玫脫脨bug 禄谩卤禄脕铆脪禄赂枚鲁脤脨貌脟氓碌么flag
        #    self.read_argument()
         #   self.gui.args_refresh_flag = 0

    def read_argument(self):
        self.gui.save_args()
        self.args_dict['lower_red'] = np.array(eval(self.gui.argument_dict['lower_red']))
        self.args_dict['upper_red'] = np.array(eval(self.gui.argument_dict['upper_red']))
        self.args_dict['lower_red_1'] = np.array(eval(self.gui.argument_dict['lower_red_1']))
        self.args_dict['upper_red_1 '] = np.array(eval(self.gui.argument_dict['upper_red_1']))

    def run(self, result):
        '''脢盲脠毛脪禄赂枚虏脦脢媒result麓芦碌脻陆谩鹿没拢篓cx, cy, flagLightFinded拢卢cnt拢漏,cnt=(cnt++)%1000拢卢脫脙cnt脌麓脜脨露脧陆谩鹿没脢脟路帽脫脨赂眉脨脗'''
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

            '''*********************************'''
            awb_gains = True
            start_val = 0
            end_val = 0
            old_start_val = 0
            old_end_val = 0
            if awb_gains:
                current_val=0
                step = 0.01
                mode_str='awb_gains'
            else:
                current_val = 1000
                step = 10
                mode_str='shutter_speed'
            '''*********************************'''
            for frame in camera.capture_continuous(stream, format="bgr", use_video_port=True):

                '''*********************************'''
                current_val = current_val+ step
                if awb_gains:
                    camera.awb_gains = current_val
                else:
                    camera.shutter_speed = current_val
                '''*********************************'''
                cx, cy, flagLightFinded, cnt=[0,0,0,0]

                src = frame.array
                # cv2.imshow('Capture',src)
                # cv2.imwrite('test.jpg',src)WW
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

                cv2.imshow('Mask', mask)
                # cv2.imwrite('test_1.jpg',src);
                cv2.imshow('Image', src)
                self.fps = self.fps + 1
                stream.truncate(0)
                cv2.waitKey(1)

                '''*********************************'''
                if flagLightFinded and start_val == old_start_val:
                    start_val = current_val
                elif start_val != old_start_val and end_val == old_end_val and not flagLightFinded:
                    end_val = current_val
                    print(mode_str,'range from',start_val,'to',end_val)
                    sure = raw_input('input y to continue\n')
                    if sure == 'y':
                        old_end_val = end_val
                        old_start_val = start_val
                        current_val = old_start_val - step
                    else:
                        return 0
                '''*********************************'''




if __name__ == '__main__':
    gui = GUI.GUI()
    cv = CV(gui)
    cv.run([])

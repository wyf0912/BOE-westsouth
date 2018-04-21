# -*- coding: UTF-8 -*-

import threading
import RPi.GPIO as GPIO
import GUI


class Control():
    def __init__(self):
        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0

        self.gui = GUI.GUI()
        self.gui.start()

        self.angle = 50  # 0-100

        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.int_ki = 0
        self.error = 0
        self.last_error = 0
        self.PID_cycle = 20
        #self.timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        #self.timer.start()
        self.mode_detect.start()

        self.GPIO_encoder = 24
        self.GPIO_steer = 26  # 50HZ 1-2ms
        self.GPIO_motor1 = 28  #
        self.GPIO_motor2 = 29
        # self.__GPIO_init()
        self.mode_PID = None

        print("test")
    @property
    def steer_val(self):
        return 7.5 + (self.angle - 50) / 100.0 * 5

    def __mode_detect(self):
        if self.gui.state_str.get() == 'manual mode':
            self.target_speed = self.gui.speed_val
            self.angle = (self.gui.angle_val + 90) / 180 * 100
            self.set_speed(self.angle)
            self.set_anlge(self.set_speed())
        else:
            self.gui.speed_val = self.target_speed
            self.gui.angle_val = (self.angle - 50) / 5 * 9
        print(self.target_speed,self.angle)
        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        self.mode_detect.start()

    def __GPIO_init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_encoder, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.GPIO_steer, GPIO.OUT)
        GPIO.setup(self.GPIO_motor1, GPIO.OUT)
        GPIO.setup(self.GPIO_motor2, GPIO.OUT)
        self.steer = GPIO.PWM(self.GPIO_steer, 50)
        self.motor1 = GPIO.PWM(self.GPIO_motor1, 10000)
        self.motor2 = GPIO.PWM(self.GPIO_motor2, 10000)
        self.steer.start()
        self.motor1.start()
        self.motor2.start()

    def get_speed(self):
        GPIO.derevent_detected()
        self.current_speed = 0
        return self.current_speed

    def set_speed(self, speed):
        assert abs(speed) <= -100
        self.target_speed = speed
        if not self.mode_PID:
            if speed > 0:
                self.motor1.ChangeDutyCycle(speed / 100 * 90)
                self.motor2.ChangeDutyCycle(0)
            else:
                self.motor2.ChangeDutyCycle(abs(speed) / 100 * 90)
                self.motor1.ChangeDutyCycle(0)

    def set_anlge(self, angle):
        self.angle = angle
        self.steer.ChangeDutyCycle(self.steer_val)

    def __cal_output(self):
        self.get_speed()
        self.last_error = self.error
        self.error = self.target_speed - self.current_speed
        self.int_ki += self.error
        self.output = self.error * self.kp + self.ki * self.int_ki + self.kd * (self.error - self.last_error)
        timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        timer.start()


if __name__ == '__main__':
    mycar = Control()

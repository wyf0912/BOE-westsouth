# -*- coding: UTF-8 -*-

import threading
import RPi.GPIO as GPIO
import pigpio
import GUI
import CV
import sys
import re


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


# sys.stdout = Unbuffered(sys.stdout)
class Control():
    def __init__(self):

        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0

        self.gui = GUI.GUI()
        self.gui.start()

        self.args_dict = {}
        self.read_argument()

        self.angle = 50  # 0-100
        self.print_count = 0
        self.int_ki = 0
        self.error = 0
        self.last_error = 0
        self.PID_cycle = 20
        self.count = 0

        self.GPIO_encoder1 = 24
        self.GPIO_encoder2 = 23
        self.GPIO_steer = 12  # 50HZ 1-2ms 12 ,18,13,19
        self.GPIO_motor1 = 20  #
        self.GPIO_motor2 = 21
        self.__GPIO_init()

        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        # self.timer.start()
        self.mode_detect.start()

        self.mode_PID = True
        self.mode_CV = False
        if self.mode_CV:
            self.cv_result = []
            self.CV = CV(self.gui)
            self.CV.run(self.cv_result)

        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.PID_timer.start()
        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        self.mode_detect.start()

        print("test")

    def read_argument(self):
        self.gui.save_args()
        self.args_dict['kp'] = eval(self.gui.argument_dict['kp'])
        self.args_dict['ki'] = eval(self.gui.argument_dict['ki'])
        self.args_dict['kd'] = eval(self.gui.argument_dict['kd'])
        self.args_dict['servo_finetuning'] = eval(self.gui.argument_dict['servo_finetuning'])  # defaut 7.5

    @property
    def steer_val(self):
        return self.args_dict['servo_finetuning'] + (self.angle - 50) / 100.0 * 5

    def __mode_detect(self):
        if self.gui.state_str.get() == 'manual mode':
            self.target_speed = self.gui.speed_val
            self.angle = (self.gui.angle_val + 90) / 180 * 100
            self.set_speed(self.target_speed)
            self.set_anlge(self.angle)
        else:
            self.gui.speed_val = self.target_speed
            self.gui.angle_val = (self.angle - 50) / 5 * 9
        ##        print(self.target_speed,self.angle)
        if self.gui.args_refresh_flag:
            self.read_argument()
            self.gui.args_refresh_flag = 0

        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        self.mode_detect.start()

    def __GPIO_init(self):

        self.pi = pigpio.pi()
        #self.com = self.pi.serial_open("/dev/ttyAMA0", 115200)
        self.com = self.pi.bb_serial_read_open(18, 115200)
        #self.encoder_1 = self.pi.callback(self.GPIO_encoder1, pigpio.RISING_EDGE, self.encouder_count)
        #self.encoder_2 = self.pi.set_mode(self.GPIO_encoder2, pigpio.INPUT)
        self.pi.set_PWM_frequency(self.GPIO_steer, 50)
        self.pi.set_PWM_frequency(self.GPIO_motor1, 10000)
        self.pi.set_PWM_frequency(self.GPIO_motor2, 10000)
        self.pi.set_PWM_range(self.GPIO_steer, 10000)
        self.pi.set_PWM_dutycycle(self.GPIO_steer, 1000)
        self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
        self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

    '''
        def encouder_count(self, gpio, level, tick):
        # if self.pi.read(self.GPIO_encoder2):
        #    self.count+=1
        # else:
        #    self.count-=1
        self.count += 1
    '''

    def get_speed(self):
        #self.current_speed = self.count
        flag, message = self.pi.bb_serial_read(18)
        #print(message)
        try:
            data=message.decode('utf-8')
            #print(data)
            result=re.findall('A.*?B',data)
            print(result)
            if result:
                self.current_speed=eval(result[-1][1:-1])
            #print(data)
        except:
            pass
        self.print_count += 1
        if self.print_count % 4 == 0:
           print(self.current_speed/100)

        return self.current_speed

    def set_speed(self, speed):
        assert abs(speed) <= 100
        self.target_speed = speed*100
        if not self.mode_PID:
            if speed > 0:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, int(speed * 255.0 / 100.0 * 0.9))
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

            else:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, int(-speed * 255.0 / 100.0 * 0.9))
        else:
            print(self.output)
            if self.output > 0:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, int(self.output * 255.0 / 100.0 * 0.9))
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

            else:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, int(-self.output * 255.0 / 100.0))
                                                                
    def set_anlge(self, angle):
        self.angle = angle
        self.pi.set_PWM_dutycycle(self.GPIO_steer, self.steer_val * 100)

    ##        self.steer.ChangeDutyCycle(self.steer_val)

    def __cal_output(self):
        self.get_speed()
        self.last_error = self.error
        self.error = self.target_speed - self.current_speed
        self.int_ki += self.error
        self.output = self.error * self.args_dict['kp'] + self.args_dict['ki'] * self.int_ki + self.args_dict['kd'] * (
                self.error - self.last_error)
        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.PID_timer.start()



if __name__ == '__main__':
    mycar = Control()

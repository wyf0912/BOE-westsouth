# -*- coding: UTF-8 -*-

import threading
import RPi.GPIO as GPIO
import pigpio
import GUI
import CV
import sys
import re

gui = GUI.GUI()
gui.start()


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


quq = 0

class FindLight:
    def __init__(self):
        self.success_flag = 0 #值为0代表没有成功灭灯，值为1代表已经进入灯比较近的的范围
        self.count = 0
        #gui.argument_dict['backtime']=0


    def cal(self, cv_result):
        cx, cy, light_find, cnt = cv_result
        #print('test',cv_result)
        speed = 0
        angle = 0

        if not light_find:
            speed, angle = self.not_found()
        else:
            if cy < 20:
                speed = 20
                angle = 50 - (cx-64)/128.0*100

            elif cy >= 20: # and cy>10
                speed = 5
                self.success_flag = 1
                angle = 50 - (cx-64)/128.0*100
        print 'output',cx,cy
        return speed,int(angle)


    def not_found(self):
        if self.success_flag == 1:
            speed = -5
            angle = 50 # 或 100
            self.count += 1
            if self.count>140:
                self.count = 0
                self.success_flag = 0
        else:
            speed = 5
            angle = 0 #或100

        return speed, angle

    def read_argument(self):
        gui.save_args()
        print('test')
        self.args_dict['time'] = eval(gui.argument_dict['kp'])







# sys.stdout = Unbuffered(sys.stdout)
class Control:
    def __init__(self, control_logic):

        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0
        self.max_val=100
        self.transed_speed=0
        self.clear_i_flag = 0
        
        self.logic = control_logic
		
        self.args_dict = {}
        self.read_argument()

        self.angle = 50  # 0-100
        self.print_count = 0
        self.int_ki = 0
        self.error = 0
        self.last_error = 0
        self.PID_cycle = 10
        self.count = 0
        self.__flag_i=1

        self.GPIO_encoder1 = 24
        self.GPIO_encoder2 = 23
        self.GPIO_steer = 12  # 50HZ 1-2ms 12 ,18,13,19
        self.GPIO_motor1 = 20  #
        self.GPIO_motor2 = 21
        self.__GPIO_init()

        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.mode_detect = threading.Timer(self.PID_cycle / 100.0, self.__mode_detect)
        # self.timer.start()
        self.mode_detect.start()
        self.PID_timer.start()

        self.mode_PID = True
        self.mode_CV = True
        if self.mode_CV:
            self.cv_result = [0,0,0,0]
            self.cv = CV.CV(gui)
            self.cv.run(self.cv_result)

        
        
        self.clear_i_flag = 1 #use to break

        print("test")

    def read_argument(self):
        gui.save_args()
        print('test')
        self.args_dict['kp'] = eval(gui.argument_dict['kp'])
        self.args_dict['ki'] = eval(gui.argument_dict['ki'])
        self.args_dict['kd'] = eval(gui.argument_dict['kd'])
        self.args_dict['servo_finetuning'] = eval(gui.argument_dict['servo_finetuning'])  # defaut 7.5

    @property
    def steer_val(self):
        return self.args_dict['servo_finetuning'] + (self.angle - 50) / 100.0 * 5

    def __find_light(self):
        target_speed,target_angle=self.logic.cal(self.cv.result)
        self.target_speed = target_speed
        self.target_anlge = target_angle
        self.set_speed(target_speed)
        self.set_anlge(target_angle)
        gui.speed_str.set('速度：' + str(target_speed))
        gui.angle_str.set('角度：' + str(target_angle))

		


    def __mode_detect(self):
        if gui.state_str.get() == 'manual mode':
            self.target_speed = gui.speed_val
            self.angle = (gui.angle_val + 90) / 180.0 * 100
            self.set_speed(self.target_speed)
            self.set_anlge(self.angle)
        else:
            if self.mode_CV:
                self.__find_light()
            gui.speed_val = self.target_speed
            gui.angle_val = (self.angle - 50) / 5 * 9

        ##        print(self.target_speed,self.angle)
        if gui.args_refresh_flag:
            self.read_argument()
            gui.args_refresh_flag = 0
		
        gui.updata_speed(self.current_speed/400.0)
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
            result_check=re.findall('B.*?C',data)

            #print(result,result_check)
            if result[-1][1:-1] != result_check[-1][1:-1]:
                check_1=result=re.findall('C.*?D',data)
                check_2=result_check=re.findall('D.*?E',data)
                if check_1[-1][1:-1] != check_2[-1][1:-1]:
                    gui.updata_speed('trans error')
                elif check_1:
                    self.current_speed=-eval(check_1[-1][1:-1])
            elif result:
                self.current_speed=-eval(result[-1][1:-1])
            #print(data)
        except:
            pass
        self.print_count += 1
        #if self.print_count % 4 == 0:
        #   print('current speed:',self.current_speed/400.0)
        #gui.save_args()

        
		
        return self.current_speed

    def set_speed(self, speed):
        assert abs(speed) <= 100
        self.transed_speed = speed*400
        if speed==0:
            if self.__flag_i:
                self.__flag_i=0
                self.int_ki=0
        else:
            self.__flag_i=1
        #self.int_ki=0
        if not self.mode_PID:
            if speed > 0:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, int(speed * 255.0 / 100.0 * 0.9))
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

            else:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, int(-speed * 255.0 / 100.0 * 0.9))
        else:
            #print(self.output)

            self.output_copy=self.output
            if self.output_copy>self.max_val:
                self.output_copy=self.max_val
            if self.output_copy<-self.max_val:
                self.output_copy=-self.max_val
            val = int(self.output_copy * 255.0 / 100.0 * 0.9)
            #print('set val:',val)
            if val > 0:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, val)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

            else:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, -val)
                                                                
    def set_anlge(self, angle):
        if angle>100:
            angle=100
        elif angle<0:
            angle=0
        self.angle = angle
        self.pi.set_PWM_dutycycle(self.GPIO_steer, self.steer_val * 100)

    ##        self.steer.ChangeDutyCycle(self.steer_val)
    
    def judge_i(self):
        
        if self.target_speed>0:
            self.clear_i_flag=1
        elif self.target_speed<0:
            self.clear_i_flag=-1
        elif self.target_speed==0:
            #print('xxx',current_speed,self_i_flag)
            if self.current_speed*self.clear_i_flag<=0:
                print('qingling')
                self.int_ki_val=0
                self.int_ki=0
        
    def __cal_output(self):
        self.get_speed()
        self.last_error = self.error
        self.error = self.transed_speed - self.current_speed
        
        self.int_ki += self.error
        self.int_ki_val = self.args_dict['ki'] * self.int_ki
        if self.int_ki_val > self.max_val*0.4:
            self.int_ki_val = self.max_val*0.4
        if self.int_ki_val < -self.max_val*0.4:
            self.int_ki_val = -self.max_val*0.4
        self.judge_i() #
        self.output = self.error * self.args_dict['kp'] + self.int_ki_val + self.args_dict['kd'] * (
                self.error - self.last_error)
        #print(self.int_ki)
        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.PID_timer.start()



if __name__ == '__main__':
    mycar = Control(FindLight())

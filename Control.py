# -*- coding: UTF-8 -*-

import threading
import RPi.GPIO as GPIO
import pigpio
import GUI


class Control():
    def __init__(self):
        self.read_argument()

        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0

        self.gui = GUI.GUI()
        self.gui.start()

        self.angle = 50  # 0-100

        self.args_dict = {}
        self.int_ki = 0
        self.error = 0
        self.last_error = 0
        self.PID_cycle = 20
        self.PID_timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.mode_detect = threading.Timer(self.PID_cycle / 1000.0, self.__mode_detect)
        # self.timer.start()
        self.mode_detect.start()

        self.GPIO_encoder1 = 23
        self.GPIO_encoder2 = 24
        self.GPIO_steer = 12  # 50HZ 1-2ms 12 ,18,13,19
        self.GPIO_motor1 = 20  #
        self.GPIO_motor2 = 21
        self.__GPIO_init()
        self.mode_PID = False

        print("test")

    def read_argument(self):
        self.args_dict['kp'] = self.gui.argument_dict['kp']
        self.args_dict['ki'] = self.gui.argument_dict['ki']
        self.args_dict['kd'] = self.gui.argument_dict['kd']
        self.args_dict['servo_finetuning'] = self.gui.argument_dict['servo_finetuning'] #defaut 7.5

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
        ##        GPIO.setwarnings(False)
        ##        GPIO.setmode(GPIO.BCM)
        ##        GPIO.setup(self.GPIO_encoder, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        ##        GPIO.setup(self.GPIO_steer, GPIO.OUT)
        ##        GPIO.setup(self.GPIO_motor1, GPIO.OUT)
        ##        GPIO.setup(self.GPIO_motor2, GPIO.OUT)
        ##        self.steer=PWM.Servo()
        ##        self.steer = GPIO.PWM(self.GPIO_steer, 50)
        ##        self.steer.set_servo(self.GPIO_steer,1500)
        ##        self.motor1 = GPIO.PWM(self.GPIO_motor1, 10000)
        ##        self.motor2 = GPIO.PWM(self.GPIO_motor2, 10000)
        ##        self.steer.start(self.steer_val)
        ##        self.motor1.start(0)
        ##        self.motor2.start(0)
        self.encoder_1 = self.pi.callback(self.GPIO_encoder1, pigpio.EITHER_EDGE)

        self.pi = pigpio.pi()
        self.pi.set_PWM_frequency(self.GPIO_steer, 50)
        self.pi.set_PWM_frequency(self.GPIO_motor1, 10000)
        self.pi.set_PWM_frequency(self.GPIO_motor2, 10000)
        self.pi.set_PWM_range(self.GPIO_steer, 10000)
        self.pi.set_PWM_dutycycle(self.GPIO_steer, 1000)
        self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
        self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

    def get_speed(self):
        print(self.encoder_1.tally())
        self.encoder_1.reset_tally()
        self.current_speed = 0
        return self.current_speed

    def set_speed(self, speed):
        assert abs(speed) <= 100
        self.target_speed = speed
        if not self.mode_PID:
            if speed > 0:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, int(speed * 255.0 / 100.0 * 0.9))
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, 0)

            else:
                self.pi.set_PWM_dutycycle(self.GPIO_motor1, 0)
                self.pi.set_PWM_dutycycle(self.GPIO_motor2, int(-speed * 255.0 / 100.0 * 0.9))

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
        self.Pid_timer.start()


if __name__ == '__main__':
    mycar = Control()

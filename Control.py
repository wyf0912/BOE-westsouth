import threading
import RPi.GPIO as GPIO


class Control():
    def __init__(self):
        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0

        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.int_ki = 0
        self.error = 0
        self.last_error = 0
        self.PID_cycle = 20
        self.timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        self.timer.start()

        self.GPIO_encoder = 24
        self.GPIO_init()

    def GPIO_init(self):
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.GPIO_encoder, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def get_speed(self):
        GPIO.derevent_detected()
        self.current_speed = 0
        return self.current_speed

    def set_speed(self, speed):
        self.target_speed = speed

    def __cal_output(self):
        self.get_speed()
        self.last_error = self.error
        self.error = self.target_speed - self.current_speed
        self.int_ki += self.error
        self.output = self.error * self.kp + self.ki * self.int_ki + self.kd * (self.error - self.last_error)
        timer = threading.Timer(self.PID_cycle / 1000.0, self.__cal_output)
        timer.start()
        print(self.output)

    def PWM(self):
        pass


if __name__ == '__main__':
    mycar = Control()

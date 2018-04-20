import threading
import RPi.GPIO as GPIO


class Control():
    def __init__(self):
        self.current_speed = 0
        self.target_speed = 0
        self.output = 0
        self.__encoder_count = 0

        self.angle = 50  # ����Ƕ� 0-100 50Ϊ�м�λ��

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
        self.GPIO_steer = 26  # 50HZ 1-2ms
        self.GPIO_motor1 = 28  #
        self.GPIO_motor2 = 29
        self.__GPIO_init()

        self.mode_PID = None

    @property
    def steer_val(self):
        return 7.5 + (self.angle - 50) / 100.0 * 5

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
                self.motor1.ChangeFrequency(speed / 100 * 90)
                self.motor2.ChangeFrequency(0)
            else:
                self.motor2.ChangeFrequency(abs(speed) / 100 * 90)
                self.motor1.ChangeFrequency(0)

    def set_anlge(self, angle):
        self.angle = angle
        self.steer.ChangeFrequency(self.steer_val)

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

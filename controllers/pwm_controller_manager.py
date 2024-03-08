from enum import Enum
import RPi.GPIO as GPIO

class StateValues(Enum):
    ON = "ON"
    OFF = "OFF"
    
class PWMController:
    def __init__(self, pin, freq=1500, percentage=50):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        # GPIO.output(self.pin, GPIO.LOW)
        self.duty_range = 100  # Assuming a range of 0-100 for duty cycle
        self.duty = int(percentage / 100 * self.duty_range)
        self.percentage = percentage
        self.pwm = GPIO.PWM(self.pin, freq)  # Frequency set to 1500 Hz
        self.pwm.start(self.duty)  # Start with 0% duty cycle (LED off)

    def set_level(self, percentage):
        if 0 <= percentage <= 100:
            self.percentage = percentage
            self.duty = int(self.percentage / 100 * self.duty_range)
            self.pwm.ChangeDutyCycle(self.duty)
        else:
            if percentage < 0:
                self.percentage = 0
            else:
                self.percentage = 100

            self.duty = int(self.percentage / 100 * self.duty_range)
            self.pwm.ChangeDutyCycle(self.duty)

    def turn_on(self):
        self.duty = int(self.percentage / 100 * self.duty_range)
        self.pwm.ChangeDutyCycle(self.duty)
        # self.set_level(percentage=100)

    def turn_off(self):
        self.duty = int(0 / 100 * self.duty_range)
        self.pwm.ChangeDutyCycle(self.duty)

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

    def get_level(self):
        return self.percentage

    def get_state(self):
        return StateValues.OFF.value if self.duty == 0  else StateValues.OFF.value
    
    def flip_state(self):
        if self.get_state() == StateValues.OFF.value :
            self.set_state(StateValues.ON.value)
        elif self.get_state() == StateValues.ON.value:
            self.set_state(StateValues.OFF.value)

    def get_state(self):
        return StateValues.OFF.value if self.duty == 0  else StateValues.ON.value 
    
    def set_state(self, state_str:str):
        if state_str == StateValues.OFF.value:
            self.turn_off()
        elif state_str == StateValues.ON.value:
            self.percentage = 100 if self.duty == 0  else self.duty
            self.turn_on()
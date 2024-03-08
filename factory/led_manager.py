from datetime import datetime, timedelta
import threading
import time
from controllers.pwm_controller_manager import PWMController

from helpers.threads_exit_flag import get_exit_flag



class LEDCommand:
    def __init__(self, state:str, time_diff:int = 4):
        self.state = state
        self.end_time = ""
        self.set_end_time(time_diff)

    def set_end_time(self, time_diff:int = 4):
        time_to_end = datetime.now() + timedelta(seconds=time_diff)
        self.end_time = time_to_end.strftime("%Y-%m-%d %H:%M:%S")

class LEDDevice:
    def __init__(self, name:str, pin:int, default_state:str = "OFF", command:LEDCommand = None):
        self.name = name
        self.pin = pin
        self.default_state = default_state
        if command == None:
            self.command = LEDCommand(default_state, 0)
        else:
            self.command = command

    def set_command(self, command:LEDCommand = None):
        self.command = command

    def get_command(self):
        return self.command

class LEDManager:
    def __init__(self, indicator_led_pin:int = 18): #2
        self.devices: dict[str, LEDDevice] = {}
        self.devices_lock = threading.Lock()
        self.exit_flag = threading.Event()
        self.indicator_controller = PWMController(pin=indicator_led_pin)
        self.indicator_controller.set_state("ON")
        self.led_controllers: dict[str, PWMController] = {}

    def add_device(self, device:LEDDevice):
        with self.devices_lock:
            self.devices[device.name] = device
            device_controller = PWMController(pin=device.pin)
            device_controller.set_state(device.default_state)
            self.led_controllers[device.name] = device_controller

    def set_command(self, name:str, command:LEDCommand):
        with self.devices_lock:
            self.devices[name].set_command(command)

    def led_manager_thread(self):
        print("starting LED manager thread...")
        while not self.exit_flag.is_set() and not get_exit_flag().is_set():
            with self.devices_lock:
                devices_list = list(self.devices.values())
                for device in devices_list:
                    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    controller = self.led_controllers[device.name]
                    if device.command.end_time > current_time_str:
                        if device.command.state == "BLINK":
                            controller.flip_state()
                        else:
                            controller.set_state(device.command.state)
                    else:
                        controller.set_state(device.default_state)

            self.indicator_controller.flip_state()
            time.sleep(1.5)
                

    def start_manager_thread(self):
        led_manager_thread = threading.Thread(target=self.led_manager_thread)
        led_manager_thread.start()

    def stop_manager_thread(self):
        self.exit_flag.set()

    def print_devices(self):
        with self.devices_lock:
            devices_list = list(self.devices.values())
            for device in devices_list:
                print("name: ", device.name, 
                      " | def_state: ", device.default_state, 
                      " | pin: ", device.pin, 
                      " | cmd_state: ", device.command.state,
                      " | cmd_end_time: ", device.command.end_time)

    
            

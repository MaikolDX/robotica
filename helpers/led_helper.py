from factory.led_manager import LEDDevice, LEDManager


led_device_manager = LEDManager(indicator_led_pin=18)
#led_device_manager = LEDManager(indicator_led_pin=2)
led_device_manager.add_device(LEDDevice("RED_LED", 22, "OFF"))
#led_device_manager.add_device(LEDDevice("YELLOW_LED", 27, "OFF"))
led_device_manager.add_device(LEDDevice("BLUE_LED", 23, "OFF"))
led_device_manager.add_device(LEDDevice("GREEN_LED", 24, "OFF"))

import sys
if sys.platform != "win32":
    import RPi.GPIO as GPIO


    class GPIOAssistant:
        is_gpio_mode_set = False

        def __init__(self, gpio_nbr):
            if not GPIOAssistant.is_gpio_mode_set:
                print("start GPIO.setmode")
                GPIO.setmode(GPIO.BCM)
                GPIOAssistant.is_gpio_mode_set = True

            self.gpio_nbr = gpio_nbr
            GPIO.setup(self.gpio_nbr, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
        def isInput(self):
                if GPIO.input(self.gpio_nbr):
                    return True
                else:
                    return False

        def setOutput(self, set_value):
            GPIO.output(self.gpio_nbr, set_value)


        def __del__(self):
            GPIO.cleanup(self.gpio_nbr)

else:
    class GPIOAssistant:
        is_gpio_mode_set = False

        def __init__(self, gpio_nbr):
             self._isInput = False
            
        def isInput(self):
            n = input('y or n: ')
            if n == "y":    return True
            else:           return False

        def setOutput(self, set_value):
            pass


        def __del__(self):
            pass
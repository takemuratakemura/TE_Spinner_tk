import sys
if sys.platform != "win32":
    import RPi.GPIO as GPIO


    class GPIOAssistant:
        is_gpio_mode_set = False

        def __init__(self, gpio_nbr, isInput):
            self.__isInput = isInput
            if not GPIOAssistant.is_gpio_mode_set:
                GPIO.setmode(GPIO.BOARD)
                GPIOAssistant.is_gpio_mode_set = True
            
            self.gpio_nbr = gpio_nbr
            if self.__isInput == True: #Inputとして扱う場合
                GPIO.setup(self.gpio_nbr, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            else:               #Outputとして扱う場合
                GPIO.setup(self.gpio_nbr, GPIO.OUT, initial=0)
            
        def isInput(self):
                if self.__isInput == False: return False
                if GPIO.input(self.gpio_nbr):   return True
                else:   return False

        def setOutput(self, set_value):
            if self.__isInput == True: return
            GPIO.output(self.gpio_nbr, set_value)

        def __del__(self):
            GPIO.cleanup(self.gpio_nbr)
            
else:
    class GPIOAssistant:
        is_gpio_mode_set = False

        def __init__(self, gpio_nbr, isInput):
             self._isInput = False
            
        def isInput(self):
            pass

        def setOutput(self, set_value):
            pass

        def __del__(self):
            pass

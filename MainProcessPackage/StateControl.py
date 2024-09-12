from common.State import State
from MainProcessPackage.GPIOAssistant import GPIOAssistant
import RPi.GPIO as GPIO

class StateControl:
    state = State(State.IG_ON_MODE) #初期値はIG_ON_MODE 
    __currentIsStandbySW = False
    __currentIsDriveSW = False
    __previousIsStandbySW = False
    __previousIsDriveSW = False
    __DriveSwIN = GPIOAssistant(3, GPIO.IN) #PIN番号はテンポラリ
    __EmergencyStopOUT = GPIOAssistant(19, GPIO.OUT)
    
    @classmethod
    def init(cls, state):
        cls.state = state
        cls.__previousIsDriveSW = cls.__DriveSwIN.isInput()

    @classmethod
    def updateState(cls, state, isStandbySW, isError):
        cls.state = state
        cls.__currentIsStandbySW = isStandbySW
        cls.__currentIsDriveSW = cls.__DriveSwIN.isInput()
        
        cls.judgeFAIL_SAFE_MODE(isError)

        if cls.state == State.FAIL_SAFE_MODE:
            pass    #FAIL_SAFE_MODEの時は他のモードには遷移させない
        else:
            if (cls.state == State.IG_ON_MODE):
                if cls.__currentIsStandbySW and not(cls.__previousIsStandbySW):
                    cls.state = State.PARKING_MODE
                else:
                    pass
            elif (cls.state == State.PARKING_MODE) or (cls.state == State.DRIVE_MODE): 
                if cls.__currentIsDriveSW and not(cls.__previousIsDriveSW):
                    cls.state = State.DRIVE_MODE
                elif not(cls.__currentIsDriveSW) and (cls.__previousIsDriveSW):
                    cls.state = State.PARKING_MODE
                else:
                    pass
            else:
                pass    #ありえない遷移のため無視
            
        cls.__previousIsStandbySW = cls.__currentIsStandbySW
        cls.__previousIsDriveSW = cls.__currentIsDriveSW
        
    @classmethod
    def judgeFAIL_SAFE_MODE(cls, isError):
        if not(cls.state == State.FAIL_SAFE_MODE) and (isError == True):
            cls.state = State.FAIL_SAFE_MODE
            cls.__EmergencyStopOUT.setOutput(1)
    
    @classmethod
    def clearnup(cls):
        del cls.__DriveSwIN
        del cls.__EmergencyStopOUT
    

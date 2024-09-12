def MotState(Spinner_State,Error_Code):
    '''
    Motor State Controller
    0x01 Drive motors servo ON
    0x02 Tilt controll motor B/F servo ON
    0x04 Tilt controll motor L/R servo ON
    0x08 Drive motors STOP
    0x10 Tilt controll motor B/F STOP
    0x20 Tilt controll motor L/R STOP
    0x40 Reset Errors of all motors

    '''
    if Spinner_State == 1: #IG-ON
        MotState_Command = 0x00
    elif Spinner_State == 2: #Parking Mode
        MotState_Command = 0x02
    elif Spinner_State ==  3: #Driving Mode
        MotState_Command = (0x01 | 0x02 |0x04)
    elif Spinner_State ==  4: #Fault Mode
        MotState_Command = (0x10 | 0x20 |0x40)
    else:
        MotState_Command = 0x00
            
    return MotState_Command

if __name__ == "__main__":
    print(MotState(3,0))
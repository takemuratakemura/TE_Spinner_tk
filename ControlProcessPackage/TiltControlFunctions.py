def Calib_Exe_Judge(Spinner_State,calib_rq,calib_state):
    if Spinner_State == 0x01 & calib_rq == 0x01 & calib_state != 0x02:
        Calib_exe_judge = 0x01
    else:
        Calib_exe_judge = 0x00
        
    return Calib_exe_judge

def get_target_roll(state, js_lr_in):
    TILT_RANGE = 11 #deg
    js_lr = min(1.0, max(-1.0,js_lr_in))
    target_roll = js_lr * TILT_RANGE
    
    return target_roll
        

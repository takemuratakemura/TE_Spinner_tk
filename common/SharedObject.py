import multiprocessing
from .State import State
import ctypes

class SharedObject:
    def __init__(self):
        self.__stateLock = multiprocessing.Lock() #車両状態制御用LOCK
        self.__i4g_p0_state = multiprocessing.Value(ctypes.c_int, State.IG_ON_MODE) #車両状態(0:IG_ON_MODE, 1:PARKING_MODE, 2:DRIVE_MODE, 3:FAIL_SAFE_MODE)
        self.i4g_p0_batteryLevel = multiprocessing.Value(ctypes.c_uint, 100) #バッテリ残量
        self.f4g_p1_joyAxisLR = multiprocessing.Value(ctypes.c_float, 0) #ジョイスティックの左右操作量
        self.f4g_p1_joyAxisFB = multiprocessing.Value(ctypes.c_float, 0) #ジョイスティックの前後操作量
        self.f4g_p2_speed = multiprocessing.Value(ctypes.c_float, 0) #車両速度
        self.i4g_p0_HWid = multiprocessing.Value(ctypes.c_uint, 0) #ハードウェア識別(0:POC, 1:本番機)
        self.u1g_p1_PKB = multiprocessing.Value(ctypes.c_char, 0) #PKB信号


    @property
    def state(self):
        with self.__stateLock:
            return self.__i4g_p0_state.value
    @state.setter
    def state(self, state):
        with self.__stateLock:
        
            if self.__i4g_p0_state.value == State.FAIL_SAFE_MODE:
                pass    #FAIL_SAFE_MODEの時は他のモードには遷移させない
            elif state == State.FAIL_SAFE_MODE:
                self.__i4g_p0_state.value = state    #引数がFAIL_SAFE_MODEの場合、他のStateであってもFAIL_SAFE_MODEをセットする
            else:

                if (self.__i4g_p0_state.value == State.IG_ON_MODE) and not(state == State.PARKING_MODE):
                    pass    #ありえない遷移のため無視
                elif (self.__i4g_p0_state.value == State.PARKING_MODE) and not(state == State.DRIVE_MODE): 
                    pass    #ありえない遷移のため無視
                elif (self.__i4g_p0_state.value == State.DRIVE_MODE) and not(state == State.PARKING_MODE): 
                    pass    #ありえない遷移のため無視
                else:
                    self.__i4g_p0_state.value = state


    

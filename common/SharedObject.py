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
        self.u1g_p1_PKB = multiprocessing.Value(ctypes.c_uint, 0) #PKB信号
        self.i4g_p0_CTRtype = multiprocessing.Value(ctypes.c_uint, 1) #0:本番機, 1:PSコントローラ, 2:Microbit
        self.b1g_p0_Stop = multiprocessing.Value(ctypes.c_bool, False) #通信処理停止SW
        self.i4g_p1_isOperationProcessError = multiprocessing.Value(ctypes.c_int, 0)
        self.i4g_p2_isControlProcessError = multiprocessing.Value(ctypes.c_int, 0)
        self.f4g_p1_EulerAngles_Pitch = multiprocessing.Value(ctypes.c_float, 0) #オイラー角y軸(Pitch)	#◆◆◆◆◆重心制御
        self.f4g_p1_EulerAngles_Roll = multiprocessing.Value(ctypes.c_float, 0) #オイラー角x軸(Roll)		#◆◆◆◆◆重心制御
        self.f4g_p1_EulerAngles_Yaw = multiprocessing.Value(ctypes.c_float, 0) #オイラー角z軸(Yaw)		#◆◆◆◆◆重心制御
        self.f4g_p1_Acceleration_x = multiprocessing.Value(ctypes.c_float, 0) #加速度x方向	#◆◆◆◆◆重心制御
        self.f4g_p1_Acceleration_y = multiprocessing.Value(ctypes.c_float, 0) #加速度y方向	#◆◆◆◆◆重心制御
        self.f4g_p1_Acceleration_z = multiprocessing.Value(ctypes.c_float, 0) #加速度z方向	#◆◆◆◆◆重心制御  
        self.f4g_p1_AngularVelocity_x = multiprocessing.Value(ctypes.c_float, 0) #角速度x軸	#◆◆◆◆◆重心制御
        self.f4g_p1_AngularVelocity_y = multiprocessing.Value(ctypes.c_float, 0) #角速度y軸	#◆◆◆◆◆重心制御
        self.f4g_p1_AngularVelocity_z = multiprocessing.Value(ctypes.c_float, 0) #角速度z軸	#◆◆◆◆◆重心制御
        self.f4g_p2_MotSpeed_FR =  multiprocessing.Value(ctypes.c_float, 0) #
        self.f4g_p2_MotSpeed_FL =  multiprocessing.Value(ctypes.c_float, 0) #
        self.f4g_p2_MotSpeed_RR =  multiprocessing.Value(ctypes.c_float, 0) #
        self.f4g_p2_MotSpeed_RL =  multiprocessing.Value(ctypes.c_float, 0) #
        self.us2g_p2_PLC_error =  multiprocessing.Value(ctypes.c_ushort, 0) #
        self.f4g_p2_WeightPos_LR =  multiprocessing.Value(ctypes.c_float, 0) #
        self.f4g_p2_WeightPos_BF =  multiprocessing.Value(ctypes.c_float, 0) #
        
        # クラス内のmultiprocessing.Valueのインスタンス変数を辞書に追加
        self.__allValues = {}
        for name, value in self.__dict__.items():
            try:
                if isinstance(value,  multiprocessing.sharedctypes.Synchronized):   self.__allValues[name] = value
            except: 
                pass


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
    
    def getAllValues(self):
        return {name: value.value for name, value in self.__allValues.items()}


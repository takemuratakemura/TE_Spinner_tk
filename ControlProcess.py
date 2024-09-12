#駆動/重心制御(プロセス2)記載用pyファイル
import time
from common.State import State
import asyncio
from struct import pack
from ControlProcessPackage.LinearInterpolation import get_target_speed
from ControlProcessPackage.LinearInterpolation import get_target_accel
from ControlProcessPackage.LinearInterpolation import get_target_decel
from ControlProcessPackage.TiltControlFunctions import Calib_Exe_Judge
from ControlProcessPackage.TiltControlFunctions import get_target_roll
from ControlProcessPackage.MotStateController import MotState

'''TCP通信用'''
import time
from MainProcessPackage.PLCComRecvObject import PLCComRecvObject
from MainProcessPackage.TCPClient import TCPClient

# Python上でC言語の関数を使用できるようにするモジュールctypesのインポート
import ctypes										#◆◆◆◆◆重心制御

import math

#TCPClientがデータを受信したときに実行されるCallback

def recvEvent_PLC(sender,buffer):
    global moniteringComWDT_PLC
    global recvObject_PLC
    moniteringComWDT_PLC = 0
    recvObject_PLC.decode_recvdata(buffer)    
    
#取得した現stateを表示する関数例
def printState(state):
    if state == State.IG_ON_MODE:
        print('p2:Current State is IG_ON_MODE')
    elif state == State.PARKING_MODE:
        print('p2:Current State is PARKING_MODE')
    elif state == State.DRIVE_MODE:
        print('p2:Current State is DRIVE_MODE')
    else:
        print('p2:Current State is FAIL_SAFE_MODE')



#駆動/重心制御用としてプロセス化される関数 ※process2=controlProcessのメイン関数にあたる
def worker(shared_obj):
    HWid = shared_obj.i4g_p0_HWid.value
    
    if HWid == 1:#ハードウェア識別(0:POC, 1:本番機)
        global moniteringComWDT_PLC
        moniteringComWDT_PLC = 0
        #TCP通信
        global recvObject_PLC
        recvObject_PLC = PLCComRecvObject()
        
    asyncio.run(ctrl_main(shared_obj))


    
async def ctrl_main(shared_obj):
    #★★プロセス開始時の初期設定(ローカル変数/定数の設定)や初期化処理を記述
    HWid = shared_obj.i4g_p0_HWid.value 
    
    p1_time_max = 0
    Max_Torque = 450.0 #Nm
    Pos_Range = 100 #mm
    
    #TCP通信クラス初期化
    if HWid == 1:#ハードウェア識別(0:POC, 1:本番機)
        loop = asyncio.get_event_loop() 
        client_plc = TCPClient(loop, recvEvent_PLC, "192.168.1.254", 55556)
        loop.create_task(client_plc.run())
        await asyncio.sleep(1)
    else:
        ''' ----------UDP Communication for Proto---------- '''
        import socket
        from struct import unpack
        M_SIZE = 32
        dummy = 0
        locaddr = ('0.0.0.0', 9998)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.01)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        sock.bind(locaddr)
        #受信確認
        message, cli_addr = sock.recvfrom(M_SIZE)
        ##モータ状態リセットを送信
        state_command = 0x06 #0x01 servo on, 0x02 stop, 0x04 reset
        send_data = pack('<4sHHHHh', b'TRQT', dummy, dummy,  dummy, state_command ,0)
        sock.sendto(send_data,cli_addr)
        time.sleep(3)
        ##モータ状態をサーボON
        state_command = 0x01 #0x01 servo on, 0x02 stop, 0x04 reset
        send_data = pack('<4sHHHHh', b'TRQT', dummy, dummy,  dummy, state_command ,0)
        sock.sendto(send_data,cli_addr)
        ''' ----------UDP Communication for Proto---------- '''
    
    #Dummy
    Target_Pitch : float = 1.0
    Target_Roll : float = 2.0
    Motstate_cmd  = 0x01
    Act_Velo = 0
    print_cnt = 0
    
    #駆動/重心制御用プロセスのメインループ
    while True:
        p1_start = time.time()
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        Spinner_State = shared_obj.state #__i4g_p0_stateはSharedObject.py内のstate関数経由で読み出すため「shared_obj.state」の記述で良く「.value」は付けない
        ### state = 0:IG-ON, 1:Parking, 2:Drive, 3:Fail
        HWid = shared_obj.i4g_p0_HWid.value			#ハードウェア識別(0:POC, 1:本番機)
        
        Yaw = shared_obj.f4g_p1_EulerAngles_Yaw.value		#◆◆◆◆◆重心制御
        Pitch = shared_obj.f4g_p1_EulerAngles_Pitch.value	#◆◆◆◆◆重心制御
        Roll = shared_obj.f4g_p1_EulerAngles_Roll.value		#◆◆◆◆◆重心制御
        Accl_x = shared_obj.f4g_p1_Acceleration_x.value		#◆◆◆◆◆重心制御
        Accl_y = shared_obj.f4g_p1_Acceleration_y.value		#◆◆◆◆◆重心制御
        Accl_z = shared_obj.f4g_p1_Acceleration_z.value		#◆◆◆◆◆重心制御
        Gyro_x = shared_obj.f4g_p1_AngularVelocity_x.value	#◆◆◆◆◆重心制御
        Gyro_y = shared_obj.f4g_p1_AngularVelocity_y.value	#◆◆◆◆◆重心制御
        Gyro_z = shared_obj.f4g_p1_AngularVelocity_z.value	#◆◆◆◆◆重心制御
        Calib_rq = shared_obj.us2g_p0_CoGcalib_request.value
        
        #PLC Recieved Data
        Motspd_FR = recvObject_PLC.f4s_p2_MotSpeed_FR
        Motspd_FL = recvObject_PLC.f4s_p2_MotSpeed_FL
        Motspd_RR = recvObject_PLC.f4s_p2_MotSpeed_RR
        Motspd_RL = recvObject_PLC.f4s_p2_MotSpeed_RL
        WeightPos_LR = recvObject_PLC.f4s_p2_WeightPos_LR
        WeightPos_BF = recvObject_PLC.f4s_p2_WeightPos_BF
        Calib_state = recvObject_PLC.us2s_p2_Calib_state
        
        
        ''' ----------UDP Communication for Proto---------- '''
        if HWid == 0 :#ハードウェア識別(0:POC, 1:本番機)
            message, cli_addr = sock.recvfrom(M_SIZE)
            command, sender_sequence, Act_Velo, Act_Torque, Spinner_State, mode, dummy_h, dummy_b = unpack('<6sHlhHbhb', message)

        ''' ----------UDP Communication for Proto---------- '''


        
        
        #コントローラからの入力（global経由）
        js_bf_local = shared_obj.f4g_p1_joyAxisFB.value
        js_lr_local = shared_obj.f4g_p1_joyAxisLR.value
        js_stp_local = shared_obj.b1g_p0_Stop.value
        
        torque = int(js_bf_local * Max_Torque)
        pos = int(js_lr_local * Pos_Range)
        
        #コントローラのSTOPボタンが推されたら通信終了
        if js_stp_local:
            sock.close()
            time.sleep(1)
            break
		
        #moniteringComWDT_PLC += 1
        '''Motor State Controller'''
        Motstate_cmd = MotState(Spinner_State,0x0)
        
        '''Center of gravity caliblation control only in Parking Mode'''
        Calib_exe = Calib_Exe_Judge(Spinner_State,Calib_rq,Calib_state)
        
        '''Roll Control'''
        Target_Roll = get_target_roll(Spinner_State,js_lr_local)

        '''Speed Calculation'''
        if HWid == 0:
            Velo = float(Act_Velo) * 7.5 / 360 #cnt/sec -> rps
            Speed_mm_s = (Velo / 5 * 42 * math.pi * 500 / 368.9)	#★★★速度算出
            Speed_km_h = Speed_mm_s * 3600 / 1000000			#★★★速度算出
        else:
            Velo = float(Act_Velo) * 6 / 360 #cnt/sec -> rps
            Speed_mm_s = (Velo / 5.2 * 248 * math.pi * 2000 / 1570)	#★★★速度算出
            Speed_km_h = Speed_mm_s * 3600 / 1000000			#★★★速度算出

#       tmp_speed = js_lr_local          #accelテスト用
#       if(tmp_speed > 0):               #accelテスト用
#           tmp_speed = tmp_speed * 4    #accelテスト用
#       Speed_km_h = tmp_speed

        #目標速度引き当て
        target_speed = get_target_speed(js_bf_local)

        #目標速度差から目標加速度を引き当てる（目標速度差 = 目標速度 - 実速度）
        def_speed = target_speed - Speed_km_h
        if def_speed >= 0:
            target_accel = get_target_accel(def_speed)
        else:
            target_accel = get_target_decel(def_speed)
#        print("joystick:", round(js_bf_local, 1),
#              "  target speed:", round(target_speed, 1),
#              "  real speed:", round(Speed_km_h, 1),
#              "  target accel:", round(target_accel, 1))

        state_command = 0x01 #Servo ON

        
        if HWid == 1:#ハードウェア識別(0:POC, 1:本番機)
            #TCP通信送信
            send_data = pack('ffffffHHi', Pitch,Roll,Gyro_x,Gyro_y,Target_Pitch,Target_Roll,Calib_exe,Motstate_cmd,Spinner_State)
            client_plc.send(send_data)
        else:
            #UDP送信 for PoC
            state_command = 0x01
            send_data = pack('<4sHHhHh', b'TRQT', 0, dummy, pos, state_command, torque)
            sock.sendto(send_data, cli_addr)
            
        await asyncio.sleep(0.01)

        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        #printState(state) #【例】
        #print("p2:EulerAngles -> ({}, {}, {})".format(Yaw, Pitch, Roll))	#◆◆◆◆◆重心制御
        #print("p2:Accl        -> ({}, {}, {})".format(Accl_x, Accl_y, Accl_z))	#◆◆◆◆◆重心制御
        #print("p2:Gyro        -> ({}, {}, {})".format(Gyro_x, Gyro_y, Gyro_z))	#◆◆◆◆◆重心制御
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        shared_obj.f4g_p2_speed.value = Speed_km_h
        shared_obj.f4g_p2_MotSpeed_FR.value = Motspd_FR
        shared_obj.f4g_p2_MotSpeed_FL.value = Motspd_FL
        shared_obj.f4g_p2_MotSpeed_RR.value = Motspd_RR
        shared_obj.f4g_p2_MotSpeed_RL.value = Motspd_RL
        shared_obj.us2g_p2_PLC_error.value = recvObject_PLC.us2s_p2_PLC_error
        shared_obj.f4g_p2_WeightPos_LR.value = WeightPos_LR
        shared_obj.f4g_p2_WeightPos_BF.value = WeightPos_BF
        
        #★★必要に応じて待ち時間を設定
        #time.sleep(1)
        p1_end = time.time()
        p1_time = p1_end - p1_start
        p1_time_max = max(p1_time_max, p1_time)
        #print(p1_time_max)
        await asyncio.sleep(max(0.001,(0.032-p1_time)))
        
        print_cnt += 1
        if print_cnt > 100:
            print_cnt = 0
            print("P2 Cycle Time : {:.1f} [ms]"  .format((time.time() -p1_start)*1000))
            printState(Spinner_State) 

##### 20240909 EPB監視追加　#####


#操作/表示系(プロセス1)記載用pyファイル
import time
from common.State import State
'''joystick用初期化処理(joystick①)'''
import pygame
import pyudev
import sys


# Python上でC言語の関数を使用できるようにするモジュールctypesのインポート
import ctypes										#◆◆◆◆◆重心制御
from OperationProcessPackage.BNO055io import BNO055	#速度算出用センサpyファイル	#◆◆◆◆◆重心制御
from OperationProcessPackage.BMX055io import BMX055	#傾き算出用センサpyファイル	#◆◆◆◆◆重心制御
import tkinter as tk								#傾き描画確認のため			#◆◆◆◆◆重心制御
import math											#三角関数等利用のため		#◆◆◆◆◆重心制御

# グローバル変数の初期化（プロセス全体で使用する）
WiredJS_connected = False  # 有線ジョイスティック (Thrustmaster)
WirelessJS_connected = False  # 無線ジョイスティック (Gamepad)
EPB_connected = False  # 電動サイドブレーキ

def device_event(action, device):
    global WiredJS_connected, WirelessJS_connected  # グローバル変数を参照
    
    # デバイス名とパスを取得
    device_name = device.get('ID_MODEL', '')
    device_node = device.device_node
    device_path = device.device_path

    # デバイス情報を出力して確認
    print(f"Device Event - Action: {action}, Device Path: {device_path}, Device Name: {device_name}")

    if action == 'remove':
        if 'Flight' in device_name:
            if WiredJS_connected:
                WiredJS_connected = False

                print("Wired Joystick Disconnected!")
        elif 'Gamepad' in device_name:
            if WirelessJS_connected:
                WirelessJS_connected = False
                print("Wireless Joystick Disconnected!")
        elif '手柄' in device_name:
            if EPB_connected:
                EPB_connected = False
                print("EPB Disconnected!")


#取得した現stateを表示する関数例
def printState(state):
    if state == State.IG_ON_MODE:
        print('p1:Current State is IG_ON_MODE')
    elif state == State.PARKING_MODE:
        print('p1:Current State is PARKING_MODE')
    elif state == State.DRIVE_MODE:
        print('p1:Current State is DRIVE_MODE')
    else:
        print('p1:Current State is FAIL_SAFE_MODE')

#操作/表示系用としてプロセス化される関数 ※process1=operationProcessのメイン関数にあたる
def worker(shared_obj):
    global WiredJS_connected, WirelessJS_connected  # グローバル変数として宣言
    
    #★★プロセス開始時の初期設定(ローカル変数/定数の設定)や初期化処理を記述
    STOP_FLAG = False     #停止フラグ
    p0_time_max = 0       #定期周期用タイマ
    js_input_lr = 0       #左右ジョイスティックの値初期化
    js_input_lr_r = 0     #冗長監視用左右ジョイスティックの値初期化
    js_input_bf = 0       #前後ジョイスティックの値初期化
    js_input_bf_r = 0     #冗長監視用前後ジョイスティックの値初期化
    CORRECTION_LR = 0.0   # 左右軸の補正定数
    coe_LR = 1.0          # 左右軸の補正係数
    CORRECTION_BF = 0.463 # 前後軸の補正定数
    coe_BF = 2.0          # 前後軸の補正係数
    TOLERANCE = 0.5       # 許容誤差範囲を設定

    '''joystick用初期化処理(joystick②)'''
    pygame.init()# Pygameの初期化
    pygame.joystick.init() # ジョイスティックの初期化
    
    # pyudevをセットアップしてUSBデバイスの接続状態を監視
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')
    monitor.start()
    
    # 接続されているジョイスティックの数を取得
    num_joysticks = pygame.joystick.get_count()
    print("joycon_num:", num_joysticks)
    
    # 現在接続されているデバイスをスキャン
    for device in context.list_devices(subsystem='input'):
        if 'ID_MODEL' in device:
            device_name = device.get('ID_MODEL', '')
            print(device_name)
            if 'Flight' in device_name:
                WiredJS_connected = True
                print("Wired Joystick (Thrustmaster) Connected!")
            elif 'Gamepad' in device_name:
                WirelessJS_connected = True
                print("Wireless Joystick (Gamepad) Connected!")
            elif '手柄' in device_name:
                EPB_connected = True
                print("EPB Connected!")
                    
    #ここでストップ
    #print("stop")
    #sys.exit()  # 正常終了

    
    # 有線ジョイスティック(0)か無線ジョイスティック(1)かを選択
    i4g_p1_CTRtype = 0  # ここを手動で変更
    #joystick = pygame.joystick.Joystick(i4g_p1_CTRtype)
            
    # 有線接続を指示しているのに信号が途絶した場合
    if not WiredJS_connected and i4g_p1_CTRtype == 0:
        print("Wired joystick selected despite being disconnected.")
        js_input_lr = 0.0
        js_input_bf = 0.0
    elif not WirelessJS_connected and i4g_p1_CTRtype == 1:
        print("Wireless joystick selected despite being disconnected.")
        js_input_lr = 0.0
        js_input_bf = 0.0

    
    # 無線ジョイスティックのみ接続の場合は自動で0に更新    
    if not WiredJS_connected:

        joystick = pygame.joystick.Joystick(0)
    else:
        joystick = pygame.joystick.Joystick(i4g_p1_CTRtype)
    
    joystick.init()

    '''joystick用初期化処理'''
    
    EulerAngles_zyx = ctypes.c_float * 3		#◆◆◆◆◆重心制御
    Acceleration_xyz = ctypes.c_float * 3		#◆◆◆◆◆重心制御
    AngularVelocity_xyz = ctypes.c_float * 3	#◆◆◆◆◆重心制御
    
    bmx = BMX055()								#◆◆◆◆◆重心制御
    time.sleep(0.1)								#◆◆◆◆◆重心制御
    
    bno = BNO055()								#◆◆◆◆◆重心制御
    if bno.begin() is not True:					#◆◆◆◆◆重心制御
        print("Error initializing device")		#◆◆◆◆◆重心制御
        #exit()									#◆◆◆◆◆重心制御
    time.sleep(1)								#◆◆◆◆◆重心制御
    bno.setExternalCrystalUse(True)				#◆◆◆◆◆重心制御
    
    root = tk.Tk()								#◆◆◆◆◆重心制御
    root.geometry("600x200")					#◆◆◆◆◆重心制御
    canvas = tk.Canvas(root, bg = "white")		#◆◆◆◆◆重心制御
    canvas.pack(fill = tk.BOTH, expand = True)	#◆◆◆◆◆重心制御

 
    # デバイスイベントハンドラを接続
    observer = pyudev.MonitorObserver(monitor, device_event)
    observer.start()

    #操作/表示系用プロセスのメインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state #__i4g_p0_stateはSharedObject.py内のstate関数経由で読み出すため「shared_obj.state」の記述で良く「.value」は付けない
        Speed_km_h = shared_obj.f4g_p2_speed.value
        
        '''joystick用ループ処理（joystick③)'''
        pygame.event.pump()  # 内部イベント状態を更新

        #有線ジョイスティックの操作を読み取る    
        if WiredJS_connected and i4g_p1_CTRtype == 0:
            js_input_bf = joystick.get_axis(1)  # 前後の軸
            js_input_lr = joystick.get_axis(0)  # 左右の軸
            js_input_bf_r = joystick.get_axis(3)  # 冗長監視用の前後の軸 (r = redundant)
            js_input_lr_r = joystick.get_axis(2)  # 冗長監視用の左右の軸 (r = redundant)
            
	        # 補正を適用
            js_input_lr_r = (js_input_lr_r + CORRECTION_LR) * coe_LR
            js_input_bf_r = (js_input_bf_r + CORRECTION_BF) * coe_BF
            
            # 冗長監視との誤差が一定以上の場合、値を0に設定
            if abs(js_input_lr_r - js_input_lr) > TOLERANCE:
                js_input_lr = 0.0  # 信号を0に上書き
            if abs(js_input_bf_r - js_input_bf) > TOLERANCE:
                js_input_bf = 0.0  # 信号を0に上書き
                
        #無線ジョイスティックの操作を読み取る
        elif WirelessJS_connected and (i4g_p1_CTRtype == 1 or not WiredJS_connected):
            js_input_bf = joystick.get_axis(4)  # 右スティックの前後の軸
            js_input_lr = joystick.get_axis(0)  # 左スティックの左右の軸

        
        # 有線接続を指示しているのに信号が途絶した場合
        if not WiredJS_connected and i4g_p1_CTRtype == 0:
            print("Joystick has been disconnected.")
            js_input_lr = 0.0
            js_input_bf = 0.0
        
        # 無線接続を指示しているのに信号が途絶した場合
        if not WirelessJS_connected and (i4g_p1_CTRtype == 1 or not WiredJS_connected):
            print("Joystick has been disconnected.")
            js_input_lr = 0.0
            js_input_bf = 0.0
       
        #9軸センサー値換算結果取得
        EulerAngles_zyx = bno.getVector(BNO055.VECTOR_EULER)		#◆◆◆◆◆重心制御
        Acceleration_xyz = bmx.read_accl()							#◆◆◆◆◆重心制御
        AngularVelocity_xyz = bmx.read_gyro()						#◆◆◆◆◆重心制御
        #print("p1:EulerAngles -> {}".format(EulerAngles_zyx))		#◆◆◆◆◆重心制御
        #print("p1:Accl        -> {}".format(Acceleration_xyz))		#◆◆◆◆◆重心制御
        #print("p1:Gyro        -> {}".format(AngularVelocity_xyz))	#◆◆◆◆◆重心制御
        
        '''
        #傾き描画																					#◆◆◆◆◆重心制御
        canvas.delete("all")																	#◆◆◆◆◆重心制御
        fnt = ("Ubuntu Mono",10)																#◆◆◆◆◆重心制御
        txt1 = ("Pitch:{}[deg]".format(EulerAngles_zyx[1]))										#◆◆◆◆◆重心制御
        txt2 = ("Roll:{}[deg]".format(EulerAngles_zyx[2]))										#◆◆◆◆◆重心制御
        txt3 = ("Gyro_Pitch:{:.2f}[deg/s]".format(AngularVelocity_xyz[1]))
        txt4 = ("Gyro_Roll:{:.2f}[deg/s]".format(AngularVelocity_xyz[0]))
        txt5 = ("Speed:{:.2f}[km/h]".format(Speed_km_h))
        canvas.create_text(150, 8, text = txt1, fill="black", font=fnt, tag="INFOTEXT")		#◆◆◆◆◆重心制御
        canvas.create_text(450, 8, text = txt2, fill="black", font=fnt, tag="INFOTEXT")		#◆◆◆◆◆重心制御        
        canvas.create_text(150, 23, text = txt3, fill="black", font=fnt, tag="INFOTEXT")		#◆◆◆◆◆重心制御
        canvas.create_text(450, 23, text = txt4, fill="black", font=fnt, tag="INFOTEXT")		#◆◆◆◆◆重心制御
        canvas.create_text(300, 180, text = txt5, fill="black", font=fnt, tag="INFOTEXT")		#◆◆◆◆◆重心制御        
        pitch_line_x = 50*math.cos(math.radians(EulerAngles_zyx[1]))							#◆◆◆◆◆重心制御
        pitch_line_y = 50*math.sin(math.radians(EulerAngles_zyx[1]))							#◆◆◆◆◆重心制御
        roll_line_x = 50*math.cos(math.radians(EulerAngles_zyx[2]))								#◆◆◆◆◆重心制御
        roll_line_y = 50*math.sin(math.radians(EulerAngles_zyx[2]))								#◆◆◆◆◆重心制御

        #傾き描画																												#◆◆◆◆◆重心制御
        canvas.delete("all")																								#◆◆◆◆◆重心制御        
        fnt = ("Ubuntu Mono",10)																							#◆◆◆◆◆重心制御
        txt1 = ("Pitch:{}[dig]".format(EulerAngles_zyx[1]))																	#◆◆◆◆◆重心制御
        txt2 = ("Roll:{}[dig]".format(EulerAngles_zyx[2]))																	#◆◆◆◆◆重心制御
        canvas.create_text(150, 20, text = txt1, fill="black", font=fnt, tag="INFOTEXT")									#◆◆◆◆◆重心制御
        canvas.create_text(450, 20, text = txt2, fill="black", font=fnt, tag="INFOTEXT")									#◆◆◆◆◆重心制御        
        pitch_line_x = 50*math.cos(math.radians(EulerAngles_zyx[1]))														#◆◆◆◆◆重心制御
        pitch_line_y = 50*math.sin(math.radians(EulerAngles_zyx[1]))														#◆◆◆◆◆重心制御
        roll_line_x = 50*math.cos(math.radians(EulerAngles_zyx[2]))															#◆◆◆◆◆重心制御
        roll_line_y = 50*math.sin(math.radians(EulerAngles_zyx[2]))															#◆◆◆◆◆重心制御

        canvas.create_line(150-pitch_line_x, 100+pitch_line_y, 150+pitch_line_x, 100-pitch_line_y, fill ="Blue", width = 5)	#◆◆◆◆◆重心制御
        canvas.create_line(450-roll_line_x, 100+roll_line_y, 450+roll_line_x, 100-roll_line_y, fill ="Green", width = 5)	#◆◆◆◆◆重心制御
        root.update()
        '''
        
		#共用変数へ書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        shared_obj.f4g_p1_joyAxisFB.value = -js_input_bf
        shared_obj.f4g_p1_joyAxisLR.value = js_input_lr
        shared_obj.b1g_p0_Stop.value = STOP_FLAG 
        '''joystick用ループ処理'''
        
        #print("前後入力:", round(shared_obj.f4g_p1_joyAxisFB.value,2),"左右入力:", round(shared_obj.f4g_p1_joyAxisLR.value,2),"Wired:",WiredJS_connected,"Wireless:",WirelessJS_connected)

#        print("前後入力:", round(shared_obj.f4g_p1_joyAxisFB.value,2),"前後冗長:", round(js_input_bf_r,2),"左右入力:", round(shared_obj.f4g_p1_joyAxisLR.value,2),"左右冗長:", round(js_input_lr_r,2),"Wired:",WiredJS_connected,"Wireless:",WirelessJS_connected)

        
        shared_obj.f4g_p1_EulerAngles_Yaw.value = EulerAngles_zyx[0]		#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_EulerAngles_Pitch.value = EulerAngles_zyx[1]		#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_EulerAngles_Roll.value = EulerAngles_zyx[2]		#◆◆◆◆◆重心制御
        
        shared_obj.f4g_p1_Acceleration_x.value = Acceleration_xyz[0]		#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_Acceleration_y.value = Acceleration_xyz[1]		#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_Acceleration_z.value = Acceleration_xyz[2]		#◆◆◆◆◆重心制御
        
        shared_obj.f4g_p1_AngularVelocity_x.value = AngularVelocity_xyz[0]	#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_AngularVelocity_y.value = AngularVelocity_xyz[1]	#◆◆◆◆◆重心制御
        shared_obj.f4g_p1_AngularVelocity_z.value = AngularVelocity_xyz[2]	#◆◆◆◆◆重心制御


        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        #printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"


        #★★必要に応じて待ち時間を設定
        time.sleep(0.1)


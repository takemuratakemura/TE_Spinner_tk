#操作/表示系(プロセス1)記載用pyファイル
import time
from common.State import State
'''joystick用初期化処理(joystick①)'''
import pygame

# Python上でC言語の関数を使用できるようにするモジュールctypesのインポート
import ctypes										#◆◆◆◆◆重心制御
from OperationProcessPackage.BNO055io import BNO055	#速度算出用センサpyファイル	#◆◆◆◆◆重心制御
from OperationProcessPackage.BMX055io import BMX055	#傾き算出用センサpyファイル	#◆◆◆◆◆重心制御
import tkinter as tk								#傾き描画確認のため			#◆◆◆◆◆重心制御
import math											#三角関数等利用のため		#◆◆◆◆◆重心制御


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
    #★★プロセス開始時の初期設定(ローカル変数/定数の設定)や初期化処理を記述
    STOP_FLAG = False #停止フラグ
    p0_time_max = 0   #定期周期用タイマ
    js_input_lr = 0 #左右ジョイスティックの値初期化
    js_input_bf = 0 #前後ジョイスティックの値初期化

    '''joystick用初期化処理(joystick②)'''
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
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
        exit()									#◆◆◆◆◆重心制御
    time.sleep(1)								#◆◆◆◆◆重心制御
    bno.setExternalCrystalUse(True)				#◆◆◆◆◆重心制御
    
    root = tk.Tk()								#◆◆◆◆◆重心制御
    root.geometry("600x200")					#◆◆◆◆◆重心制御
    canvas = tk.Canvas(root, bg = "white")		#◆◆◆◆◆重心制御
    canvas.pack(fill = tk.BOTH, expand = True)	#◆◆◆◆◆重心制御

 
    #操作/表示系用プロセスのメインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state #__i4g_p0_stateはSharedObject.py内のstate関数経由で読み出すため「shared_obj.state」の記述で良く「.value」は付けない
        
        '''joystick用ループ処理（joystick③)'''
        if pygame.event.get():
            #ジョイスティックの操作を読み取る
            js_input_lr = joystick.get_axis(0) #左のジョイスティックの左右方向
            #print(js_input_lr)
            js_input_bf = joystick.get_axis(4) #右のジョイスティックの上下方向
            #print(js_input_bf)

            # Aボタンが押されたら終了
            if joystick.get_button(0):
                print('stop!')
                STOP_FLAG = True
                break
        
        #9軸センサー値換算結果取得
        EulerAngles_zyx = bno.getVector(BNO055.VECTOR_EULER)		#◆◆◆◆◆重心制御
        Acceleration_xyz = bmx.read_accl()							#◆◆◆◆◆重心制御
        AngularVelocity_xyz = bmx.read_gyro()						#◆◆◆◆◆重心制御
        #print("p1:EulerAngles -> {}".format(EulerAngles_zyx))		#◆◆◆◆◆重心制御
        #print("p1:Accl        -> {}".format(Acceleration_xyz))		#◆◆◆◆◆重心制御
        #print("p1:Gyro        -> {}".format(AngularVelocity_xyz))	#◆◆◆◆◆重心制御
        
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
        

		#共用変数へ書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        shared_obj.f4g_p1_joyAxisFB.value = js_input_bf
        shared_obj.f4g_p1_joyAxisLR.value = js_input_lr
        shared_obj.i4g_p1_ComStop.value = STOP_FLAG 
        '''joystick用ループ処理'''
        
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

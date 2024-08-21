#操作/表示系(プロセス1)記載用pyファイル
import time
from common.State import State
'''joystick用初期化処理(joystick①)'''
import pygame


'''Microbit用初期化処理(Microbit①)'''
from bluepy.btle import DefaultDelegate, Peripheral,ADDR_TYPE_RANDOM

# takemura microbitのMACアドレス
MAC_ADDRESS = 'F3:52:BC:B2:86:72'

#ACCELEROMETER SERVICE/CHARACTERISTICS UUID
ACC_SERVICE_UUID = 'E95D0753251D470AA062FA1922DFA9A8'
ACC_CHARACTERISTICS_UUID = 'E95DCA4B251D470AA062FA1922DFA9A8'

#BUTTON SERVICE/BUTTON A CHARACTERISTICS UUID
BTN_SERVICE_UUID = 'E95D9882251D470AA062FA1922DFA9A8'
BTN_A_CHARACTERISTICS_UUID = 'E95DDA90251D470AA062FA1922DFA9A8'
BTN_B_CHARACTERISTICS_UUID = 'E95DDA91251D470AA062FA1922DFA9A8'

#TEMPATURE SERVICE/CHARACTERISTICS UUID
TMP_SERVICE_UUID = 'E95D6100251D470AA062FA1922DFA9A8'
TMP_CHARACTERISTICS_UUID = 'E95D9250251D470AA062FA1922DFA9A8'
'''Microbit用初期化処理'''


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

    '''Microbit用初期化処理（Microbit②)'''
    # Microbit接続有無
    MB_enable = shared_obj.b1g_p0_Microbit_enable.value
    # 接続設定
    peripheral = Peripheral(MAC_ADDRESS, ADDR_TYPE_RANDOM)
    # 加速度センサー
    acc_service = peripheral.getServiceByUUID(ACC_SERVICE_UUID)
    acc_characteristic = peripheral.getCharacteristics(uuid=ACC_CHARACTERISTICS_UUID)
    # ボタン状態
    btn_service = peripheral.getServiceByUUID(BTN_SERVICE_UUID)
    btn_A_characteristic = peripheral.getCharacteristics(uuid=BTN_A_CHARACTERISTICS_UUID)
    btn_B_characteristic = peripheral.getCharacteristics(uuid=BTN_B_CHARACTERISTICS_UUID)
    '''Microbit用初期化処理'''
 
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

		#共用変数へ書き込み
        shared_obj.f4g_p1_joyAxisFB.value = js_input_bf
        shared_obj.f4g_p1_joyAxisLR.value = js_input_lr
        shared_obj.b1g_p0_Stop.value = STOP_FLAG
        '''joystick用ループ処理'''

        '''Microbit用ループ処理(Microbit③)'''
        if MB_enable == True:
            # 値の読み取り
            acc_read_data = acc_characteristic[0].read()
            btna_read_data =btn_A_characteristic[0].read()
            btnb_read_data =btn_B_characteristic[0].read()

            # 加速度センサー
            x = int.from_bytes(acc_read_data[0:2], byteorder='little', signed=True)
            y = int.from_bytes(acc_read_data[2:4], byteorder='little', signed=True)
            z = int.from_bytes(acc_read_data[4:6], byteorder='little', signed=True)

            # 加速度の表示
            print(f"ACCELEROMETER - x:{int(x/10)}, y:{y/10}, z:{z/10}")

            # ボタン状態の表示
            print(f"btn A:{btna_read_data[0]}")
            print(f"btn B:{btnb_read_data[0]}")


        '''Microbit用ループ処理'''


        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"


        #★★必要に応じて待ち時間を設定
        time.sleep(0.1)

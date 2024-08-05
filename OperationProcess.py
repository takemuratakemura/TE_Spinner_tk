#操作/表示系(プロセス1)記載用pyファイル
import time
from common.State import State
from bluepy.btle import DefaultDelegate, Peripheral,ADDR_TYPE_RANDOM
from common.SharedObject import SharedObject

#コントローラ入力取得
import pygame
import socket

#コントローラ種別
JOYSTICK = 0
PSCONTROLLER = 1
MICROBIT = 2

'''Microbit初期設定'''
# MicrobitのMAC
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
'''Microbit初期設定ここまで'''

#SharedObjectのインスタンスを定義
so = SharedObject()

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

    #コントローラ種別
    i4_ctr_type = shared_obj.i4g_p0_CTRtype.value

    # 初期接続処理
    match i4_ctr_type:
#        case 0: #JOYSTICK:
        case 1: #PSCONTROLLER:
            '''PSコントローラの接続前設定'''
            M_SIZE = 32
            locaddr = ('0.0.0.0', 9998)
            sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
            sock.settimeout(0.01)
            print('create socket')

            sock.bind(locaddr)

            ##受信確認
            message, cli_addr = sock.recvfrom(M_SIZE)

        case 2: #MICROBIT:
            # 接続設定
            peripheral = Peripheral(MAC_ADDRESS, ADDR_TYPE_RANDOM)
            # - 加速度センサー
            acc_service = peripheral.getServiceByUUID(ACC_SERVICE_UUID)
            acc_characteristic = peripheral.getCharacteristics(uuid=ACC_CHARACTERISTICS_UUID)
            # - ボタン
            btn_service = peripheral.getServiceByUUID(BTN_SERVICE_UUID)
            btn_A_characteristic = peripheral.getCharacteristics(uuid=BTN_A_CHARACTERISTICS_UUID)
            btn_B_characteristic = peripheral.getCharacteristics(uuid=BTN_B_CHARACTERISTICS_UUID)
            # - 温度センサー
            tmp_service = peripheral.getServiceByUUID(TMP_SERVICE_UUID)
            tmp_characteristic = peripheral.getCharacteristics(uuid=TMP_CHARACTERISTICS_UUID)
        case _:
            print("invalid controller")
    
    #操作/表示系用プロセスのメインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #コントローラからデータを取得
        match i4_ctr_type:
#            case 0: #JOYSTICK:
            case 1: #PSCONTROLLER:
                STOP_FLAG = val0_loacl[1]
                if STOP_FLAG == True:
                    sock.close()
                    time.sleep(1)
                    break
                    
                trq_bf = val1_loacl[0]*Max_Torque
                pos_lr = int(val1_loacl[1]*Pos_Range)


            case 2: #MICROBIT:
                '''Microbitデータ読み出し'''
                acc_read_data  = acc_characteristic[0].read()
                btnA_read_data = btn_A_characteristic[0].read()
                btnB_read_data = btn_B_characteristic[0].read()
                tmp_read_data  = tmp_characteristic[0].read()

                # 加速度
                axis_x = int.from_bytes(acc_read_data[0:2], byteorder='little', signed=True)
                axis_y = int.from_bytes(acc_read_data[2:4], byteorder='little', signed=True)
                axis_z = int.from_bytes(acc_read_data[4:6], byteorder='little', signed=True)
                '''Microbit読み出しここまで'''
            case _:
                print("invalid controller")
            
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state

        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        match i4_ctr_type:
#            case 0: #JOYSTICK:
#            case 1: #PSCONTROLLER:
            case 2: #MICROBIT:
                shared_obj.f4g_p1_joyAxisLR.value = axis_x #横方向をグローバルに書き込み
                shared_obj.f4g_p1_joyAxisFB.value = axis_y #縦方向をグローバルに書き込み
                shared_obj.u1g_p1_Pkb.value = btnB_read_data #PKB状態を書き込み

            case _:
                print("invalid controller")


        #★★必要に応じて待ち時間を設定
        time.sleep(1)

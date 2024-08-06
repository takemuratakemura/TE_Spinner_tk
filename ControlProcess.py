#駆動/重心制御(プロセス2)記載用pyファイル
import time
import socket
import numpy as np
from common.State import State
from common.SharedObject import SharedObject
from struct import pack, unpack
JOYSTICK = 0
PSCONTROLLER = 1
MICROBIT = 2

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
    #★★プロセス開始時の初期設定(ローカル変数/定数の設定)や初期化処理を記述
    '''■■■横軸と縦軸の現在〜過去値'''
    f4_x     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #横方向の値 0番目が生値相当 10回平均
    f4_y     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #縦方向の値 0番目が生値相当 10回平均
    f4_speed = [0, 0, 0, 0, 0] #車速 0番目が生値相当 5回平均
    i4_state = [0, 0] #車両状態 0番目が現在値、1番目が前回値 ※想定外の状態遷移防止
    '''■■■ここまで'''

    #コントローラ種別
    i4_ctr_type = shared_obj.i4g_p0_CTRtype.value
    
    '''■■■PoC流用'''
    i = 0
    dummy= 0
    p1_time_max = 0
    Max_Torque = 450.0
    Min_Torque = -Max_Torque
    Torque_UpperLimit = Max_Torque
    Torque_LowerLimit = -Torque_UpperLimit
    Max_Velo = 200.0 #rps
    Velo_Tor = 50.0 #最大車速超過許容
    Pos_Range = 100 #mm

    # 初期接続処理
    M_SIZE = 32
    locaddr = ('0.0.0.0', 9998)
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(0.01)
    '''■■■PoC流用ここまで'''

    #コントローラの接続はOperationProcessへ
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    communication_counter=0
    
    ##受信確認
    message, cli_addr = sock.recvfrom(M_SIZE)

    #駆動関係の通信初期設定
    '''■■■PoC流用'''
    ##モータ状態リセットを送信
    state_command = 0x06 #0x01 servo on, 0x02 stop, 0x04 reset
    send_data = pack('<4sHHHHh', b'TRQT', dummy, communication_counter,  dummy, state_command ,0)
    sock.sendto(send_data,cli_addr)
    time.sleep(3)
    ##モータ状態リセット結果の確認
    #recv_data =
    ##モータ状態をサーボON
    state_command = 0x01 #0x01 servo on, 0x02 stop, 0x04 reset
    send_data = pack('<4sHHHHh', b'TRQT', dummy, communication_counter,  dummy, state_command ,0)
    sock.sendto(send_data,cli_addr)
    '''■■■PoC流用ここまで'''

    
    #駆動/重心制御用プロセスのメインループ
    while True:
        p1_start = time.time()
        try : 
            '''■■■グローバル変数からローカル変数へ値更新'''
            #車両状態取得（[0]今回値、[1]前回値） 0:IG_ON_MODE, 1:PARKING_MODE, 2:DRIVE_MODE, 3:FAIL_SAFE_MODE
            i4_state = input_raw_data(i4_state, shared_obj.__i4g_p0_state.value)

            #コントローラからの入力値を取得
            f4_x = input_raw_data(f4_x, shared_obj.f4g_p1_joyAxisLR.value) #横軸生値更新
            f4_y = input_raw_data(f4_y, shared_obj.f4g_p1_joyAxisFB.value) #縦軸生値更新
            f4_speed =  input_raw_data(f4_speed, shared_obj.f4g_p2_speed.value) #車速生値更新
            u1_Pkb = shared_obj.u1g_p1_Pkb.value #PKB取得
            f4_x_ave = np.average(f4_x) #配列分だけ単純平均
            '''■■■ここまで'''

            #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
            #【例】"ローカル変数" = shared_obj."共有変数".value
            state = shared_obj.state

            #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
            printState(state) #【例】

            #【暫定】入力チェック
            print(f4_x[0], f4_x_ave)
        
            '''■■■UDPの通信'''

            ###UDP受信
            
            #print("x",val1_loacl[0])
            # ★★↑
            # ★★↑
            # ★★↑
            #print("process2 -> cycle:{}, value0:{}, value1:{}, value2:{},".format(i, val0_loacl[0], val1_loacl[0], val3_loacl[0]))
            i = i + 1
            
            message, cli_addr = sock.recvfrom(M_SIZE)
            command, sender_sequence, Act_Velo, Act_Torque, state, mode,dummy_h,dummy_b  = unpack('<6sHlhHbhb', message)  
            
            
            Velo = float(Act_Velo) * 7.5 / 360 #cnt/sec -> rps
            
            #Torque_UpperLimit = min(max(0.0,Max_Torque*(1-(Velo-Max_Velo)/Velo_Tor)),Max_Torque)
            #Torque_LowerLimit = max(min(0.0,Min_Torque*(1+(Velo+Max_Velo)/Velo_Tor)),Min_Torque)
            if communication_counter < 65535:
                communication_counter = communication_counter+1
            else:
                communication_counter = 0
                
            torque = val1_loacl[0]*Max_Torque
            torque = int(torque)
            #torque =int(max(min(torque,Torque_UpperLimit),Torque_LowerLimit))
            
            state_command = 0x01 #Servo ON
            #if i % 20 == 0: 
            print("MorVelo:", Velo, "[rps] Torque_cmd:", torque, "[Nm]  Torque_act:", Act_Torque)

            send_data = pack('<4sHHhHh', b'TRQT', dummy, communication_counter,  pos_lr, state_command,torque)
            sock.sendto(send_data,cli_addr)
            '''■■■ここまで'''

            p1_end = time.time()
            p1_time = p1_end - p1_start
            p1_time_max = max(p1_time_max, p1_time)
            #print(p1_time_max)
            time.sleep(max(0.001,(0.05-p1_time)))

            #★★shared_obj定義の共有変数への書き込み
            #【例】shared_obj."共有変数".value = "ローカル変数"


        except KeyboardInterrupt:
            sock.close()
            break
            
        #★★必要に応じて待ち時間を設定
        time.sleep(0.01)

#0番目に生値を格納して過去値を1つずらす
def input_raw_data(arr, raw):
    new_arr = np.roll(arr, 1)
    new_arr[0] = raw
    return new_arr

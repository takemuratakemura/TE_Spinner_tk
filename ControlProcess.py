#駆動/重心制御(プロセス2)記載用pyファイル
import time
from common.State import State

'''UDP通信用ヘッダ(UDP①)'''
import socket
import time
from struct import pack, unpack
'''UDP通信用ヘッダ'''


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
    '''UDP通信用初期化処理(UDP②)'''
    M_SIZE = 32
    dummy = 0
    Max_Torque = 450.0 #Nm
    Pos_Range = 100 #mm
    locaddr = ('0.0.0.0', 9998)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.01)
    sock.bind(locaddr)
    communication_counter = 0

    #受信確認
    message, cli_addr = sock.recvfrom(M_SIZE)

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
    
    '''UDP通信用初期化処理'''
    
    #駆動/重心制御用プロセスのメインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state #__i4g_p0_stateはSharedObject.py内のstate関数経由で読み出すため「shared_obj.state」の記述で良く「.value」は付けない

        '''UDP通信用ループ処理(UDP③)'''
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
		
		#受信
        message, cli_addr = sock.recvfrom(M_SIZE)
        command, sender_sequence, Act_Velo, Act_Torque, state, mode, dummy_h, dummy_b = unpack('<6sHlhHbhb', message)
		
		#Torque_UpperLimit = min(max(0.0,Max_Torque*(1-(Velo-Max_Velo)/Velo_Tor)),Max_Torque)
        #Torque_LowerLimit = max(min(0.0,Min_Torque*(1+(Velo+Max_Velo)/Velo_Tor)),Min_Torque)
        if communication_counter < 65535:
            communication_counter = communication_counter+1
        else:
            communication_counter = 0

        Velo = float(Act_Velo) * 7.5 / 360 #cnt/sec -> rps

        state_command = 0x01 #Servo ON
        #if i % 20 == 0: 
        print("MorVelo:", Velo, "[rps] Torque_cmd:", torque, "[Nm]  Torque_act:", Act_Torque)


		#送信
        state_command = 0x01
        send_data = pack('<4sHHhHh', b'TRQT', 0, communication_counter, pos, state_command, torque)
        sock.sendto(send_data, cli_addr)
		
        '''UDP通信用ループ処理'''


        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"

        #★★必要に応じて待ち時間を設定
        #time.sleep(1)
        p1_end = time.time()
        p1_time = p1_end - p1_start
        p1_time_max = max(p1_time_max, p1_time)
        #print(p1_time_max)
        time.sleep(max(0.001,(0.05-p1_time)))

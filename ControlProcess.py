#駆動/重心制御(プロセス2)記載用pyファイル
import time
from common.State import State

'''UDP通信用ヘッダ(UDP①)'''
import socket
import time
from struct import pack, unpack
'''UDP通信用ヘッダ'''

# Python上でC言語の関数を使用できるようにするモジュールctypesのインポート
import ctypes										#◆◆◆◆◆重心制御

#ControlProcess内定数定義
MAX_FORWARD_SPEED 4.0 #[km/h]
MAX_BACKWARD_SPEED 1.0 #[km/h]

target_speed_map = {
    -100: MAX_BACKWARD_SPEED,
    -95: MAX_BACKWARD_SPEED,
    -5: 0,
    5: 0,
    95: MAX_FORWARD_SPEED,
    100: MAX_FORWARD_SPEED
}


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
    p1_time_max = 0
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
    
    p1_start = time.time()
    
    #駆動/重心制御用プロセスのメインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state #__i4g_p0_stateはSharedObject.py内のstate関数経由で読み出すため「shared_obj.state」の記述で良く「.value」は付けない
        Yaw = shared_obj.f4g_p1_EulerAngles_Yaw.value		#◆◆◆◆◆重心制御
        Pitch = shared_obj.f4g_p1_EulerAngles_Pitch.value	#◆◆◆◆◆重心制御
        Roll = shared_obj.f4g_p1_EulerAngles_Roll.value		#◆◆◆◆◆重心制御
        Accl_x = shared_obj.f4g_p1_Acceleration_x.value		#◆◆◆◆◆重心制御
        Accl_y = shared_obj.f4g_p1_Acceleration_y.value		#◆◆◆◆◆重心制御
        Accl_z = shared_obj.f4g_p1_Acceleration_z.value		#◆◆◆◆◆重心制御
        Gyro_x = shared_obj.f4g_p1_AngularVelocity_x.value	#◆◆◆◆◆重心制御
        Gyro_y = shared_obj.f4g_p1_AngularVelocity_y.value	#◆◆◆◆◆重心制御
        Gyro_z = shared_obj.f4g_p1_AngularVelocity_z.value	#◆◆◆◆◆重心制御

        '''UDP通信用ループ処理(UDP③)'''
		#コントローラからの入力（global経由）
        js_bf_local = shared_obj.f4g_p1_joyAxisFB.value #ジョイスティックの前後操作量
        js_lr_local = shared_obj.f4g_p1_joyAxisLR.value #ジョイスティックの左右操作量
        js_stp_local = shared_obj.i4g_p1_ComStop.value  #外部からの通信停止信号
        
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
        Speed_mm_s = (Velo * 4200 / 368.9) # - (Gyro_x * 250)		#★★★速度算出
        Speed_km_h = Speed_mm_s * 3600 / 1000000				#★★★速度算出

        #ジョイスティックの傾きにより目標車速を決定する
        #ジョイスティックは[-100, +100]の範囲で動く
        #[-100, -95] 使わない
        #[-95, -5] 0 - MAX_BACKWARD_SPEEDの範囲
        #[-5, 5] 使わない
        #[5, 95] 0 - MAX_FORWARD_SPEEDの範囲
        #[95, 100] 使わない
        

        state_command = 0x01 #Servo ON
        #if i % 20 == 0:
        print("MotVelo:", Velo, "[rps] Torque_cmd:", torque, "[Nm]  Torque_act:", Act_Torque)
        #print("Speed:", Speed_mm_s, "[mm/s] ,", Speed_km_h, "[km/h]")

		#送信
        state_command = 0x01
        send_data = pack('<4sHHhHh', b'TRQT', 0, communication_counter, pos, state_command, torque)
        sock.sendto(send_data, cli_addr)
		
        '''UDP通信用ループ処理'''


        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        #printState(state) #【例】
        #print("p2:EulerAngles -> ({}, {}, {})".format(Yaw, Pitch, Roll))	#◆◆◆◆◆重心制御
        #print("p2:Accl        -> ({}, {}, {})".format(Accl_x, Accl_y, Accl_z))	#◆◆◆◆◆重心制御
        #print("p2:Gyro        -> ({}, {}, {})".format(Gyro_x, Gyro_y, Gyro_z))	#◆◆◆◆◆重心制御
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"

        #★★必要に応じて待ち時間を設定
        #time.sleep(1)
        p1_end = time.time()
        p1_time = p1_end - p1_start
        p1_time_max = max(p1_time_max, p1_time)
        #print(p1_time_max)
        time.sleep(max(0.001,(0.05-p1_time)))


#変数valueに対してmapで定義された点を線形補間する
#範囲の外側は最小値または最大値が入る
def linear_interpolation(target_map, value):
    """
    Performs linear interpolation based on a set of points.
    If the value is outside the range, it returns the min or max value.

    Parameters:
    points (dict): A dictionary where the keys are the input points and the values are the corresponding output points.
    value (float): The input value to interpolate.

    Returns:
    float: The interpolated output value.
    """
    # ソートされたリストに変換
    sorted_points = sorted(target_map.items())

    # 入力値が範囲外の場合、最小値または最大値を返す
    if value <= sorted_points[0][0]:
        return sorted_points[0][1]
    elif value >= sorted_points[-1][0]:
        return sorted_points[-1][1]

    # 2つの近い点を探す
    for i in range(len(sorted_points) - 1):
        x1, y1 = sorted_points[i]
        x2, y2 = sorted_points[i + 1]

        if x1 <= value <= x2:
            # 線形補間の計算
            t = (value - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)

    # ここには到達しないはず
    return None


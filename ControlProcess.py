#駆動/重心制御(プロセス2)記載用pyファイル
import time
import numpy as np
from common.State import State
from common.SharedObject import SharedObject

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

'''
'''
#駆動/重心制御用としてプロセス化される関数 ※process2=controlProcessのメイン関数にあたる
def worker(shared_obj):
    #★★プロセス開始時の初期設定(ローカル変数/定数の設定)や初期化処理を記述
    f4_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #横方向の値 0番目が生値相当
    f4_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #縦方向の値 0番目が生値相当

    #駆動/重心制御用プロセスのメインループ
    while True:
        #コントローラからの入力値を取得
        f4_x = input_raw_data(f4_x, shared_obj.f4g_p1_joyAxisLR.value) #横軸生値
        f4_y = input_raw_data(f4_y, shared_obj.f4g_p1_joyAxisFB.value) #縦軸生値
        u1_PKB = shared_obj.u1g_p1_PKB.value
        f4_x_ave = np.average(f4_x)

        #【暫定】Microbitから入力を取得する
        #print('x=', shared_obj.f4g_p1_joyAxisLR.value, ', y=', shared_obj.f4g_p1_joyAxisFB.value, ', PKB=', shared_obj.u1g_p1_PKB.value)
        print(f4_x[0], f4_x_ave)
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state

        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"


        #★★必要に応じて待ち時間を設定
        time.sleep(0.01)

#0番目に生値を格納して過去値を1つずらす
def input_raw_data(arr, raw):
    new_arr = np.roll(arr, 1)
    new_arr[0] = raw
    return new_arr

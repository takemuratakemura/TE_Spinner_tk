#操作/表示系(プロセス1)記載用pyファイル
import time
from common.State import State
'''joystick用初期化処理(joystick①)'''
import pygame

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


        #★★計算や処理 ※worker関数外に別関数を定義して呼び出す記載にしても良い
        printState(state) #【例】
        
        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"


        #★★必要に応じて待ち時間を設定
        time.sleep(0.1)

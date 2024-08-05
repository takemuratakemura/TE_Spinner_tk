import multiprocessing
import time
import asyncio
import ControlProcess
import OperationProcess
from common.SharedObject import SharedObject
from common.State import State
from MainProcessPackage.GPIOAssistant import GPIOAssistant
from MainProcessPackage.TCPClient import TCPClient
import struct

#FIFO処理モジュールのインポート
import queue
#コントローラ入力取得
import pygame
import socket

#コントローラ種別
JOYSTICK = 0
PSCONTROLLER = 1
MICROBIT = 2


def updateState(shared_obj, currentIsStandbySW, currentIsDriveSW, previousIsStandbySW, previousIsDriveSW):
    currentState = shared_obj.state

    if currentState == State.FAIL_SAFE_MODE:
        pass    #FAIL_SAFE_MODEの時は他のモードには遷移させない
    else:
        if (currentState == State.IG_ON_MODE):
            if currentIsStandbySW and not(previousIsStandbySW):
                shared_obj.state = State.PARKING_MODE
        elif (currentState == State.PARKING_MODE) or (currentState == State.DRIVE_MODE): 
            if currentIsDriveSW and not(previousIsDriveSW):
                shared_obj.state = State.DRIVE_MODE
            elif not(currentIsDriveSW) and (previousIsDriveSW):
                shared_obj.state = State.PARKING_MODE
            else:
                pass
        else:
            pass    #ありえない遷移のため無視

#■operationProcessへ定義が正しい？
def recvEvent(sender,buffer):
    tuplenum = struct.unpack("ii", buffer)
    shared_obj.f4g_p1_joyAxisLR.value = tuplenum[0]
    shared_obj.f4g_p1_joyAxisFB.value = tuplenum[1]

#取得した現stateを表示する関数例
def printState(state):
    if state == State.IG_ON_MODE:
        print('p0:Current State is IG_ON_MODE')
    elif state == State.PARKING_MODE:
        print('p0:Current State is PARKING_MODE')
    elif state == State.DRIVE_MODE:
        print('p0:Current State is DRIVE_MODE')
    else:
        print('p0:Current State is FAIL_SAFE_MODE')

async def main():
    #プロセス初期化
    operationProcess = multiprocessing.Process(target=OperationProcess.worker, args=(shared_obj,)) #process1※操作/表示系用プロセス
    controlProcess = multiprocessing.Process(target=ControlProcess.worker, args=(shared_obj,)) #process2※駆動/重心制御用プロセス

    #プロセス開始
    operationProcess.start() #process1※操作/表示系用プロセス
    controlProcess.start() #process2※駆動/重心制御用プロセス

    #GPIO初期化
    """
    StandbySwIO = GPIOAssistant(7)
    DriveSwIO = GPIOAssistant(8)
    previousIsStandbySW = StandbySwIO.isInput()
    previousIsDriveSW = DriveSwIO.isInput()
    """
    previousIsStandbySW = 0 #DRIVE_MODE設定のための仮入力
    previousIsDriveSW = 0 #DRIVE_MODE設定のための仮入力
    
    #TCP通信初期化
    """
    loop = asyncio.get_event_loop() 
    client = TCPClient(loop, recvEvent)
    client_task = loop.create_task(client.run())
    """

    #CAN通信初期化(バッテリ残量取得用IO)
    #(TODO)CAN通信初期化処理実装

    STOP_FLAG = False #socketを閉じる前の書き込み状況確認フラグ
    p0_time_max = 0   #周期

    #コントローラ種別
    i4_ctr_type = shared_obj.i4g_p0_CTRtype.value
    
    #★★★OperationProcessに移植可能か検討すること！
    match i4_ctr_type:
#        case 0: #JOYSTICK:
        case 1: #PSCONTROLLER:
            #コントローラ入力用のキュー
            ctrl_input_x = queue.Queue()
            ctrl_input_y = queue.Queue()
            ctrl_input_strt = [0,0]
            ctrl_input_curve = [0,0]

            # pygame初期化
            pygame.init()
            # joystickオブジェクトを作成
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

#        case 2: #MICROBIT:
        case _:
            print("invalid controller")
            
            
    #メインループ
    while True:
        p0_start = time.time() #現在時刻を取得

        #★★★OperationProcessに移植可能か検討すること！
        # コントローラ入力の取得
        match i4_ctr_type:
#            case 0: #JOYSTICK:
            case 1: #PSCONTROLLER:
                if pygame.event.get():
                    # Aボタンが押されたら終了
                    if joystick.get_button(0):
                        print('stop!')
                        STOP_FLAG = True
                        #break
                    else:
                        #ジョイスティックの操作を読み取る
                        js_input_lr = joystick.get_axis(0) #左のジョイスティックの左右方向
                        #print(js_input_lr)
                        js_input_bf = joystick.get_axis(4) #右のジョイスティックの上下方向
                        #print(js_input_bf)
#            case 2: #MICROBIT:
            case _:
                print("invalid controller")


        #状態更新
        """
        currentIsStandbySW = StandbySwIO.isInput()
        currentIsDriveSW = DriveSwIO.isInput()
        """
        currentIsStandbySW = 1 #DRIVE_MODE設定のための仮入力
        currentIsDriveSW = 1 #DRIVE_MODE設定のための仮入力
        updateState(shared_obj, currentIsStandbySW, currentIsDriveSW, previousIsStandbySW, previousIsDriveSW)
        previousIsStandbySW = currentIsStandbySW
        #previousIsDriveSW = currentIsDriveSW #DRIVE_MODE設定のためのコメント化

        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = shared_obj.state


        #★★計算や処理
        printState(state) #【例】
        
        #TCP通信
        #await client.send()

        #CAN通信
        #(TODO)CAN通信処理実装

        #異常チェック
        #(TODO)異常チェック実装


        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        match i4_ctr_type:
#            case 0: #JOYSTICK:
            case 1: #PSCONTROLLER:
                shared_obj.f4g_p1_joyAxisLR = js_input_lr #ジョイスティックの左右操作量
                shared_obj.f4g_p1_joyAxisFB = js_input_bf #ジョイスティックの前後操作量
                shared_obj.b1g_p0_Stop = STOP_FLAG

#            case 2: #MICROBIT:
            case _:
                print("invalid controller")

        #★★必要に応じて待ち時間を設定
        #await asyncio.sleep(1)
        p0_end = time.time()
        p0_time = p0_end - p0_start
        p0_time_max = max(p0_time_max, p0_time)
        time.sleep(max(0.001,(0.05-p0_time)))
        #print(p0_time)

'''
共有変数定義
メインプロセス実行
'''
if __name__ == "__main__":
    shared_obj = SharedObject()
    asyncio.run(main())

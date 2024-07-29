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

'''
関数名: updateState
shared_obj:
currentIsStandbySW: 
currentIsDriveSW: 
previousIsStandbySW: 
previousIsDriveSW: 
'''
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
    各SWの入力だったりスタンバイスイッチだったりを受け付ける
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

    '''
    グローバルからローカルに共有変数を落とし込む
    計算処理を行う
    必要なものはローカルからグローバルに書き込む
    '''

    #メインループ
    while True:
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


        #★★必要に応じて待ち時間を設定
        await asyncio.sleep(1)


'''
共有変数定義
メインプロセス実行
'''
if __name__ == "__main__":
    shared_obj = SharedObject()
    asyncio.run(main())

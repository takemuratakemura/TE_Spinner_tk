import multiprocessing
import asyncio
import ControlProcess
import OperationProcess
from common.SharedObject import SharedObject
from common.State import State
from MainProcessPackage.StateControl import StateControl
from MainProcessPackage.TCPClient import TCPClient
from MainProcessPackage.MoniteringComRecvObject import MoniteringComRecvObject
import json
import atexit

#TCPClientがデータを受信したときに実行されるCallback
def recvEvent(sender,buffer):
    global moniteringComWDT
    moniteringComWDT = 0
    stringData = buffer.decode('ascii')
    #print(stringData)
    dictData = json.loads(stringData)
    recvObject.update(dictData)
    
    
def exitEvent():
    StateControl.clearnup()

async def main():
    #強制終了時のイベントハンドラを指定
    atexit.register(exitEvent)
    
    #プロセス初期化
    operationProcess = multiprocessing.Process(target=OperationProcess.worker, args=(shared_obj,)) #process1※操作/表示系用プロセス
    controlProcess = multiprocessing.Process(target=ControlProcess.worker, args=(shared_obj,)) #process2※駆動/重心制御用プロセス

    #プロセス開始
    operationProcess.start() #process1※操作/表示系用プロセス
    controlProcess.start() #process2※駆動/重心制御用プロセス

    #状態制御クラス初期化
    StateControl.init(shared_obj.state)
    
    #TCP通信クラス初期化
    loop = asyncio.get_event_loop() 
    client = TCPClient(loop, recvEvent, "192.168.11.6", 55555)
    loop.create_task(client.run())
    await asyncio.sleep(1)

    #CAN通信初期化(バッテリ残量取得用IO)
    #(TODO)CAN通信初期化処理実装

    #メインループ
    while True:
        #★★shared_obj定義の共有変数からローカル変数への値読み出し※計算に使用するものなど必要なものを読み出す
        #【例】"ローカル変数" = shared_obj."共有変数".value
        state = State(StateControl.state)
        values = shared_obj.getAllValues()
        isControlProcessError = shared_obj.i4g_p2_isControlProcessError.value
        isOperationProcessError = shared_obj.i4g_p1_isOperationProcessError.value
        
        #★★計算や処理
        print("p0:Current State is",state.name)
        #状態更新
        global moniteringComWDT
        isError = bool(recvObject.isEmergencyStopSW) or bool(isControlProcessError) or bool(isOperationProcessError) or (moniteringComWDT > 30)
        StateControl.updateState(state, recvObject.isStandbySW, isError)
        #moniteringComWDT+= 1
        
        #TCP通信
        client.send(json.dumps(values, ensure_ascii=False, indent=4).encode('ascii'))

        #CAN通信
        #(TODO)CAN通信処理実装

        #★★shared_obj定義の共有変数への書き込み
        #【例】shared_obj."共有変数".value = "ローカル変数"
        shared_obj.state = StateControl.state

        #★★必要に応じて待ち時間を設定
        await asyncio.sleep(1)

if __name__ == "__main__":
    shared_obj = SharedObject()
    recvObject = MoniteringComRecvObject()
    moniteringComWDT = 0
    moniteringComWDT_PLC = 0

    asyncio.run(main())


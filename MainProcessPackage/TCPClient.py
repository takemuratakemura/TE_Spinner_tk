import asyncio, socket
import sys

class TCPClient:
        def __init__(self,loop, recvEvent, distIpAddress='127.0.0.1', distPort=55555):
                self._loop = loop                                 #カレントスレッドのイベントループを取得
                self._distIpAddress = distIpAddress
                self._distPort = distPort
                self._initSocket()
                self._recvEvent = recvEvent

        def _initSocket(self):
                self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._client.setblocking(False)

        async def _connect(self):
            while True:
                try:
                    await self._loop.sock_connect(self._client,(self._distIpAddress,self._distPort))    # Client ソケット
                    break
                except Exception as e:
                        print("_connect() fail.", e)
                        await asyncio.sleep(5)
                        if sys.platform != "win32":
                            if e.errno == 106:
                                self._initSocket()
                        else:
                            if e.errno == 10056:
                                self._initSocket()


        async def _recv_forever(self):
            try:
                while  data := await self._loop.sock_recv(self._client, 1024):                          #データ受信するまでカレントスレッドの処理を開放し待機。データ受信後、カレントスレッドが空いたタイミングで移行の処理が実行される
                    self._recvEvent(self, data)
            except Exception as e:
                    print("_recv_forever fail.", e)
                    if sys.platform != "win32":
                        if e.errno == 106:
                            self._initSocket()
                    else:
                        if e.errno == 10056:
                            self._initSocket()

        async def send(self):
            print("Client Send")
            try:
                await self._loop .sock_sendall(self._client , b"Cliet Send")
            except:
                print('Connection Error')

        async def run(self):
            while True:
                try:
                    await self._connect()
                    await self._recv_forever()    #データ受信用の処理を登録。カレントスレッドが空いたタイミングで実行される
                    
                except Exception as e:
                    print(e)
                    await asyncio.sleep(1)


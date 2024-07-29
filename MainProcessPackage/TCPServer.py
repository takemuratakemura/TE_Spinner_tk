import asyncio, socket
import struct

class TCPServer:
        def __init__(self,loop,ip='localhost',port=55555):
                self._loop = loop                                 #カレントスレッドのイベントループを取得
                self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      #TCPソケット
                self._server.setblocking(False)
                self._server.bind((ip, port))

                self._client :socket = None
                self._cnt = 0

        async def _listen(self):
                self._server.listen()                                             #clientからの接続要求待機状態
                self._client, address = await self._loop.sock_accept(self._server)            #clientから接続要求があるまで待機
                self._client.setblocking(False)

        async def _recv_forever(self):
            try:
                while  data := await self._loop.sock_recv(self._client, 1024):                   #データ受信するまでカレントスレッドの処理を開放し待機。データ受信後、カレントスレッドが空いたタイミングで移行の処理が実行される
                    print("Server Received:", data.decode())
            except Exception as e:
                    print(e)

        async def send(self):
            print("Server Send")
            try:
                self._cnt = self._cnt + 1
                binary_data = struct.pack("ii", self._cnt, self._cnt*2)
                await self._loop .sock_sendall(self._client, binary_data)
            except:
                print('Connection Error')

        async def run(self):
            while True:
                try:
                    await self._listen()
                    await self._recv_forever()    #データ受信用の処理を登録。カレントスレッドが空いたタイミングで実行される
                    
                except Exception as e:
                    print(e)
                    await asyncio.sleep(1)


                



async def main():
    loop = asyncio.get_event_loop() 

    server = TCPServer(loop)
    server_task = loop.create_task(server.run())

    while True:
        await asyncio.sleep(1)
        await server.send()


if __name__ == "__main__":
    asyncio.run(main())
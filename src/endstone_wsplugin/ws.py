import websockets
import asyncio
import json

class WebSocketServer:
    def __init__(self):
        self._connected = None  # 1つのクライアント接続を保持

    async def handler(self, websocket):
        if self._connected is not None:  # 既存の接続があれば切断
            await self._connected.close()
            
        self._connected = websocket  # 新しいクライアント接続を保存

        try:
            async for message in websocket:  # メッセージを受信するループ
                await self.onmessage(message)
        except websockets.exceptions.ConnectionClosed:
            print('[WS] Closed by client.')
        finally:
            self._connected = None  # 接続解除

    async def onmessage(self, message):
        data = json.loads(message)  # 受信したJSONをパース
        # await self.sendToMC(data)
    
    async def sendToClient(self,message):
        if self._connected is not None:
             self._connected.send(message)

    def start(self):
        server = websockets.serve(self.handler, "localhost", 8765)  # サーバー起動
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    server = WebSocketServer()
    server.start()

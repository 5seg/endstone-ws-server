from endstone.event import (
    PlayerChatEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
    event_handler,
)
from endstone.plugin import Plugin
from endstone_wsplugin.listener import BasicListener
import threading
import asyncio
import websockets
import json
import base64


class WSPlugin(Plugin):
    prefix = "WSServerPlugin"
    api_version = "0.11"
    websocket = None  # WebSocketの接続を保持するための変数

    async def echo(self, websocket):
        self.websocket = websocket  # 接続を保持
        print("クライアントが接続しました")
        try:
            async for message in websocket:
                if message == "0":
                    websocket.send("1")
                else:
                    print(f"[WS] Recv: {message}")
                    # メッセージをサーバーのチャットに送信
                    self.server.broadcast_message(f"[Discord] {message}")
        except websockets.exceptions.ConnectionClosed:
            print("クライアントとの接続が閉じられました")

    def on_enable(self) -> None:
        self.logger.info("on_enable is called!")
        self.register_events(self)
        self.register_events(BasicListener(self))

        # 別スレッドで asyncio イベントループを回して WebSocket サーバーを起動
        t = threading.Thread(target=self._start_ws_loop_thread, daemon=True)
        t.start()

    def _start_ws_loop_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # start_websocket_server は async 関数なのでタスクとして起動
        loop.create_task(self.start_websocket_server())
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def start_websocket_server(self):
        # 0.0.0.0:8765 で待ち受け（パス引数は websockets v11 以降で異なるので環境に合わせて修正）
        server = await websockets.serve(self.echo, "0.0.0.0", 8765)
        self.logger.info("WebSocketサーバーが起動しました")
        await server.wait_closed()

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        player = event.player
        message = event.message

        # プレイヤーのチャットメッセージをログ表示
        self.logger.info(f"{player.name}: {message}")

        # メッセージをWebSocketに送信
        data = {"event": "chat", "player": {"name": player.name}, "message": message}
        asyncio.run(self.send_message_to_websocket(json.dumps(data)))

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        player = event.player
        data = {"event": "join", "player": {"name": player.name, "xuid": player.xuid}}
        asyncio.run(self.send_message_to_websocket(json.dumps(data)))

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        player = event.player
        data = {"event": "join", "player": {"name": player.name, "xuid": player.xuid}}
        asyncio.run(self.send_message_to_websocket(json.dumps(data)))

    async def send_message_to_websocket(self, message: str):
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except Exception as e:
                self.logger.error(f"WebSocketへの送信エラー: {e}")

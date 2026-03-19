from endstone.event import ServerLoadEvent, PlayerChatEvent, event_handler
from endstone.plugin import Plugin
from endstone_wsplugin.listener import BasicListener
import asyncio
import websockets

class WSPlugin(Plugin):
    prefix = "WSServerPlugin"
    api_version = "0.11"
    websocket = None  # WebSocketの接続を保持するための変数

    def on_load(self) -> None:
        self.logger.info("on_load is called!")

    def on_enable(self) -> None:
        self.logger.info("on_enable is called!")
        self.register_events(self)
        self.register_events(BasicListener(self))
        #self.server.scheduler.run_task(self, self.log_time, delay=0, period=20 * 1) #type:ignore

        # WebSocketサーバーを起動
        asyncio.run(self.start_websocket_server())

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")

    async def echo(self, websocket):
        self.websocket = websocket  # 接続を保持
        print("クライアントが接続しました")
        try:
            async for message in websocket:
                print(f"[WS] Recv: {message}")
                # メッセージをサーバーのチャットに送信
                self.server.broadcast_message(f"[WS] {message}")
        except websockets.exceptions.ConnectionClosed:
            print("クライアントとの接続が閉じられました")

    async def start_websocket_server(self):
        async with websockets.serve(self.echo, "0.0.0.0", 8765):
            print("WebSocketサーバーが起動しました")
            await asyncio.Future()  # 永久に待機

    @event_handler
    def on_server_load(self, event: ServerLoadEvent):
        self.logger.info(f"{event.event_name} is passed to on_server_load")

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        player = event.player
        message = event.message

        # プレイヤーのチャットメッセージをログ表示
        self.logger.info(f"{player.name}: {message}")

        # メッセージをWebSocketに送信
        asyncio.run(self.send_message_to_websocket(f"{player.name}: {message}"))

    async def send_message_to_websocket(self, message: str):
        if self.websocket is not None:
            try:
                await self.websocket.send(message)
            except Exception as e:
                self.logger.error(f"WebSocketへの送信エラー: {e}")

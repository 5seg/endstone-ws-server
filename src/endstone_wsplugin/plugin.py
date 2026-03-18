from endstone.event import ServerLoadEvent, event_handler
from endstone.plugin import Plugin

from endstone_wsplugin.listener import BasicListener

class WSPlugin(Plugin):
    prefix = "WSServerPlugin"
    api_version = "0.1"
    # load = "POSTWORLD" idk is this needed

    def on_load(self) -> None:
        self.logger.info("on_load is called!")

    def on_enable(self) -> None:
        self.logger.info("on_enable is called!")
        self.register_events(self)  # register event listeners defined directly in Plugin class
        self.register_events(BasicListener(self))  # you can also register event listeners in a separate class

        self.server.scheduler.run_task(self, self.log_time, delay=0, period=20 * 1) # type: ignore  # every second

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")

    @event_handler
    def on_server_load(self, event: ServerLoadEvent):
        self.logger.info(f"{event.event_name} is passed to on_server_load")

from time import localtime
from typing import Union, Dict

from mcdreforged.api.all import *

from wish_message import message
from .message import get_wish_message, get_wish_day


def register_command(server: PluginServerInterface):
    def give_wish_message(source: CommandSource):
        new_time = []
        for i in localtime()[0:3]:
            new_time.append(f"§a{str(i)}§6")
        wish_message: Union[Dict[str, str], None] = \
            get_wish_message(get_wish_day(server))
        day_message = server.rtr("wish_message.date").to_plain_text() % tuple(new_time)
        if wish_message is None:
            no_festival = server.rtr("wish_message.no_festival").to_plain_text()
            player_message = f"{day_message}\n{no_festival}"
        else:
            festival = server.rtr("wish_message.festival").to_plain_text() \
                       % (wish_message["day"], wish_message["message"])
            player_message = f"§6{day_message}\n{festival}"
        source.reply(player_message)

    server.register_command(
        Literal("!!wish").runs(give_wish_message)
    )


def on_load(server: PluginServerInterface, old):
    server.logger.info(server.tr("wish_message.on_load"))
    server.register_help_message("!!wish", server.tr("wish_message.help"))
    get_wish_day(server)
    register_command(server)

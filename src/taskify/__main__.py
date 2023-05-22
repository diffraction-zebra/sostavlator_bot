from .secrets import TelegramSecrets
from .handlers import BotApp
from pyrogram import Client
from pyrogram import enums
import os
from .models import (
    db,
    User,
    TaskList,
    Task
)


if __name__ == "__main__":
    app = Client(
        "taskify",
        api_id=TelegramSecrets().api_id,
        api_hash=TelegramSecrets().api_hash,
        bot_token=TelegramSecrets().bot_token,
        workdir=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../data'
        )
    )
    app.set_parse_mode(enums.ParseMode.MARKDOWN)
    bot_app = BotApp(app, db)
    bot_app.app.run()

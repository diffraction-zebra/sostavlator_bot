import pyrogram.filters
from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler
from .secrets import TelegramSecrets
from .config import TelegramConfig
from peewee import SqliteDatabase
from .models import User, TaskList, Task
from .utils import format_datetime, create_datetime, get_or_create_user
import os
import typing as tp
import uuid
import lucidity


class BotApp:
    app: Client
    db: SqliteDatabase

    @staticmethod
    def __generate_task_lists_keyboard(task_lists: tp.Iterable,
                                       user_uid: str,
                                       back_callback: str) -> tuple[InlineKeyboardMarkup, str]:
        keyboard_list = []
        for task_list in task_lists:
            if (user_uid not in [user.uid for user in task_list.collaborators]) and \
                    (task_list.owner.uid != user_uid):
                continue

            prefix = "📌" if task_list.is_noting else ""
            prefix += "🔗" if task_list.owner.uid != user_uid else ""
            prefix += " "
            keyboard_list.append(
                [InlineKeyboardButton(
                    prefix + task_list.title,
                    callback_data=f"redraw:task_list:{task_list.uid} show_task_lists"
                )]
            )
        keyboard_list.append(
            [InlineKeyboardButton(
                "📝 New task list",
                switch_inline_query_current_chat=TelegramConfig().add_task_list_template.format(
                    task_list_title="",
                    task_list_is_noting="n"
                )
            )]
        )

        keyboard_list.append(
            [InlineKeyboardButton(
                "🔙",
                callback_data=back_callback
            )]
        )
        return InlineKeyboardMarkup(keyboard_list), TelegramConfig().task_lists_text

    @staticmethod
    def __generate_tasks_keyboard(task_list: tp.Iterable,
                                  user_uid: str,
                                  back_callback: str,
                                  task_list_ref: TaskList = None
                                  ) -> tuple[InlineKeyboardMarkup, str]:
        keyboard_list = []
        if task_list_ref is not None:
            keyboard_list.append(
                [InlineKeyboardButton(
                    "🔗 Add collaborator",
                    switch_inline_query_current_chat=TelegramConfig().add_collaborator_template.format(
                        task_list_uid=task_list_ref.uid,
                        col_uid=""
                    )
                )]
            )
        for task in task_list:
            if (task_list_ref is not None) and (task.task_list != task_list_ref):
                continue

            if (user_uid not in [user.uid for user in task.task_list.collaborators]) \
                    and (task.task_list.owner.uid != user_uid):
                continue

            if task.is_completed and (not task.task_list.is_noting):
                continue

            prefix = "🔗" if task.creator.uid != user_uid else ""
            prefix += " "
            prefix += "❗" * task.priority if task.priority > 0 else ""

            backref_postfix = f"redraw:task_list:{task_list_ref.uid}" if task_list_ref else "redraw:show_all_tasks"
            keyboard_list.append(
                [
                    InlineKeyboardButton(
                        prefix + task.title,
                        callback_data=f"redraw:task:{task.uid}:show_all_tasks {backref_postfix}"
                    ),
                    InlineKeyboardButton(
                        "✅" if task.is_completed else "☑️",
                        callback_data=f"redraw:task_complete:{task.uid} {backref_postfix}"
                    )
                ]
            )
        if task_list_ref is not None:
            keyboard_list.append(
                [InlineKeyboardButton(
                    "📝 Add task",
                    switch_inline_query_current_chat=TelegramConfig().add_task_template.format(
                        task_list_uid=task_list_ref.uid,
                        task_uid="-",
                        task_title="",
                        task_due_date="-",
                        task_category="",
                        task_priority="",
                        task_description=""
                    )
                )]
            )
        keyboard_list.append(
            [InlineKeyboardButton(
                "🔙",
                callback_data=back_callback
            )]
        )

        out_text = TelegramConfig().task_list_text.format(
            task_list_title=task_list_ref.title
        ) if task_list_ref is not None else TelegramConfig().all_tasks_text
        return InlineKeyboardMarkup(keyboard_list), out_text

    @staticmethod
    def __generate_menu_keyboard() -> tuple[InlineKeyboardMarkup, str]:
        keyboard_list = [
            [InlineKeyboardButton(
                "📝 All tasks",
                callback_data="redraw:show_all_tasks"
            )],
            [InlineKeyboardButton(
                "📌 Task lists",
                callback_data="redraw:show_task_lists"
            )]
        ]
        return InlineKeyboardMarkup(keyboard_list), TelegramConfig().menu_text

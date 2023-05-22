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
    
    @staticmethod
    def __generate_task_layout(task: Task, back_callback: str) -> tp.Iterable:
        backref_postfix = back_callback
        keyboard_list = [
            [InlineKeyboardButton(
                "Mark as completed" if not task.is_completed else "Mark as uncompleted",
                callback_data=f"redraw:task_complete:{task.uid} {backref_postfix}"
            )],
            [
                InlineKeyboardButton(
                    "🔙",
                    callback_data=f"{back_callback} {backref_postfix}"
                ),
                InlineKeyboardButton(
                    "📝 Edit",
                    switch_inline_query_current_chat=TelegramConfig().add_task_template.format(
                        task_list_uid=task.task_list.uid,
                        task_uid=task.uid,
                        task_title=task.title,
                        task_due_date=format_datetime(task.due_date,
                                                      TelegramConfig().time_template)
                        if task.due_date is not None else "-",
                        task_category=task.category,
                        task_priority=task.priority,
                        task_description=task.description
                    )
                ),
                InlineKeyboardButton(
                    "🗑️ Delete",
                    callback_data=f"delete_task:{task.uid}"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard_list), TelegramConfig().task_text.format(
            task_title=task.title,
            task_due_time=(
                format_datetime(task.due_date,
                                TelegramConfig().time_template) if task.due_date is not None else "Unlimited"
            ),
            task_category=task.category,
            task_priority=("!" * task.priority if task.priority > 0 else "-"),
            task_description=task.description
        )

    def redraw_handler(self, client, callback_query):
        user = User.get(User.uid == callback_query.from_user.id)
        callback_meta_args = callback_query.data.split()
        callback_args = callback_meta_args[0].split(":")

        text = None
        new_keyboard = None

        if callback_args[1] == "task_complete":
            task = Task.get(Task.uid == callback_args[2])
            task.is_completed = not task.is_completed
            task.save()
            callback_query.answer(
                text="Task marked as completed" if task.is_completed else "Task marked as uncompleted",
                show_alert=False
            )

            new_pseudo_callback = callback_meta_args[1]
            callback_meta_args = new_pseudo_callback.split()
            callback_args = callback_meta_args[0].split(":")

        if callback_args[1] == "menu":
            new_keyboard, text = self.__generate_menu_keyboard()
        elif callback_args[1] == "show_task_lists":
            tasklist_iterator = TaskList.select()  # Вынужденный костыль из-за недоработки Peewee
            new_keyboard, text = self.__generate_task_lists_keyboard(
                tasklist_iterator,
                user.uid,
                "redraw:menu"
            )
        elif callback_args[1] == "show_all_tasks":
            tasks_iterator = Task.select()  # Вынужденный костыль из-за недоработки Peewee
            new_keyboard, text = self.__generate_tasks_keyboard(
                tasks_iterator,
                user.uid,
                "redraw:menu"
            )
        elif callback_args[1] == "task":
            task = Task.get(Task.uid == callback_args[2])
            new_keyboard, text = self.__generate_task_layout(
                task,
                callback_meta_args[1]
            )
        elif callback_args[1] == "task_list":
            task_list = TaskList.get(TaskList.uid == callback_args[2])
            new_keyboard, text = self.__generate_tasks_keyboard(
                task_list.tasks,
                user.uid,
                "redraw:show_task_lists",
                task_list
            )

        callback_query.edit_message_text(
            text=text,
            reply_markup=new_keyboard
        )

    def start_handler(self, client, message: Message):
        message.reply_text(
            f"Hello, {message.from_user.first_name}! I'm Taskify bot.\n"
            f"Here you can create your own task lists and tasks.\n\n"
            f"Here is your personal ID: `{message.from_user.id}`\n"
        )

    def menu_handler(self, client, message: Message):
        user = get_or_create_user(str(message.from_user.id))
        keyboard, text = self.__generate_menu_keyboard()

        self.app.send_message(
            message.from_user.id,
            text,
            reply_markup=keyboard
        )

    def cmd_handler(self, client, message: Message):
        user = get_or_create_user(str(message.from_user.id))
        command_args = message.text.split(" ")
        query = " ".join(command_args[1:])
        command = command_args[1]

        if (not message.via_bot) and (not message.forward_from):
            return

        print(command + " | ", query)

        if command == "add_collaborator":
            query_data = TelegramConfig().add_collaborator_parse_template.parse(query)

            col_user = User.get_or_none(User.uid == query_data["col_uid"])

            task_list = TaskList.get_or_none(TaskList.uid == query_data["task_list_uid"])

            task_list.collaborators.add(col_user)
            task_list.save()

            message.reply_text("User added as a collaborator")
        if command == "add_or_modify_task":
            query_data = TelegramConfig().add_task_parse_template.parse(query)

            task_list = TaskList.get_or_none(TaskList.uid == query_data["task_list_uid"])

            is_creating = query_data["task_uid"] == '-'

            if is_creating:
                task = Task.create(
                    uid=str(uuid.uuid4())[-6:],
                    title=query_data["task_title"],
                    due_date=create_datetime(query_data["task_due_date"],
                                             TelegramConfig().time_template)
                    if query_data["task_due_date"] != "-" else None,
                    category=query_data["task_category"],
                    priority=int(query_data["task_priority"]),
                    description=query_data["task_description"],
                    task_list=task_list,
                    creator=user
                )
            else:
                task = Task.get_or_none(Task.uid == query_data["task_uid"])
                task.title = query_data["task_title"]
                task.due_date = create_datetime(query_data["task_due_date"],
                                                TelegramConfig().time_template) if query_data[
                                                                                       "task_due_date"] != "-" else None
                task.category = query_data["task_category"]
                task.priority = int(query_data["task_priority"])
                task.description = query_data["task_description"]
                task.save()

            message.reply_text("Task added or modified")
        if command == "add_task_list":
            query_data = TelegramConfig().add_task_list_parse_template.parse(query)

            task_list = TaskList.create(
                uid=str(uuid.uuid4())[-6:],
                title=query_data["task_list_title"],
                is_noting=query_data["task_list_is_noting"] == "y",
                owner=user
            )

            message.reply_text("Task list added")
        print(command)

    def inline_query_handler(self, client, inline_query: InlineQuery):
        user = User.get(User.uid == inline_query.from_user.id)
        query = inline_query.query

        query_args = query.split()
        print(query_args)
        if query_args[0] == "add_collaborator":
            add_collaborator_parse_template = TelegramConfig().add_collaborator_parse_template
            answer_text = ""
            title_text = ""
            correctness_flag = True
            try:
                query_data = add_collaborator_parse_template.parse(query)

            except lucidity.error.ParseError:
                title_text = "Form is not filled"
                answer_text = "Just continue typing"
                correctness_flag = False
            else:
                answer_text = str(query_data)
                col_user = User.get_or_none(User.uid == query_data["col_uid"])
                task_list = TaskList.get_or_none(TaskList.uid == query_data["task_list_uid"])
                if task_list is None:
                    correctness_flag = False
                    title_text = "Task list not found"
                    answer_text = "Task list with this id is not registered in the system"

                if correctness_flag and col_user is None:
                    correctness_flag = False
                    title_text = "User not found"
                    answer_text = "User with this id is not registered in the system"

                if correctness_flag and col_user == user:
                    correctness_flag = False
                    title_text = "You can't add yourself"
                    answer_text = "You can't add yourself as a collaborator"

                if correctness_flag and col_user in task_list.collaborators:
                    correctness_flag = False
                    title_text = "User already added"
                    answer_text = "This user is already added to this task list"

                if correctness_flag:
                    title_text = "Add collaborator"
                    answer_text = "Tap here to confirm adding collaborator"

            input_message = InputTextMessageContent("/cmd " + query if correctness_flag else query)
            inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        title=title_text,
                        description=answer_text,
                        input_message_content=input_message,
                    )
                ],
                cache_time=1
            )
        if query_args[0] == "add_or_modify_task":
            add_task_parse_template = TelegramConfig().add_task_parse_template
            answer_text = ""
            title_text = ""
            correctness_flag = True
            answers_list = []
            try:
                query_data = add_task_parse_template.parse(query)

            except lucidity.error.ParseError:
                answers_list.append(
                    {
                        "title_text": "Form is not filled",
                        "answer_text": "Just continue typing"
                    }
                )

                correctness_flag = False
            else:
                answer_text = str(query_data)
                task_list = TaskList.get_or_none(TaskList.uid == query_data["task_list_uid"])
                if task_list is None:
                    correctness_flag = False
                    answers_list.append(
                        {
                            "title_text": "Task list not found",
                            "answer_text": "Task list with this id is not registered in the system"
                        }
                    )

                if correctness_flag and task_list.owner != user and (not (user in task_list.collaborators)):
                    correctness_flag = False
                    answers_list.append(
                        {
                            "title_text": "Access denied",
                            "answer_text": "You are not owner of this task list"
                        }
                    )

                if correctness_flag and (not query_data["task_priority"].isnumeric()):
                    correctness_flag = False
                    answers_list.append(
                        {
                            "title_text": "Priority format is wrong",
                            "answer_text": "You should type priority as a number from 0 to 4"
                        }
                    )

                if correctness_flag:
                    if query_data["task_due_date"] == '-':
                        due_date = None
                    else:
                        try:
                            due_date = create_datetime(query_data["task_due_date"], TelegramConfig().time_template)
                        except ValueError:
                            correctness_flag = False
                            answers_list.append(
                                {
                                    "title_text": "Due date format is wrong",
                                    "answer_text": "You should type due date like HH:MM dd.mm.YYYY"
                                }
                            )

                if correctness_flag:
                    answers_list = [
                        {
                            "title_text": "Title",
                            "answer_text": query_data["task_title"]
                        },
                        {
                            "title_text": "Due date",
                            "answer_text": format_datetime(due_date,
                                                           TelegramConfig().time_template)
                            if due_date is not None else "Unlimited"
                        },
                        {
                            "title_text": "Category",
                            "answer_text": query_data["task_category"]
                        },
                        {
                            "title_text": "Priority",
                            "answer_text": "❗" * int(query_data["task_priority"])
                        },
                        {
                            "title_text": "Description",
                            "answer_text": query_data["task_description"]
                        },
                        {
                            "title_text": "Add task",
                            "answer_text": "Tap here to confirm adding task"
                        }
                    ]

            input_message = InputTextMessageContent("/cmd " + query if correctness_flag else query)
            results_list = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4())[-6:],
                    title=answer["title_text"],
                    description=answer["answer_text"],
                    input_message_content=input_message
                ) for answer in answers_list
            ]
            inline_query.answer(
                results=results_list,
                cache_time=1
            )
        if query_args[0] == "add_task_list":
            add_task_list_parse_template = TelegramConfig().add_task_list_parse_template
            answer_text = ""
            title_text = ""
            correctness_flag = True
            try:
                query_data = add_task_list_parse_template.parse(query)

            except lucidity.error.ParseError:
                correctness_flag = False
                title_text = "Form is not filled"
                answer_text = "Just continue typing"

            if correctness_flag:
                title_text = "Add task list"
                answer_text = f"Tap here to confirm adding task list {query_data['task_list_title']}"

            input_message = InputTextMessageContent("/cmd " + query if correctness_flag else query)
            inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        title=title_text,
                        description=answer_text,
                        input_message_content=input_message,
                    )
                ],
                cache_time=1
            )

    def add_all_handlers(self):
        self.app.add_handler(MessageHandler(self.start_handler, filters.command(["start"])))
        self.app.add_handler(MessageHandler(self.menu_handler, filters.command(["menu"])))
        self.app.add_handler(MessageHandler(self.cmd_handler, filters.command(["cmd"])))

        self.app.add_handler(CallbackQueryHandler(
            self.redraw_handler,
            filters=pyrogram.filters.regex(r"^redraw:.*")
        ))

        self.app.add_handler(InlineQueryHandler(self.inline_query_handler))

    def __init__(self, app: Client, db: SqliteDatabase):
        self.db = db
        self.app = app

        self.add_all_handlers()

        if User().get_or_none(User.uid == "316490607") is None:
            user = User.create(uid="316490607")
            task_list = TaskList.create(
                uid="1",
                title="Example task list",
                owner=user,
                is_noting=True,
            )
            Task.create(
                uid="2",
                title="Example task",
                task_list=task_list,
                creator=user,
            )

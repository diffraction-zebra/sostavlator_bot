from pydantic import BaseSettings
import lucidity


class TelegramConfig(BaseSettings):
    task_text: str = "**{task_title}**\n\n" \
                     "Due: ``{task_due_time}``\n\n" \
                     "Category: {task_category}\n" \
                     "Priority: {task_priority}\n\n" \
                     "{task_description}"
    menu_text: str = "Menu"
    task_list_text: str = "**{task_list_title}**"
    all_tasks_text: str = "All tasks"
    task_lists_text: str = "Your task lists"

    add_collaborator_template: str = "add_collaborator <{task_list_uid}>\n" \
                                     "👤 Enter user's Telegram uid: <{col_uid}>"
    add_collaborator_parse_template = lucidity.Template('model', add_collaborator_template,
                                                        default_placeholder_expression='[^/]+')

    add_task_template: str = "add_or_modify_task <{task_list_uid}> <{task_uid}>\n" \
                             "📝 Enter task title: <{task_title}>" \
                             "\n\n📅 Enter due date (Example: 04:20 09.11.2001) or -: <{task_due_date}>" \
                             "\n\n📌 Enter category: <{task_category}>" \
                             "\n\n🔥 Enter priority (0-4): <{task_priority}>" \
                             "\n\n📝 Enter description: <{task_description}>"
    add_task_parse_template = lucidity.Template('model', add_task_template, default_placeholder_expression='[^/]+')

    add_task_list_template: str = "add_task_list \n" \
                                  "📝 Enter task list title: <{task_list_title}>\n" \
                                  "Is this task list for noting? (y/n): <{task_list_is_noting}>"
    add_task_list_parse_template = lucidity.Template('model', add_task_list_template,
                                                     default_placeholder_expression='[^/]+')

    time_template: str = "%H:%M %d.%m.%Y"

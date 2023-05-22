from peewee import *
import os

db = SqliteDatabase(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../../data/taskify.db'
    )
)


class User(Model):
    uid = CharField(primary_key=True)

    class Meta:
        database = db


class TaskList(Model):
    uid = CharField(primary_key=True)
    title = CharField()
    owner = ForeignKeyField(User, backref='task_lists')
    collaborators = ManyToManyField(User, backref='shared_task_lists')
    is_noting = BooleanField(default=False)

    class Meta:
        database = db


class Task(Model):
    uid = CharField(primary_key=True)
    title = CharField()
    description = TextField(null=True)
    category = CharField(null=True)
    priority = IntegerField(default=0)
    is_completed = BooleanField(default=False)
    due_date = DateTimeField(null=True)
    task_list = ForeignKeyField(TaskList, backref='tasks')
    creator = ForeignKeyField(User, backref='created_tasks')

    class Meta:
        database = db


db.create_tables([
    User,
    TaskList,
    Task,
    TaskList.collaborators.get_through_model()]
)

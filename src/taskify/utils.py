from .models import User
from datetime import datetime


def get_or_create_user(uid: str) -> User:
    try:
        return User.get(User.uid == uid)
    except User.DoesNotExist:
        return User.create(uid=uid)


def format_datetime(dtime: datetime, template: str):
    return datetime.strftime(dtime, template)


def create_datetime(dtime_string: str, template: str):
    return datetime.strptime(dtime_string, template)

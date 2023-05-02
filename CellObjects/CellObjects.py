from datetime import datetime
#from datetime import time
from enum import Enum


def to_time(string: str):
    return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


class MarkCell:
    def __init__(self, period: float = 0, calls_number: int = 0, action: str = "",
                 edited: datetime = datetime.now().replace(microsecond=0),
                 status: bool = False):
        self.__period = period
        self.__calls_number = calls_number
        self.__action = action
        self.__edited = edited
        self.__status = status

    def get_period(self) -> float:
        return self.__period

    def get_calls_number(self) -> float:
        return self.__calls_number

    def get_action(self) -> str:
        return self.__action

    def get_edited(self) -> datetime:
        return self.__edited

    def get_status(self) -> bool:
        return self.__status

    def set_period(self, new_period: float = 0):
        self.__period = new_period
        return self

    def set_calls_number(self, new_calls_number: int = 0):
        self.__calls_number = new_calls_number
        return self

    def set_action(self, new_action: str = ""):
        self.__action = new_action
        return self

    def set_edited(self, new_edited: str = datetime.now()):
        self.__edited = to_time(new_edited)
        return self

    def set_status(self, new_status: bool = False):
        if self.__status is True and new_status is False:
            calls = self.__calls_number
            interval = (datetime.now() - self.__edited).total_seconds() / 3600
            self.__period = (calls * self.__period + interval) / (calls + 1)
            self.__edited = datetime.now().replace(microsecond=0)
            self.__calls_number += 1
        self.__status = new_status
        return self

    def to_list(self) -> list:
        return list(vars(self).values())

    def __str__(self) -> str:
        return str(list(vars(self).values()))

    def __iter__(self) -> iter:
        return iter(vars(self))


class CheckMarkCell(MarkCell):
    def __init__(self, period: float = 0, calls_number: int = 0, action: str = "",
                 edited: datetime = datetime.now().replace(microsecond=0),
                 status: bool = False, params_list: list = None):
        if params_list is None:
            super().__init__(period=period, calls_number=calls_number, action=action, edited=edited, status=status)
        else:
            super().__init__(float(params_list[0]), int(params_list[1]), action=params_list[2],
                             edited=to_time(params_list[3]),
                             status=True if params_list[4] == 'True' else False)

    def copy(self):
        return CheckMarkCell(*vars(self).values())


class Category(Enum):
    NONE = 0
    STUDY = 1
    SPORT = 2
    WORK = 3
    HOME = 4


class Importance(Enum):
    NONE = 0
    MIDDLE = 1
    HIGH = 2
    VERY_HIGH = 3


class TimeCell(MarkCell):
    def __init__(self, hintable=True, scheduled: datetime = datetime.now().replace(microsecond=0), category: Category = Category.STUDY,
                 importance: Importance = Importance.NONE, period: float = 0, calls_number: int = 0, action: str = "",
                 edited: datetime = datetime.now().replace(microsecond=0),
                 status: bool = False, params_list: list = None):
        if params_list is None:
            self.__hintable = hintable
            self.__scheduled = scheduled
            self.__category = category
            self.__importance = importance
            super().__init__(period=period, calls_number=calls_number, action=action, edited=edited, status=status)
        else:
            self.__hintable = True if params_list[0] == 'True' else False
            self.__scheduled = to_time(params_list[1])
            self.__category = eval(params_list[2])
            self.__importance = eval(params_list[3])
            super().__init__(float(params_list[4]), int(params_list[5]), action=params_list[6],
                             edited=to_time(params_list[7]),
                             status=True if params_list[8] == 'True' else False)

    def get_hintable(self) -> bool:
        return self.__hintable

    def get_scheduled(self) -> datetime:
        return self.__scheduled

    def get_day(self) -> int:
        return self.__scheduled.day

    def get_category(self) -> Category:
        return self.__category

    def get_importance(self) -> Importance:
        return self.__importance

    def set_hintable(self, new_hintable: bool = True):
        self.__hintable = new_hintable

    def set_scheduled(self, new_scheduled: str = datetime.now()):
        self.__scheduled = to_time(new_scheduled)
        return self

    def set_category(self, new_category: Category = Category.STUDY):
        self.__category = new_category
        return self

    def set_importance(self, new_importance: Importance = Importance.NONE):
        self.__importance = new_importance
        return self

    def get_path(self) -> str:
        return str(self.get_scheduled().year) + '/' + str(self.get_scheduled().month) + '/' + str(
            self.get_scheduled().day) + '.csv'

    def get_ymd_act(self) -> tuple:
        return self.get_scheduled().year, self.get_scheduled().month, self.get_scheduled().day, self.get_action()

    def get_ymd(self) -> tuple:
        return self.get_scheduled().year, self.get_scheduled().month, self.get_scheduled().day

    def copy(self):
        return TimeCell(*vars(self).values())

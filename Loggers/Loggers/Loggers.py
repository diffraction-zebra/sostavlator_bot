import datetime
import itertools
import os
import shutil
from datetime import datetime
from datetime import date

from CellObjects.CellObjects import Category
from CellObjects.CellObjects import CheckMarkCell
from CellObjects.CellObjects import Importance
from CellObjects.CellObjects import TimeCell
from Loggers.Readers.Readers import CSVReader
from Loggers.Readers.Readers import PickleReader


def note_path(username: str = 'oshalesha', note_name: str = ""):
    return '__data/' + username + '/__check_marks/' + note_name + '.csv'


def get_path(username: str = 'oshalesha', file_name: str = ""):
    return '__data/' + username + '/' + file_name


def get_dir(username: str = 'oshalesha', dir_name: str = ""):
    return '__data/' + username + '/' + dir_name


def get_regular_path(username: str = 'oshalesha', day: int = 0):
    return '__data/' + username + '/__time/__weekdays/' + str(day) + '.csv'


def to_check_mark(yanked):
    return [CheckMarkCell(params_list=row) for row in yanked]


def to_time_mark(yanked):
    return [TimeCell(params_list=row) for row in yanked]


class NotesManager:
    def __init__(self, username: str = 'oshalesha'):
        self.__username = username
        self.__file_name = get_path(username, '__notes.csv')
        self.__reader = CSVReader(self.__file_name)

    def __get_list(self) -> list:
        return self.__reader.read()

    def get_list(self) -> list:
        return list(itertools.chain.from_iterable(self.__reader.read()))

    def __exists(self, name: str = ""):
        got = self.__get_list()
        for pos in range(len(got)):
            if got[pos] == [name]:
                return pos
        return None

    def remove(self, name: str = ""):
        got = self.__get_list()
        index = self.__exists(name=name)
        del got[index]
        self.__reader.write_list(records=got)
        os.remove(note_path(self.__username, note_name=name))

    def add(self, name: str = ""):
        got = self.__get_list()
        if self.__exists(name=name) is None:
            got.append([name])
            self.__reader.write_list(records=got)
            CSVReader(file_name=note_path(name))

    def clear(self):
        self.__reader.write_list([])
        shutil.rmtree(get_dir(self.__username, '__check_marks'))


class CheckMarkLogger:
    def __init__(self, username: str = 'oshalesha', note_name: str = ""):
        self.__file_name = get_path(username, '__check_marks/' + note_name + '.csv')
        self.__reader = CSVReader(file_name=self.__file_name)
        notes_manager = NotesManager(username)
        notes_manager.add(note_name)

    def get_file_name(self) -> str:
        return self.__file_name

    def __get_as_lists(self) -> list:
        return self.__reader.read()

    def get(self) -> list:
        return to_check_mark(self.__get_as_lists())

    def __get_tuple(self, name: str) -> tuple:
        got = self.__get_as_lists()
        pos = None
        for pos in range(len(got)):
            if CheckMarkCell(params_list=got[pos]).get_action() == name:
                break
        return pos, got

    def __get(self, name: str) -> CheckMarkCell:
        got = self.get()
        for item in got:
            if item.get_action() == name:
                return item

    def exists(self, name: str) -> bool:
        yanked = self.get()
        for item in yanked:
            if item.get_action() == name:
                return True
        return False

    def remove(self, cell: CheckMarkCell):
        index, got = self.__get_tuple(name=cell.get_action())
        del got[index]
        self.__reader.write_list(records=got)

    def add(self, cell: CheckMarkCell):
        got = self.__get_as_lists()
        if not self.exists(name=cell.get_action()):
            got.append(cell.to_list())
            self.__reader.write_list(records=got)

    def clear(self):
        self.__reader.write_list([])

    def rename(self, old_name: str = "", new_name: str = ""):
        if self.exists(new_name) and self.exists(old_name) and new_name != old_name:
            raise "You cannot save it as an existing name."
        self.remove(CheckMarkCell(action=old_name))
        self.add(CheckMarkCell(action=new_name))

    def set_status(self, name: str = "", status=False):
        cell = self.__get(name)
        self.remove(cell=cell)
        cell.set_status(status)
        self.add(cell=cell)


class TimeLogger:
    def __init__(self, username: str = 'oshalesha'):
        self.__dir_name = get_dir(username, '__time')
        self.__username = username
        os.makedirs(self.__dir_name, exist_ok=True)

    def get_dir_name(self) -> str:
        return self.__dir_name

    def __get_dir_path(self, year: int = datetime.now().year, month: int = datetime.now().month) -> str:
        return self.get_dir_name() + '/' + str(year) + '/' + str(month) + '/'

    def __get_path_ymd(self, year: int = datetime.now().year, month: int = datetime.now().month, day: int = 1) -> str:
        return self.__get_dir_path(year, month) + str(day) + '.csv'

    def __get_path_cell(self, cell: TimeCell) -> str:
        return self.__get_path_ymd(cell.get_scheduled().year, cell.get_scheduled().month, cell.get_scheduled().day)

    def __get_as_lists(self, year: int = datetime.now().year, month: int = datetime.now().month,
                       day: int = datetime.now().day) -> list:
        reader = CSVReader(self.__get_path_ymd(year, month, day))
        return reader.read()

    def __get_tuple(self, year: int = datetime.now().year, month: int = datetime.now().month,
                    day: int = datetime.now().day, name: str = "") -> tuple:
        got = self.__get_as_lists(year, month, day)
        for pos in range(len(got)):
            if TimeCell(params_list=got[pos]).get_action() == name:
                return pos, got
        return None, None

    def __get(self, year: int = datetime.now().year, month: int = datetime.now().month, day: int = datetime.now().day,
              name: str = "") -> TimeCell:
        pos, got = self.__get_tuple(year, month, day, name)
        return TimeCell(params_list=got[pos])

    def get_for_day(self, year: int = datetime.now().year, month: int = datetime.now().month,
                    day: int = datetime.now().day) -> list:
        regular_logger = RegularLogger(self.__username)
        regular = regular_logger.get_for_day(date(year, month, day).weekday())
        for cell in regular:
            cell.set_scheduled(str(datetime.combine(date(year, month, day), cell.get_scheduled().time())))
            cell.set_hintable(False)
            self.add(cell)
        return to_time_mark(self.__get_as_lists(year, month, day))

    def exists(self, year: int = datetime.now().year, month: int = datetime.now().month, day: int = datetime.now().day,
               name: str = "") -> bool:
        pos, got = self.__get_tuple(year, month, day, name)
        return pos is not None

    def remove(self, cell: TimeCell):
        index, got = self.__get_tuple(*cell.get_ymd_act())
        removed = got[index]
        del got[index]
        reader = CSVReader(self.__get_path_cell(cell))
        reader.write_list(records=got)
        return removed

    def add(self, cell: TimeCell):
        got = self.__get_as_lists(*cell.get_ymd())
        if not self.exists(*cell.get_ymd_act()):
            OracleLogger(self.__username).update(cell.get_action())
            got.append(cell.to_list())
            reader = CSVReader(self.__get_path_cell(cell))
            reader.write_list(got)

    def rename(self, old_name: str = "", new_name: str = "", year: int = datetime.now().year,
               month: int = datetime.now().month,
               day: int = datetime.now().day):
        if self.exists(year, month, day, new_name) and self.exists(year, month, day, old_name) and new_name != old_name:
            raise "You cannot save it as an existing name."
        got = self.__get(year, month, day, old_name)
        self.remove(cell=got)
        got.set_action(new_name)
        self.add(cell=got)

    def set_status(self, name: str = "", year: int = datetime.now().year, month: int = datetime.now().month,
                   day: int = datetime.now().day,
                   status=False):
        cell = self.__get(year, month, day, name)
        self.remove(cell=cell)
        cell.set_status(status)
        self.add(cell=cell)

    def set_category(self, name: str = "", year: int = datetime.now().year, month: int = datetime.now().month,
                     day: int = datetime.now().day, new_category=Category.NONE):
        cell = self.__get(year, month, day, name)
        self.remove(cell=cell)
        cell.set_category(new_category=new_category)
        self.add(cell=cell)

    def set_importance(self, name: str = "", year: int = datetime.now().year, month: int = datetime.now().month,
                       day: int = datetime.now().day, new_importance=Importance.NONE):
        cell = self.__get(year, month, day, name)
        self.remove(cell=cell)
        cell.set_importance(new_importance=new_importance)
        self.add(cell=cell)

    def set_datetime(self, name: str = "", year: int = datetime.now().year, month: int = datetime.now().month,
                     day: int = datetime.now().day, new_datetime=datetime.now()):
        new_datetime.replace(microsecond=0)
        cell = self.__get(year, month, day, name)
        self.remove(cell=cell)
        cell.set_scheduled(new_scheduled=str(new_datetime))
        self.add(cell=cell)

    def clear(self):
        name = self.get_dir_name()
        for direct in os.listdir(name):
            for file in os.listdir(name + '/' + direct + '/'):
                os.remove(name + '/' + direct + '/' + file)


class OracleLogger:
    def __init__(self, username: str = 'oshalesha'):
        self.__file_name = get_path(username, '__oracle.pickle')
        self.__reader = PickleReader(self.__file_name)

    def get(self):
        return self.__reader.read()

    def get_five(self):
        got = self.get()
        return [k for k, v in sorted(got.items(), key=lambda item: item[1], reverse=True)][:min(len(got), 5)]

    def write(self, loaded: dict = None):
        self.__reader.write(loaded)

    def update(self, key: str = ""):
        loaded = self.get()
        loaded[key] = loaded.get(key, 0) + 1
        self.write(loaded)

    def empty(self) -> bool:
        got = self.get()
        return len(got) == 0


class PersonalLogger:  # use it only once
    def __init__(self, username: str = 'oshalesha'):
        self.__file_name = get_path(username, '__personal.pickle')
        self.__reader = PickleReader(self.__file_name)

    def write_features(self, sex: str = 'М', age: int = 19, free_time: float = 0.1, picked_movies: bool = True,
                       picked_reading: bool = False, picked_art: bool = True,
                       picked_studying: bool = True, picked_activities: bool = False, picked_sports: bool = True,
                       picked_work: bool = True):
        loaded = dict({'sex': sex, 'age': age, 'free_time': free_time, 'picked_movies': picked_movies,
                       'picked_reading': picked_reading, 'picked_art': picked_art,
                       'picked_studying': picked_studying, 'picked_activities': picked_activities,
                       'picked_sports': picked_sports, 'picked_work': picked_work})
        self.__reader.write(loaded)

    def write(self, loaded: dict = None):
        self.__reader.write(loaded)

    def get(self):
        return self.__reader.read()

    def empty(self) -> bool:
        got = self.get()
        return len(got) == 0

    def clear(self):
        self.write(loaded=dict())


class RegularLogger:
    def __init__(self, username: str = 'oshalesha'):
        self.__dir_name = get_dir(username, '__time/__weekdays')
        self.__username = username
        os.makedirs(self.__dir_name, exist_ok=True)

    def get_dir(self):
        return self.__dir_name

    def __get_as_lists(self, day: int = datetime.now().weekday()) -> list:
        reader = CSVReader(get_regular_path(self.__username, day))
        return reader.read()

    def __get_tuple(self, day: int = datetime.now().weekday(), name: str = "") -> tuple:
        got = self.__get_as_lists(day)
        for pos in range(len(got)):
            if TimeCell(params_list=got[pos]).get_action() == name:
                return pos, got
        return None, None

    def __get(self, day: int = datetime.now().weekday(), name: str = "") -> TimeCell:
        pos, got = self.__get_tuple(day, name)
        return TimeCell(params_list=got[pos])

    def __get_path_cell(self, cell: TimeCell) -> str:
        return get_regular_path(self.__username, cell.get_scheduled().weekday())

    def get_for_day(self, day: int = datetime.now().weekday()) -> list:
        return to_time_mark(self.__get_as_lists(day))

    def exists(self, day: int = datetime.now().weekday(), name: str = "") -> bool:
        pos, got = self.__get_tuple(day, name)
        return pos is not None

    def remove(self, cell: TimeCell):
        index, got = self.__get_tuple(cell.get_scheduled().weekday(), cell.get_action())
        removed = got[index]
        del got[index]
        reader = CSVReader(self.__get_path_cell(cell))
        reader.write_list(records=got)
        return removed

    def add(self, cell: TimeCell):
        got = self.__get_as_lists(cell.get_scheduled().weekday())
        if not self.exists(cell.get_scheduled().weekday(), cell.get_action()):
            got.append(cell.to_list())
            reader = CSVReader(self.__get_path_cell(cell))
            reader.write_list(got)

    def rename(self, old_name: str = "", new_name: str = "", day: int = datetime.now().weekday()):
        if self.exists(day, new_name) and self.exists(day, old_name) and new_name != old_name:
            raise "You cannot save it as an existing name."
        got = self.__get(day, old_name)
        self.remove(cell=got)
        got.set_action(new_name)
        self.add(cell=got)

    def set_status(self, name: str = "", day: int = datetime.now().weekday(), status=False):
        cell = self.__get(day, name)
        self.remove(cell=cell)
        cell.set_status(status)
        self.add(cell=cell)

    def set_category(self, name: str = "", day: int = datetime.now().weekday(), new_category=Category.NONE):
        cell = self.__get(day, name)
        self.remove(cell=cell)
        cell.set_category(new_category=new_category)
        self.add(cell=cell)

    def set_importance(self, name: str = "", day: int = datetime.now().weekday(), new_importance=Importance.NONE):
        cell = self.__get(day, name)
        self.remove(cell=cell)
        cell.set_importance(new_importance=new_importance)
        self.add(cell=cell)

    def set_datetime(self, name: str = "", day: int = datetime.now().weekday(), new_datetime=datetime.now()):
        new_datetime.replace(microsecond=0)
        cell = self.__get(day, name)
        self.remove(cell=cell)
        cell.set_scheduled(new_scheduled=str(new_datetime))
        self.add(cell=cell)

    def clear(self):
        shutil.rmtree(self.__dir_name)

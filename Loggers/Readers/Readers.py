import csv
import os
import pickle
from os import path


class CSVReader:
    def __init__(self, file_name: str = ""):
        self.__file_name = file_name
        os.makedirs(os.path.dirname(self.__file_name), exist_ok=True)
        if not path.exists(self.__file_name):
            with open(self.__file_name, 'x'):
                pass

    def read(self) -> list:
        with open(self.__file_name, mode='r') as f:
            yanked = list(csv.reader(f))
        return yanked

    def write(self, record: list):
        got = self.read()
        got.append(record)
        with open(self.__file_name, mode='w') as f:
            writer = csv.writer(f)
            writer.writerows(got)

    def write_list(self, records: list):
        with open(self.__file_name, mode='w') as f:
            writer = csv.writer(f)
            writer.writerows(records)


class PickleReader:
    def __init__(self, file_name: str = ""):
        self.__file_name = file_name
        os.makedirs(os.path.dirname(self.__file_name), exist_ok=True)
        if not os.path.exists(self.__file_name):
            with open(self.__file_name, mode='wb'):
                self.write(loaded=dict())

    def write(self, loaded: dict = None):
        with open(self.__file_name, 'wb') as f:
            pickle.dump(loaded, f)

    def read(self):
        with open(self.__file_name, 'rb') as f:
            loaded = pickle.load(f)
        return loaded

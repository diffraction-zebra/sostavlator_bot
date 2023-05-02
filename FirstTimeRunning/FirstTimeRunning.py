from os import path


class FirstTimeRunning:
    def __init__(self):
        self.__dir_name = '__data'

    def first_time_running(self):
        return not path.exists(self.__dir_name)

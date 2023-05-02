from datetime import datetime


class MultiTask:
    def __init__(self, action: str = "", edited: datetime = datetime.max.replace(microsecond=0),
                 collaborators: list = None,
                 done_by: str = ''):
        self.__action = action
        self.__edited = edited
        self.__collaborators = collaborators
        self.__done_by = done_by

    def get_action(self) -> str:
        return self.__action

    def get_edited(self) -> datetime:
        return self.__edited

    def get_collaborators(self) -> list:
        return self.__collaborators

    def get_done_by(self) -> str:
        return self.__done_by

    def get_status(self) -> bool:
        return self.__done_by != ''

    def set_action(self, new_action: str = ''):
        self.__action = new_action

    def set_edited(self, new_edited: datetime = datetime.now().replace(microsecond=0)):
        self.__edited = new_edited

    def set_collaborators(self, new_collaborators: list = None):
        self.__collaborators = new_collaborators

    def set_done_by(self, new_done_by):
        self.__done_by = new_done_by

from CellObjects.CellObjects import TimeCell
from Loggers.Loggers.Loggers import RegularLogger


def make_regular(cell: TimeCell, username: str = 'oshalesha'):
    regular = RegularLogger(username)
    regular.add(cell)

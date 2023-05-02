from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

from Loggers.Loggers.Loggers import CheckMarkLogger
from Loggers.Loggers.Loggers import OracleLogger
from Loggers.Loggers.Loggers import PersonalLogger


class CheckMarkOracle:
    def __init__(self, name: str):
        self.__logger = CheckMarkLogger(name)

    def predict(self) -> list:
        hint = []
        yanked = self.__logger.get()
        for pos in range(len(yanked)):
            if timedelta(days=yanked[pos].get_period()) + yanked[pos].get_date_time() < datetime.now():
                hint.append(yanked[pos])
        return sorted(yanked, key=lambda l: l.get_calls_number(), reverse=True)[:min(5, len(yanked))]


class Ganglion:
    def __init__(self):
        self.__data = pd.read_csv('Ganglion/data.csv')
        self.__category_features = ['sex', 'picked_movies',
                                    'picked_reading', 'picked_art', 'picked_studying', 'picked_activities',
                                    'picked_sports', 'picked_work']
        self.__real_features = ['age', 'free_time']
        self.__target_features = ['movies', 'reading', 'studying', 'activities', 'sports', 'work']
        self.__models = [LinearRegression(fit_intercept=True) for _ in range(6)]
        self.__encoder = OneHotEncoder(drop='first', sparse_output=False)
        self.__encoder.fit_transform(self.__data[self.__category_features])

    def think(self):
        train_cat = self.__encoder.transform(self.__data[self.__category_features])
        x_train = np.hstack([self.__data[self.__real_features], train_cat])
        for i in range(len(self.__target_features)):
            self.__models[i].fit(x_train, self.__data[self.__target_features[i]])

    def predict(self, data: dict = None):
        df = pd.DataFrame(data, index=[0])
        test_cat = self.__encoder.transform(df[self.__category_features])
        x_test = np.hstack([df[self.__real_features], test_cat])
        test_predictions = dict()
        for i in range(len(self.__target_features)):
            test_predictions[self.__target_features[i]] = self.__models[i].predict(x_test)[0]
        return test_predictions


class TimeOracle:
    def __init__(self):
        self.__logger = OracleLogger()
        self.__personal_logger = PersonalLogger()
        self.__ganglion = Ganglion()
        self.__ganglion.think()

    def predict(self) -> list:
        got = self.__logger.get_five()
        if len(got) < 5:
            predicted = self.__ganglion.predict(self.__personal_logger.get())
            if datetime.now().weekday() in [5, 6]:
                predicted.pop('work')
            predicted_list = [k for k, v in
                              sorted(predicted.items(), key=lambda item: item[1], reverse=True)[
                              :min(len(predicted), 5)]]
            return (got + predicted_list)[:min(len(got + predicted_list), 5)]
        return got

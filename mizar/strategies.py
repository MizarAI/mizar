from abc import ABC
from abc import abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    @property
    @abstractmethod
    def name(self):
        """strategy name"""
        pass

    @property
    @abstractmethod
    def description(self):
        """strategy description"""
        pass

    @abstractmethod
    def take_position(self, row):
        """accept a dataset and return a position"""
        pass


class Signal:
    def __init__(self, base_asset: str, quote_asset: str, exchange: str, bar_type):
        self._base_asset = base_asset
        self._quote_asset = quote_asset
        self._exchange = exchange
        self._bar_type = bar_type

    @property
    def input_columns(self):
        pass

    def transform(self, df: pd.DataFrame):
        df = df[self.input_columns]

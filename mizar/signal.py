from typing import Any
from typing import Callable
from typing import List

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin


class Signal(BaseEstimator, TransformerMixin):
    def __init__(
        self, min_n_bars: int, input_columns: List[Any], transformer: Callable
    ):
        self.min_n_bars = min_n_bars
        self.input_columns = input_columns
        self.transformer = transformer

    def _transform(self, X: pd.DataFrame):
        self.transform(X[self.input_columns])

    def transform(self, X: pd.DataFrame):
        return self.transformer.transform(X)


def signal_from_sklearn(sklearn_model: BaseEstimator):
    pass

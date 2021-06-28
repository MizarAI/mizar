import os
from typing import Dict

import pandas as pd

from mizar.api import Mizar


class MizarStudio:
    def __init__(self, mizar: Mizar, path: str = "./"):
        self.mizar = mizar
        self.path = path
        if path[-1] != "/":
            path = f"{path}/"

        if not os.path.isdir(path):
            os.makedirs(path)

    def get_bar_df(
        self,
        base_asset: str,
        quote_asset: str,
        start_timestamp: int = 0,
        bar_type: str = "time",
        bar_subclass: str = "D",
        exchange: str = "binance",
    ) -> pd.DataFrame:
        """
        :param base_asset: Base asset to select (e.g. BTC)
        :type base_asset: str
        :param quote_asset: Quote asset to select (e.g. USDT)
        :type quote_asset: str
        :param start_timestamp: The timestamp from which collect the bars
        :param exchange: exchange name
        :type exchange: str
        :param bar_type: bar type can be (e.g. tick, dollar, volume, time)
        :type bar_type: str
        :param bar_subclass: bar subclass specify the class of bar type
                             to select (e.g. 1min, 3min, dynamic etc..)
        :type bar_subclass: str
        :return: bar dataframe
        :rtype: pd.DataFrame
        """
        directory = f"{self.path}bar/{exchange}/{base_asset}{quote_asset}/{bar_type}"

        if os.path.isfile(f"{directory}/{bar_subclass}_bar_data.csv"):
            bars_df = pd.read_csv(f"{directory}/{bar_subclass}_bar_data.csv")
            timestamp = bars_df["time"].max()

        else:
            os.makedirs(f"{directory}/", exist_ok=True)
            bars_df = pd.DataFrame()
            timestamp = start_timestamp

        previous_size = -1

        while bars_df.shape[0] != previous_size:
            previous_size = bars_df.shape[0]

            response = self.mizar.get_bar_data(
                base_asset=base_asset.upper(),
                quote_asset=quote_asset.upper(),
                start_timestamp=timestamp,
                bar_type=bar_type,
                bar_subclass=bar_subclass,
                exchange=exchange,
            )

            if not response.get("bars"):
                continue

            bars_df = pd.concat([bars_df, pd.DataFrame(response["bars"])], axis=0)

            bars_df.drop_duplicates(
                inplace=True, ignore_index=True, subset=["first_trade_id"]
            )
            timestamp = bars_df["time"].max()
        bars_df.sort_values(by="time", inplace=True)
        bars_df.to_csv(f"{directory}/{bar_subclass}_bar_data.csv", index=False)
        bars_df.set_index(
            pd.to_datetime(bars_df["time"], unit="ms"), inplace=True, drop=True
        )
        bars_df.set_index(bars_df.index.tz_localize(None), inplace=True, drop=True)
        bars_df.drop("time", axis=1, inplace=True)
        return bars_df

    def save_strategy(
        self,
        strategy,
        strategy_file_path: str,
        data_sources: Dict[str, Dict[str, str]],
        strategy_name: str,
        strategy_description: str,
    ):

        with open(
            strategy_file_path,
        ) as r:
            strategy_file = r.read()

        strategy_info = {
            "strategy_signal_name": strategy_name,
            "target_data_source": strategy.strategy_pipeline.align_on_,
            "num_expiration_bars": strategy.num_expiration_bars,
            "data_sources": data_sources,
            "description": strategy_description,
            "trailing_take_profit_deviation": strategy.trailing_take_profit_deviation,
            "trailing_stop_loss_deviation": strategy.trailing_stop_loss_deviation,
            "stop_loss_tick_level": strategy.stop_loss_tick_level,
            "take_profit_tick_level": strategy.take_profit_tick_level,
        }

        self.mizar.save_strategy(
            strategy=strategy, strategy_file=strategy_file, strategy_info=strategy_info
        )

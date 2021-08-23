import json
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import dill as pickle
import requests

MAXIMUM_STRATEGY_SIZE = 200
MAXIMUM_STRATEGY_FILE = 2


class MizarAPIException(Exception):
    pass


class MizarRequestException(Exception):
    pass


class StrategySizeExceededLimit(Exception):
    def __init__(self, strategy_model_size: float, maximum_strategy_model_size: float):
        message = f"Maximum size of {maximum_strategy_model_size}MB exceeded. Strategy model size is {strategy_model_size}MB."
        super().__init__(message)


class StrategyFileSizeExceededLimit(Exception):
    def __init__(self, strategy_file_size: float, maximum_strategy_file_size: float):
        message = f"Maximum size of {maximum_strategy_file_size}MB exceeded. Strategy file size is {strategy_file_size}MB."
        super().__init__(message)


class Mizar:
    # API_KEY = "mizar-temp-secret-key"
    API_VERSION = "api/v1"
    API_URL = "{scheme}://{host}/{version}/"

    def __init__(self, api_key=None, api_url=None, scheme="https", host="api.mizar.ai"):
        if not api_key:
            api_key = os.getenv("MIZAR_API_KEY")
            if not api_key:
                raise ValueError("Both api_key and MIZAR_API_KEY are empty")
        self.api_key = api_key
        self.session = self._create_session()
        self.api_url = api_url or self.API_URL
        if scheme not in ("http", "https"):
            raise ValueError("Allowed scheme are http and https")
        self.api_url = self.API_URL.format(
            scheme=scheme, host=host, version=self.API_VERSION
        )
        # check working
        self.ping()

    def _create_session(self):
        session = requests.session()
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "mizar/python",
                "MIZAR-API-KEY": self.api_key,
            }
        )
        return session

    def _get(self, resource, **kwargs):
        uri = self.api_url + resource
        return self.session.get(uri, **kwargs)

    def _post(self, resource, **kwargs):
        uri = self.api_url + resource
        return self.session.post(url=uri, **kwargs)

    def ping(self):
        resp = self._get("ping")
        if resp.status_code != 200:
            raise MizarAPIException(resp.text)
        return self._handle_response(resp)

    def server_time(self):
        resp = self._get("server-time")
        return self._handle_response(resp)

    def _handle_response(self, response):
        if response.ok:
            return response.json()
        else:
            raise MizarAPIException(response.json())

    def get_exchanges(self):
        resp = self._get("exchanges")
        return self._handle_response(resp)

    def get_symbols(self, exchange: str, market: str = None):
        resp = self._get("symbols", params={"exchange": exchange, "market": market})
        return self._handle_response(resp)

    def get_bar_types(
        self,
        *,
        base_asset: Optional[str] = None,
        quote_asset: Optional[str] = None,
        bar_type: Optional[str] = None,
        bar_subclass: Optional[str] = None,
        exchange: Optional[str] = None,
        **kwargs,
    ):
        """
        Return the bar types

        :param base_asset: Base asset to select (e.g. BTC)
        :type base_asset: str
        :param quote_asset: Quote asset to select (e.g. USDT)
        :type quote_asset: str
        :param bar_type: bar type can be (e.g. tick, dollar, volume, time)
        :type bar_type: str
        :param bar_subclass: bar subclass specify the class of bar type
                             to select (e.g. 1min, 3min, dynamic etc..)
        :type bar_subclass: str
        :param exchange: exchange name
        :type exchange: str
        """
        kwargs.update(
            {
                "base_asset": base_asset,
                "quote_asset": quote_asset,
                "bar_type": bar_type,
                "bar_subclass": bar_subclass,
                "exchange": exchange,
            }
        )

        resp = self._get("bar-types", params=kwargs)
        return self._handle_response(resp)

    def get_bar_data(
        self,
        *,
        base_asset: str,
        quote_asset: str,
        start_timestamp: int = 0,
        limit: int = 500,
        bar_type: str = "time",
        bar_subclass: str = "D",
        exchange: str = "binance",
        **kwargs,
    ):
        """
        Return the bar data for a specific bar type

        :param base_asset: Base asset to select (e.g. BTC)
        :type base_asset: str
        :param quote_asset: Quote asset to select (e.g. USDT)
        :type quote_asset: str
        :param start_timestamp: The timestamp from which collect the bars
        :int start_timestamp: int
        :param limit: max number of bars to fetch (maximum allowed limit is 500)
        :type limit: int
        :param exchange: exchange name
        :type exchange: str
        :param bar_type: bar type can be (e.g. tick, dollar, volume, time)
        :type bar_type: str
        :param bar_subclass: bar subclass specify the class of bar type
                             to select (e.g. 1min, 3min, dynamic etc..)
        :type bar_subclass: str
        :return:

        [
            {
                'bar_type_id': 1,
                'base_asset_buy_volume': 105736.42,
                'base_asset_id': 184,
                'base_asset_sell_volume': 5325.2,
                'base_asset_volume': 111061.61999999998,
                'close': 0.27,
                'exchange_id': 1,
                'first_timestamp': 1523937753168,
                'first_trade_id': 0,
                'high': 0.27,
                'id': 1,
                'last_timestamp': 1523937778928,
                'last_trade_id': 14,
                'low': 0.25551,
                'num_buy_ticks': 13,
                'num_sell_ticks': 2,
                'num_ticks': 15,
                'open': 0.25551,
                'quote_asset_buy_volume': 27380.973451500002,
                'quote_asset_id': 4,
                'quote_asset_sell_volume': 1362.102,
                'quote_asset_volume': 28743.0754515,
                'time': '2018-04-17 04:02:00+00:00'
            },
            {
                etc
            },
            etc
        ]
        """
        kwargs.update(
            {
                "base_asset": base_asset,
                "quote_asset": quote_asset,
                "start_timestamp": start_timestamp,
                "limit": limit,
                "exchange": exchange,
                "bar_type": bar_type,
                "bar_subclass": bar_subclass,
            }
        )
        resp = self._get("bars", params=kwargs)
        return self._handle_response(resp)

    def save_hosted_strategy(
        self,
        strategy,
        strategy_info: Dict[str, Any],
        strategy_file: str = "",
    ):
        import codecs

        encoded_strategy = codecs.encode(pickle.dumps(strategy), "base64")

        encoded_strategy_size = len(encoded_strategy) / 1e6
        encoded_strategy_file_size = len(strategy_file.encode("utf-8")) / 1e6

        if encoded_strategy_size > MAXIMUM_STRATEGY_SIZE:
            raise StrategySizeExceededLimit(
                encoded_strategy_size, MAXIMUM_STRATEGY_SIZE
            )

        if encoded_strategy_file_size > MAXIMUM_STRATEGY_FILE:
            raise StrategyFileSizeExceededLimit(
                encoded_strategy_file_size, MAXIMUM_STRATEGY_FILE
            )

        resp = self._post(
            "publish-hosted-strategy",
            data={
                "strategy-info": json.dumps(strategy_info),
                "strategy-file": strategy_file,
                "strategy": encoded_strategy.decode(),
            },
        )

        return self._handle_response(resp)

    def create_self_hosted_strategy(
        self,
        name: str,
        description: str,
        exchanges: List[str],
        symbols: List[str],
        market: str,
    ):
        resp = self._post(
            "publish-self-hosted-strategy",
            json={
                "name": name,
                "description": description,
                "exchanges": exchanges,
                "symbols": symbols,
                "market": market,
            },
        )
        return self._handle_response(resp)

    def open_position(
        self,
        strategy_id: int,
        base_asset: str,
        quote_asset: str,
        size: float,
        is_long: bool,
    ):

        resp = self._post(
            "open-position",
            json={
                "strategy_id": strategy_id,
                "base_asset": base_asset,
                "quote_asset": quote_asset,
                "size": size,
                "is_long": is_long,
            },
        )
        return self._handle_response(resp)

    def close_position(self, position_id: int):
        resp = self._post(
            "close-position",
            json={
                "position_id": position_id,
            },
        )
        return self._handle_response(resp)

    def close_all_positions(self, strategy_id: int):
        resp = self._post(
            "close-all-positions",
            json={
                "strategy_id": strategy_id,
            },
        )
        return self._handle_response(resp)

    def get_all_open_positions(self, strategy_id: int):
        resp = self._get("all-open-positions", params={"strategy_id": strategy_id})
        return self._handle_response(resp)

    def get_all_self_hosted_strategies_info(self):
        resp = self._get("self-hosted-strategy-info")
        return self._handle_response(resp)

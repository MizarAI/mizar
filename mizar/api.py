import json
import os
import pickle
from typing import Any
from typing import Dict

import requests


class MizarAPIException(Exception):
    pass


class MizarRequestException(Exception):
    pass


class StrategySizeLimitReached(Exception):
    def __init__(self, signal_size: float, maximum_signal_size_allowed: float):
        message = f"Maximum size of {maximum_signal_size_allowed}MB exceeded. Signal size is {signal_size}MB."
        super().__init__(message)


class Mizar:
    # API_KEY = "mizar-temp-secret-key"
    API_VERSION = "v1"
    API_URL = "{scheme}://{host}/{version}/"

    def __init__(self, api_key=None, api_url=None, scheme="https", host="api.mizar.ai"):
        if not api_key:
            api_key = os.getenv("MIZAR_API_KEY")
            if not api_key:
                raise ValueError("Both api_key and MIZAR_API_KEY are empty")
        self.api_key = api_key
        self.session = self._create_session()
        self.api_url = api_url or self.API_URL
        assert scheme in ("http", "https")
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
        assert "pong" in resp.json().get("message")
        assert resp.status_code == 200
        return self._handle_response(resp)

    def _handle_response(self, response):
        if response.ok:
            try:
                if response.json().get("data"):
                    return {
                        "status": response.status_code,
                        "url": response.url,
                        "data": response.json().get("data"),
                    }
                elif response.json().get("message"):
                    return {
                        "status": response.status_code,
                        "url": response.url,
                        "message": response.json().get("message"),
                    }
                else:
                    raise MizarRequestException("No message or data")
            except ValueError:
                return MizarRequestException(response.text)
        else:
            raise MizarAPIException(response.json().get("message"))

    def get_quote_assets(self):
        resp = self._get("quote-assets")
        return self._handle_response(resp)

    def get_base_assets(self):
        resp = self._get("base-assets")
        return self._handle_response(resp)

    def get_exchanges(self):
        resp = self._get("exchanges")
        return self._handle_response(resp)

    def get_bar_types(self):
        resp = self._get("bar-types")
        return self._handle_response(resp)

    def get_bar_data(
        self,
        *,
        base_asset,
        quote_asset,
        start_timestamp,
        end_timestamp,
        exchange_name="binance",
        bar_type="time",
        bar_frequency="1min",
        **kwargs,
    ):
        """
        call to get bar data

        :param base_asset:
        :param quote_asset:
        :param start_timestamp:
        :param end_timestamp:
        :param exchange_name:
        :param bar_type:
        :param bar_frequency:
        :param kwargs:
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
                "end_timestamp": end_timestamp,
                "exchange_name": exchange_name,
                "bar_type": bar_type,
                "bar_frequency": bar_frequency,
            }
        )
        resp = self._get("bar", params=kwargs)
        return self._handle_response(resp)

    def save_strategy_signal(
        self,
        strategy,
        strategy_signal_info: Dict[str, Any],
    ):
        # TODO: later stage check if strategy-info entries match with
        #  strategy properties
        import codecs

        MAXIMUM_SIGNAL_SIZE_ALLOWED = 200

        encoded_strategy = codecs.encode(pickle.dumps(strategy), "base64")

        encoded_strategy_size = len(encoded_strategy) / 1e6

        if encoded_strategy_size > MAXIMUM_SIGNAL_SIZE_ALLOWED:
            raise StrategySizeLimitReached(
                encoded_strategy_size, MAXIMUM_SIGNAL_SIZE_ALLOWED
            )
        resp = self._post(
            "save-strategy",
            # do not change the way the data is posted to mizar
            # the strategy info are dumped in a json string because
            # data does not support nested dictionaries. The values in data
            # haveto be not nested
            data={
                "strategy-info": json.dumps(strategy_signal_info),
                # protocol is set to 0 otherwise we lose info when
                # the pickle object is transformed to string
                "strategy": encoded_strategy.decode(),
            },
        )

        return self._handle_response(resp)
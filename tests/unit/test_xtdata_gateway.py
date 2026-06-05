from __future__ import annotations

import time

import pytest

import app.services.xtdata_gateway as xtdata_gateway_module
from app.config import Settings
from app.services.contracts import KlineHistoryQuery, L2Query, TickHistoryQuery, TradingCalendarQuery
from app.services.xtdata_gateway import XtDataGateway
from app.utils.exceptions import DataServiceException


def build_settings(mode: str) -> Settings:
    return Settings(xtquant={"mode": mode, "data": {"qmt_userdata_path": "C:/fake-qmt"}})


@pytest.mark.parametrize(
    "callable_name, kwargs",
    [
        ("get_kline_history", {"query": KlineHistoryQuery(symbols=["000001.SZ"], period="1d")}),
        ("get_tick_history", {"query": TickHistoryQuery(symbols=["000001.SZ"])}),
        ("get_full_tick_snapshot", {"symbols": ["000001.SZ"]}),
    ],
)
def test_real_modes_fail_fast_when_xtdata_is_unavailable(monkeypatch, callable_name: str, kwargs: dict[str, object]):
    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: setattr(self, "_initialized", False))

    gateway = XtDataGateway(build_settings("dev"))

    with pytest.raises(DataServiceException) as exc:
        getattr(gateway, callable_name)(**kwargs)
    assert exc.value.error_code == "XTDATA_UNAVAILABLE"


def test_mock_mode_keeps_mock_data_paths():
    gateway = XtDataGateway(build_settings("mock"))

    kline = gateway.get_kline_history(KlineHistoryQuery(symbols=["000001.SZ"], period="1d"))
    tick = gateway.get_tick_history(TickHistoryQuery(symbols=["000001.SZ"]))
    snapshot = gateway.get_full_tick_snapshot(["000001.SZ"])

    assert kline[0]["symbol"] == "000001.SZ"
    assert tick[0]["ticks"]
    assert snapshot[0]["tick"]["last_price"] == 100.0


def test_real_mode_connect_attempt_is_single_flight(monkeypatch):
    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: None)
    gateway = XtDataGateway(build_settings("dev"))

    class FakeThread:
        def __init__(self):
            self.started = False

        def is_alive(self):
            return True

    existing_thread = FakeThread()
    gateway._connect_thread = existing_thread

    with gateway._connect_lock:
        thread = gateway._start_connect_thread_locked()

    assert thread is existing_thread


def test_real_mode_connect_respects_retry_cooldown(monkeypatch):
    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: None)
    gateway = XtDataGateway(build_settings("dev"))
    gateway._last_connect_failure_at = time.monotonic()

    def fail_if_called():
        raise AssertionError("should not start a new xtdata connect attempt during cooldown")

    monkeypatch.setattr(gateway, "_configure_xtdata", fail_if_called)

    with gateway._connect_lock:
        thread = gateway._start_connect_thread_locked()

    assert thread is None


class FakeArray:
    def __init__(self, values):
        self._values = values

    def tolist(self):
        return self._values

    def __bool__(self):
        raise ValueError("ambiguous truth value")


def test_l2_helpers_accept_empty_array_payloads(monkeypatch):
    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: setattr(self, "_initialized", True))
    gateway = XtDataGateway(build_settings("dev"))

    class DummyXtData:
        @staticmethod
        def get_l2_quote(**kwargs):
            return FakeArray([])

        @staticmethod
        def get_l2_order(**kwargs):
            return FakeArray([])

        @staticmethod
        def get_l2_transaction(**kwargs):
            return FakeArray([])

    monkeypatch.setattr(xtdata_gateway_module, "xtdata", DummyXtData())

    query = L2Query(symbols=["000001.SZ"], start_time="", end_time="")
    assert gateway.get_l2_quote(query) == []
    assert gateway.get_l2_order(query) == [{"symbol": "000001.SZ", "orders": []}]
    assert gateway.get_l2_transaction(query) == [
        {"symbol": "000001.SZ", "transactions": []}
    ]


def test_mock_mode_download_history_data_noop():
    gateway = XtDataGateway(build_settings("mock"))
    gateway.download_history_data("000001.SZ", "1d", incrementally=True)


def test_dev_mode_download_calls_xtdata(monkeypatch):
    recorded: list[tuple[str, str, bool]] = []

    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: setattr(self, "_initialized", True))

    class DummyXtData:
        @staticmethod
        def download_history_data(symbol, period, incrementally=True):
            recorded.append((symbol, period, incrementally))

    monkeypatch.setattr(xtdata_gateway_module, "xtdata", DummyXtData())
    monkeypatch.setattr(xtdata_gateway_module, "XTQUANT_DATA_AVAILABLE", True)

    gateway = XtDataGateway(build_settings("dev"))
    gateway.download_history_data("000001.SZ", "1m", incrementally=True)
    assert recorded == [("000001.SZ", "1m", True)]


def test_trading_calendar_unsupported_maps_to_feature_not_supported(monkeypatch):
    monkeypatch.setattr(XtDataGateway, "_try_initialize", lambda self: setattr(self, "_initialized", True))
    gateway = XtDataGateway(build_settings("dev"))

    class DummyXtData:
        @staticmethod
        def get_trading_calendar(*args, **kwargs):
            raise RuntimeError("function not realize")

    monkeypatch.setattr(xtdata_gateway_module, "xtdata", DummyXtData())

    with pytest.raises(DataServiceException) as exc:
        gateway.get_trading_calendar(TradingCalendarQuery(market="SH", start_time="20240101", end_time="20240131"))
    assert exc.value.error_code == "FEATURE_NOT_SUPPORTED"

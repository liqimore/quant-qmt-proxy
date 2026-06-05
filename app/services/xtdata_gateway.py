from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timedelta
from typing import Any

from app.config import Settings, XTQuantMode
from app.services.contracts import FinancialDataQuery, KlineHistoryQuery, L2Query, TickHistoryQuery, TradingCalendarQuery
from app.utils.exceptions import DataServiceException
from app.utils.helpers import validate_stock_code
from app.utils.logger import logger

try:
    import xtquant.xtdata as xtdata

    XTQUANT_DATA_AVAILABLE = True
except ImportError:
    xtdata = None
    XTQUANT_DATA_AVAILABLE = False


KLINE_FIELDS = [
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "settle",
    "openInterest",
    "preClose",
    "suspendFlag",
]

TICK_FIELDS = [
    "time",
    "lastPrice",
    "open",
    "high",
    "low",
    "lastClose",
    "amount",
    "volume",
    "pvolume",
    "openInt",
    "stockStatus",
    "lastSettlementPrice",
    "askPrice",
    "bidPrice",
    "askVol",
    "bidVol",
    "transactionNum",
]

CONNECT_JOIN_TIMEOUT_SECONDS = 5.0
CONNECT_RETRY_COOLDOWN_SECONDS = 5.0


def normalize_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes, dict)):
        try:
            return value.tolist()
        except Exception:
            pass
    return value


def to_epoch_ms(value: Any) -> int:
    value = normalize_scalar(value)
    if value in (None, ""):
        return int(time.time() * 1000)
    if isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    if isinstance(value, (int, float)):
        if value > 1_000_000_000_000:
            return int(value)
        if value > 1_000_000_000:
            return int(float(value) * 1000)
    value_str = str(value)
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d"):
        try:
            return int(datetime.strptime(value_str, fmt).timestamp() * 1000)
        except ValueError:
            continue
    return int(time.time() * 1000)


def normalize_sequence(value: Any) -> list[Any]:
    value = normalize_scalar(value)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes, dict)):
        try:
            normalized = value.tolist()
            if normalized is None:
                return []
            if isinstance(normalized, list):
                return normalized
            if isinstance(normalized, tuple):
                return list(normalized)
            return [normalized]
        except Exception:
            pass
    return [value]


class XtDataGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._initialized = False
        self._connect_lock = threading.RLock()
        self._connect_thread: threading.Thread | None = None
        self._last_connect_error: str | None = None
        self._last_connect_failure_at = 0.0
        self._try_initialize()

    def _is_mock_mode(self) -> bool:
        return self.settings.xtquant.mode == XTQuantMode.MOCK

    def _configure_xtdata(self) -> None:
        if not XTQUANT_DATA_AVAILABLE:
            return
        xtdata.enable_hello = False
        if self.settings.xtquant.data.qmt_userdata_path:
            xtdata.data_dir = os.path.join(self.settings.xtquant.data.qmt_userdata_path, "datadir")

    def _connect_worker(self) -> None:
        result: dict[str, Any] = {"error": None, "client": None}
        try:
            result["client"] = xtdata.connect()
        except Exception as exc:
            result["error"] = exc

        error = result["error"]
        if error is not None:
            logger.warning(f"xtdata connect failed: {error}")
            self._initialized = False
            self._last_connect_error = str(error)
            self._last_connect_failure_at = time.monotonic()
            return

        client = result["client"]
        connected = bool(client and hasattr(client, "is_connected") and client.is_connected())
        self._initialized = connected
        if connected:
            self._last_connect_error = None
            return
        self._last_connect_error = "xtdata.connect() did not yield a connected client"
        self._last_connect_failure_at = time.monotonic()

    def _start_connect_thread_locked(self) -> threading.Thread | None:
        if self._connect_thread and self._connect_thread.is_alive():
            return self._connect_thread
        if self._last_connect_failure_at:
            retry_after = self._last_connect_failure_at + CONNECT_RETRY_COOLDOWN_SECONDS
            if time.monotonic() < retry_after:
                return None

        self._configure_xtdata()
        thread = threading.Thread(target=self._connect_worker, daemon=True, name="xtdata-connect")
        self._connect_thread = thread
        thread.start()
        return thread

    def _try_initialize(self) -> None:
        if self._is_mock_mode():
            self._initialized = False
            return
        if not XTQUANT_DATA_AVAILABLE:
            self._initialized = False
            self._last_connect_error = "xtquant.xtdata is unavailable"
            return

        thread: threading.Thread | None
        with self._connect_lock:
            thread = self._start_connect_thread_locked()
        if thread is not None:
            thread.join(timeout=CONNECT_JOIN_TIMEOUT_SECONDS)
            if thread.is_alive():
                logger.warning("xtdata connect attempt timed out; waiting for current attempt to finish")

    def ensure_ready(self) -> None:
        if self._is_mock_mode():
            return
        if self._initialized:
            return
        with self._connect_lock:
            if not self._initialized:
                self._try_initialize()
        if not self._initialized:
            reason = f": {self._last_connect_error}" if self._last_connect_error else ""
            raise DataServiceException(
                "xtdata is unavailable; verify xtquant installation, QMT login state, and qmt_userdata_path"
                + reason,
                error_code="XTDATA_UNAVAILABLE",
            )

    def download_history_data(self, symbol: str, period: str, *, incrementally: bool = True) -> None:
        validate_stock_code(symbol)
        if self._is_mock_mode():
            logger.debug(
                f"mock download_history_data skipped: symbol={symbol} period={period} incrementally={incrementally}"
            )
            return
        self.ensure_ready()
        xtdata.download_history_data(symbol, period=period, incrementally=incrementally)

    def get_kline_history(self, query: KlineHistoryQuery) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return self._mock_kline_history(query)
        self.ensure_ready()
        raw = xtdata.get_market_data(
            field_list=query.fields,
            stock_list=query.symbols,
            period=query.period,
            start_time=query.start_time,
            end_time=query.end_time,
            count=-1,
            dividend_type=query.adjust_type,
            fill_data=query.fill_data,
        )
        return self._format_kline_history(raw, query.symbols, query.fields)

    def get_tick_history(self, query: TickHistoryQuery) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return self._mock_tick_history(query.symbols)
        self.ensure_ready()
        raw = xtdata.get_market_data(
            field_list=query.fields,
            stock_list=query.symbols,
            period="tick",
            start_time=query.start_time,
            end_time=query.end_time,
            count=-1,
            dividend_type=query.adjust_type,
            fill_data=False,
        )
        return self._format_tick_history(raw, query.symbols, query.fields)

    def get_full_tick_snapshot(self, symbols: list[str]) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [{"symbol": symbol, "tick": self._mock_tick_payload(symbol)} for symbol in symbols]
        self.ensure_ready()
        raw = xtdata.get_full_tick(symbols)
        return [
            {"symbol": symbol, "tick": self._normalize_tick_payload(payload)}
            for symbol, payload in (raw or {}).items()
        ]

    def get_financial_data(self, query: FinancialDataQuery) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [
                {
                    "symbol": symbol,
                    "table_name": table_name,
                    "columns": ["date", "value"],
                    "rows": [{"date": "20241231", "value": "100"}],
                }
                for symbol in query.symbols
                for table_name in query.table_names
            ]
        self.ensure_ready()
        raw = xtdata.get_financial_data(
            query.symbols,
            table_list=query.table_names,
            start_time=query.start_time,
            end_time=query.end_time,
        )
        items: list[dict[str, Any]] = []
        for symbol, table_map in (raw or {}).items():
            for table_name, frame in table_map.items():
                rows: list[dict[str, str]] = []
                columns = list(getattr(frame, "columns", []))
                if hasattr(frame, "reset_index"):
                    for record in frame.reset_index().to_dict("records"):
                        rows.append({str(k): str(normalize_scalar(v)) for k, v in record.items()})
                items.append(
                    {
                        "symbol": symbol,
                        "table_name": table_name,
                        "columns": [str(column) for column in columns],
                        "rows": rows,
                    }
                )
        return items

    def get_instrument_detail(self, symbol: str, complete: bool = False) -> dict[str, Any]:
        if self._is_mock_mode():
            return {"symbol": symbol, "fields": {"InstrumentID": symbol, "InstrumentName": f"Mock {symbol}"}}
        self.ensure_ready()
        detail = xtdata.get_instrument_detail(symbol, iscomplete=complete) or {}
        return {"symbol": symbol, "fields": {str(k): str(normalize_scalar(v)) for k, v in detail.items()}}

    def get_trading_calendar(self, query: TradingCalendarQuery) -> dict[str, Any]:
        if self._is_mock_mode():
            base = datetime.strptime(query.start_time or "20250101", "%Y%m%d")
            return {
                "market": query.market,
                "dates": [(base + timedelta(days=offset)).strftime("%Y%m%d") for offset in range(5)],
            }
        self.ensure_ready()
        try:
            dates = xtdata.get_trading_calendar(query.market, query.start_time, query.end_time)
        except RuntimeError as exc:
            if self._is_feature_not_supported_error(exc):
                raise DataServiceException(
                    "trading calendar is not supported by the current QMT client",
                    error_code="FEATURE_NOT_SUPPORTED",
                ) from exc
            raise
        return {"market": query.market, "dates": [str(item) for item in (dates or [])]}

    def get_index_weight(self, index_code: str) -> dict[str, Any]:
        if self._is_mock_mode():
            return {
                "index_code": index_code,
                "components": [{"symbol": "000001.SZ", "weight": 0.1}, {"symbol": "600000.SH", "weight": 0.2}],
            }
        self.ensure_ready()
        data = xtdata.get_index_weight(index_code) or {}
        components = [
            {"symbol": str(symbol), "weight": float(normalize_scalar(weight))}
            for symbol, weight in data.items()
        ]
        return {"index_code": index_code, "components": components}

    def get_sector_list(self) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [{"sector_name": "Mock Sector", "symbols": ["000001.SZ", "600000.SH"]}]
        self.ensure_ready()
        sectors = xtdata.get_sector_list() or []
        result = []
        for sector_name in sectors:
            try:
                symbols = xtdata.get_stock_list_in_sector(sector_name) or []
            except Exception:
                symbols = []
            result.append({"sector_name": str(sector_name), "symbols": [str(item) for item in symbols]})
        return result

    def get_l2_quote(self, query: L2Query) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [{"symbol": symbol, "quote": self._mock_tick_payload(symbol)} for symbol in query.symbols]
        self.ensure_ready()
        items = []
        for symbol in query.symbols:
            payload = xtdata.get_l2_quote(stock_code=symbol, start_time=query.start_time, end_time=query.end_time)
            records = normalize_sequence(payload)
            if not records:
                continue
            for record in records:
                items.append({"symbol": symbol, "quote": self._normalize_tick_payload(record)})
        return items

    def get_l2_order(self, query: L2Query) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [{"symbol": symbol, "orders": [self._mock_l2_order()]} for symbol in query.symbols]
        self.ensure_ready()
        items = []
        for symbol in query.symbols:
            payload = xtdata.get_l2_order(stock_code=symbol, start_time=query.start_time, end_time=query.end_time)
            records = normalize_sequence(payload)
            items.append({"symbol": symbol, "orders": [self._normalize_l2_order(item) for item in records]})
        return items

    def get_l2_transaction(self, query: L2Query) -> list[dict[str, Any]]:
        if self._is_mock_mode():
            return [{"symbol": symbol, "transactions": [self._mock_l2_transaction()]} for symbol in query.symbols]
        self.ensure_ready()
        items = []
        for symbol in query.symbols:
            payload = xtdata.get_l2_transaction(
                stock_code=symbol,
                start_time=query.start_time,
                end_time=query.end_time,
            )
            records = normalize_sequence(payload)
            items.append(
                {"symbol": symbol, "transactions": [self._normalize_l2_transaction(item) for item in records]}
            )
        return items

    def _format_kline_history(
        self,
        data: Any,
        symbols: list[str],
        requested_fields: list[str],
    ) -> list[dict[str, Any]]:
        if not isinstance(data, dict) or not data:
            return []
        result: list[dict[str, Any]] = []
        first_frame = next(iter(data.values()))
        columns = list(getattr(first_frame, "columns", []))
        for symbol in symbols:
            if hasattr(first_frame, "index") and symbol not in first_frame.index:
                continue
            bars: list[dict[str, Any]] = []
            for column in columns:
                bar = {"time_ms": to_epoch_ms(column)}
                for field in KLINE_FIELDS[1:]:
                    if field not in data:
                        continue
                    try:
                        value = data[field].loc[symbol, column]
                    except Exception:
                        continue
                    normalized = normalize_scalar(value)
                    key = self._snake_case_field(field)
                    if key in {"volume", "open_interest", "suspend_flag"}:
                        bar[key] = int(normalized or 0)
                    else:
                        bar[key] = float(normalized or 0.0)
                bars.append(bar)
            result.append({"symbol": symbol, "fields": requested_fields or KLINE_FIELDS, "bars": bars})
        return result

    def _format_tick_history(
        self,
        data: Any,
        symbols: list[str],
        requested_fields: list[str],
    ) -> list[dict[str, Any]]:
        if not isinstance(data, dict) or not data:
            return []
        result: list[dict[str, Any]] = []
        for symbol in symbols:
            rows = data.get(symbol)
            if rows is None:
                continue
            ticks: list[dict[str, Any]] = []
            if hasattr(rows, "dtype") and getattr(rows.dtype, "names", None):
                available_fields = list(rows.dtype.names)
                selected = requested_fields or available_fields
                for row in rows:
                    item = {field: normalize_scalar(row[field]) for field in selected if field in available_fields}
                    ticks.append(self._normalize_tick_payload(item))
            elif hasattr(rows, "to_dict"):
                for record in rows.to_dict("records"):
                    ticks.append(self._normalize_tick_payload(record))
            elif isinstance(rows, list):
                for row in rows:
                    ticks.append(self._normalize_tick_payload(row))
            result.append({"symbol": symbol, "fields": requested_fields or TICK_FIELDS, "ticks": ticks})
        return result

    def _normalize_tick_payload(self, payload: Any) -> dict[str, Any]:
        if payload is None:
            return self._mock_tick_payload("UNKNOWN")
        if hasattr(payload, "to_dict"):
            try:
                payload = payload.to_dict()
            except Exception:
                payload = {}
        if not isinstance(payload, dict):
            payload = dict(payload)
        return {
            "time_ms": to_epoch_ms(payload.get("time")),
            "last_price": float(normalize_scalar(payload.get("lastPrice", payload.get("last_price", 0.0))) or 0.0),
            "open": float(normalize_scalar(payload.get("open", 0.0)) or 0.0),
            "high": float(normalize_scalar(payload.get("high", 0.0)) or 0.0),
            "low": float(normalize_scalar(payload.get("low", 0.0)) or 0.0),
            "last_close": float(normalize_scalar(payload.get("lastClose", payload.get("last_close", 0.0))) or 0.0),
            "amount": float(normalize_scalar(payload.get("amount", 0.0)) or 0.0),
            "volume": int(normalize_scalar(payload.get("volume", 0)) or 0),
            "pvolume": int(normalize_scalar(payload.get("pvolume", 0)) or 0),
            "open_int": int(normalize_scalar(payload.get("openInt", payload.get("open_int", 0))) or 0),
            "stock_status": int(normalize_scalar(payload.get("stockStatus", payload.get("stock_status", 0))) or 0),
            "last_settlement_price": float(
                normalize_scalar(payload.get("lastSettlementPrice", payload.get("last_settlement_price", 0.0))) or 0.0
            ),
            "ask_price": [
                float(normalize_scalar(item) or 0.0)
                for item in payload.get("askPrice", payload.get("ask_price", []))
            ],
            "bid_price": [
                float(normalize_scalar(item) or 0.0)
                for item in payload.get("bidPrice", payload.get("bid_price", []))
            ],
            "ask_vol": [int(normalize_scalar(item) or 0) for item in payload.get("askVol", payload.get("ask_vol", []))],
            "bid_vol": [int(normalize_scalar(item) or 0) for item in payload.get("bidVol", payload.get("bid_vol", []))],
            "transaction_num": int(
                normalize_scalar(payload.get("transactionNum", payload.get("transaction_num", 0))) or 0
            ),
        }

    def _normalize_l2_order(self, payload: Any) -> dict[str, Any]:
        return {
            "time_ms": to_epoch_ms(payload.get("time")),
            "price": float(normalize_scalar(payload.get("price", 0.0)) or 0.0),
            "volume": int(normalize_scalar(payload.get("volume", 0)) or 0),
            "entrust_no": int(normalize_scalar(payload.get("entrustNo", payload.get("entrust_no", 0))) or 0),
            "entrust_type": int(normalize_scalar(payload.get("entrustType", payload.get("entrust_type", 0))) or 0),
            "entrust_direction": int(
                normalize_scalar(payload.get("entrustDirection", payload.get("entrust_direction", 0))) or 0
            ),
        }

    def _normalize_l2_transaction(self, payload: Any) -> dict[str, Any]:
        return {
            "time_ms": to_epoch_ms(payload.get("time")),
            "price": float(normalize_scalar(payload.get("price", 0.0)) or 0.0),
            "volume": int(normalize_scalar(payload.get("volume", 0)) or 0),
            "amount": float(normalize_scalar(payload.get("amount", 0.0)) or 0.0),
            "trade_index": int(normalize_scalar(payload.get("tradeIndex", payload.get("trade_index", 0))) or 0),
            "buy_no": int(normalize_scalar(payload.get("buyNo", payload.get("buy_no", 0))) or 0),
            "sell_no": int(normalize_scalar(payload.get("sellNo", payload.get("sell_no", 0))) or 0),
            "trade_type": int(normalize_scalar(payload.get("tradeType", payload.get("trade_type", 0))) or 0),
            "trade_flag": int(normalize_scalar(payload.get("tradeFlag", payload.get("trade_flag", 0))) or 0),
        }

    def _mock_kline_history(self, query: KlineHistoryQuery) -> list[dict[str, Any]]:
        base = datetime.strptime(query.start_time or "20250101", "%Y%m%d")
        items = []
        for symbol in query.symbols:
            if not validate_stock_code(symbol):
                raise DataServiceException(f"invalid stock code: {symbol}", error_code="INVALID_STOCK_CODE")
            bars = []
            for offset in range(5):
                ts = base + timedelta(days=offset)
                price = 100 + offset
                bars.append(
                    {
                        "time_ms": int(ts.timestamp() * 1000),
                        "open": price,
                        "high": price + 1,
                        "low": price - 1,
                        "close": price + 0.5,
                        "volume": 1000 + offset,
                        "amount": (price + 0.5) * (1000 + offset),
                        "settle": price + 0.25,
                        "open_interest": 500 + offset,
                        "pre_close": price - 0.5,
                        "suspend_flag": 0,
                    }
                )
            items.append({"symbol": symbol, "fields": query.fields or KLINE_FIELDS, "bars": bars})
        return items

    def _mock_tick_history(self, symbols: list[str]) -> list[dict[str, Any]]:
        return [{"symbol": symbol, "fields": TICK_FIELDS, "ticks": [self._mock_tick_payload(symbol)]} for symbol in symbols]

    def _mock_tick_payload(self, symbol: str) -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        return {
            "time_ms": now_ms,
            "last_price": 100.0,
            "open": 99.0,
            "high": 101.0,
            "low": 98.5,
            "last_close": 99.5,
            "amount": 1000000.0,
            "volume": 10000,
            "pvolume": 10000,
            "open_int": 0,
            "stock_status": 0,
            "last_settlement_price": 0.0,
            "ask_price": [100.1, 100.2],
            "bid_price": [99.9, 99.8],
            "ask_vol": [500, 300],
            "bid_vol": [450, 250],
            "transaction_num": 20,
        }

    def _mock_l2_order(self) -> dict[str, Any]:
        return {
            "time_ms": int(time.time() * 1000),
            "price": 100.0,
            "volume": 1000,
            "entrust_no": 12345,
            "entrust_type": 1,
            "entrust_direction": 1,
        }

    def _mock_l2_transaction(self) -> dict[str, Any]:
        return {
            "time_ms": int(time.time() * 1000),
            "price": 100.0,
            "volume": 1000,
            "amount": 100000.0,
            "trade_index": 1,
            "buy_no": 100,
            "sell_no": 200,
            "trade_type": 1,
            "trade_flag": 1,
        }

    def _snake_case_field(self, field: str) -> str:
        mapping = {
            "openInterest": "open_interest",
            "preClose": "pre_close",
            "suspendFlag": "suspend_flag",
        }
        return mapping.get(field, field)

    def _is_feature_not_supported_error(self, exc: RuntimeError) -> bool:
        message = str(exc).lower()
        return "function not realize" in message or "errorid" in message

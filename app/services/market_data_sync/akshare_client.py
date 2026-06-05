from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.services.market_data_sync.symbol_mapping import akshare_row_to_xt_symbol, market_from_symbol


def fetch_a_share_rows() -> list[dict[str, Any]]:
    import akshare as ak

    frame = ak.stock_info_a_code_name()
    code_column = "code" if "code" in frame.columns else frame.columns[0]
    name_column = "name" if "name" in frame.columns else frame.columns[1]
    rows: list[dict[str, Any]] = []
    for _, record in frame.iterrows():
        code = str(record[code_column]).strip()
        name = str(record[name_column]).strip()
        symbol = akshare_row_to_xt_symbol(code)
        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "market": market_from_symbol(symbol),
                "source": "akshare",
                "enabled": True,
            }
        )
    return rows


def default_fetch_rows() -> list[dict[str, Any]]:
    return fetch_a_share_rows()


FetchRowsFn = Callable[[], list[dict[str, Any]]]

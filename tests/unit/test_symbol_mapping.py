from __future__ import annotations

import pytest

from app.services.market_data_sync.symbol_mapping import akshare_row_to_xt_symbol


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("600000", "600000.SH"),
        ("000001", "000001.SZ"),
        ("300750", "300750.SZ"),
        ("920001", "920001.BJ"),
    ],
)
def test_akshare_row_to_xt_symbol(code: str, expected: str):
    assert akshare_row_to_xt_symbol(code) == expected


def test_akshare_row_invalid_raises():
    with pytest.raises(ValueError):
        akshare_row_to_xt_symbol("INVALID")

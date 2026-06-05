from __future__ import annotations


def akshare_row_to_xt_symbol(code: str) -> str:
    normalized = str(code).strip()
    if len(normalized) != 6 or not normalized.isdigit():
        raise ValueError(f"invalid a-share code: {code!r}")
    if normalized.startswith("6"):
        return f"{normalized}.SH"
    if normalized.startswith(("0", "3")):
        return f"{normalized}.SZ"
    if normalized.startswith(("4", "8", "9")):
        return f"{normalized}.BJ"
    raise ValueError(f"unsupported code prefix: {code!r}")


def market_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SH"):
        return "SH"
    if symbol.endswith(".SZ"):
        return "SZ"
    if symbol.endswith(".BJ"):
        return "BJ"
    raise ValueError(f"cannot infer market from symbol: {symbol!r}")

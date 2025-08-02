from dataclasses import dataclass


@dataclass
class MarketMetadata:
    name: str
    date: str
    market_index: float
    market_sma: float  # current sma125 value
    market_momentum: float  # VN30 and its 125-day moving average
    market_volatility: float  # VIX and its 50-day moving average
    price_strength: float  # number of stocks on the VN30 at 52-week highs compared to those at 52-week lows.
    price_breadth: float  # McClellan Volume Summation Index: amount/volume/shares price rising vs falling
    # next v3
    safe_haven_demand: float  # Difference in 20-day stock and bond returns
    junk_bond_demand: float  # Yield spread: junk bonds vs. investment grade
    put_call_ratio: float  # 5-day average put/call ratio

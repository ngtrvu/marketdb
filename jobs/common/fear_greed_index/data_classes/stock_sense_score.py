from dataclasses import dataclass


@dataclass
class StockSenseScore:
    """Data structure for stock market sentiment score."""

    name: str
    date: str
    price: float  # close or current price
    volume: float

    # indicators
    returns: float  # current log returns
    is_advance: bool  # Advance or Decline in last 5 days
    volatility: float  # last 50 days
    sma: float  # current sma125 value
    rsi: float  # current rsi value

    # sentiment
    sma_sense: float
    rsi_sense: float
    returns_sense: float
    volatility_sense: float

    def __init__(
            self, name: str, date: str, price: float, volume: float,
            sma: float, rsi: float, returns: float, is_advance: bool, volatility: float,
            sma_sense: float, rsi_sense: float, returns_sense: float, volatility_sense: float,
    ):
        self.name = name.upper()
        self.date = date
        self.price = price
        self.volume = volume

        self.returns = returns
        self.is_advance = is_advance
        self.volatility = volatility
        self.sma = sma
        self.rsi = rsi

        self.sma_sense = sma_sense
        self.rsi_sense = rsi_sense
        self.returns_sense = returns_sense
        self.volatility_sense = volatility_sense

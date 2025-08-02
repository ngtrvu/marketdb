import click

from utils.logger import logger
from pipelines.stock_prices.stock_price_history_by_time import (
    StockPriceHistoryByTime,
)
from pipelines.stock_prices.stock_price_history_eod import (
    StockPriceHistoryEOD,
)
from pipelines.stock_prices.stock_price_history_init import (
    StockPriceHistoryInit,
)
from pipelines.stock_prices.stock_price_history_reset import (
    StockPriceHistoryReset,
)
from pipelines.stock_analytics.stock_price_analytics_intraday_job import (
    StockPriceAnalyticsIntradayJob,
)
from pipelines.stock_analytics.stock_price_analytics_job import (
    StockPriceAnalyticsJob,
)


@click.command()
def commands():
    logger.info("Stock: 0.0.1")


@click.command()
@click.option("--input_date", type=str)
def run_stock_price_history_init(input_date: str = None):
    StockPriceHistoryInit().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_stock_price_history_eod(input_date: str = None):
    StockPriceHistoryEOD().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_stock_price_history_by_time(input_date: str = None):
    StockPriceHistoryByTime().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_stock_price_history_reset(input_date: str = None):
    StockPriceHistoryReset().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
@click.option("--exchange", type=str)
@click.option("--type", type=str)
@click.option("--data_type", type=str)
@click.option("--data_ver", type=int)
def run_stock_price_analytics(
    input_date: str = None,
    exchange: str = None,
    type: str = None,
    data_type: str = None,
    data_ver: int = 2,
):
    StockPriceAnalyticsJob().run(
        input_date=input_date,
        type=type,
        data_type=data_type,
    )


@click.command()
@click.option("--input_date", type=str)
def run_stock_price_analytics_intraday(input_date: str = None):
    StockPriceAnalyticsIntradayJob().run(input_date=input_date)

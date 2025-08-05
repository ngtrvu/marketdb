import click

from utils.logger import logger

from pipelines.market_index.market_index_stock_indexer import (
    MarketIndexStockIndexer,
)
from pipelines.market_index.market_index_daily_backfill import (
    MarketIndexDailyBackfill,
)
from pipelines.market_index.market_index_bulk_transform import (
    MarketIndexBulkTransform,
)
from pipelines.market_index.market_index_bulk_transform_v1 import (
    MarketIndexBulkTransformV1,
)
from pipelines.market_index.market_index_analytics_job import (
    MarketIndexAnalyticsJob,
)
from pipelines.market_index.market_index_intraday_job import (
    MarketIndexIntradayJob,
)
from pipelines.stock_prices.stock_price_intraday import (
    StockPriceIntradayJob,
)


@click.command()
def commands():
    logger.info("MarketIndex: 0.0.1")


@click.command()
@click.option("--input_date", type=str)
def run_market_index_stock_indexer(input_date=None):
    MarketIndexStockIndexer().pipeline(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_market_index_daily_backfill(input_date=None):
    MarketIndexDailyBackfill().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_market_index_bulk_transform(input_date: str = None):
    MarketIndexBulkTransform().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_market_index_bulk_transform_v1(input_date: str = None):
    MarketIndexBulkTransformV1().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_market_index_analytics(input_date=None):
    MarketIndexAnalyticsJob().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_exchange_intraday_indexer(input_date=None):
    StockPriceIntradayJob().run(input_date=input_date)
    MarketIndexIntradayJob().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_market_index_intraday_indexer(input_date=None):
    MarketIndexIntradayJob().run(input_date=input_date)

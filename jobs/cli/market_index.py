import click

from pipelines.market_index.market_index_stock_indexer import (
    MarketIndexStockIndexer,
)
from pipelines.market_index.market_index_daily_backfill import (
    MarketIndexDailyBackfill,
)
from utils.logger import logger


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

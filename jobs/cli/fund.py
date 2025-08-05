import click

from utils.logger import logger

from pipelines.marketdb_exporter.fund_nav_bulk_exporter import FundNavBulkExporter
from pipelines.funds.mutual_fund_nav import MutualFundNAVCrawler
from pipelines.funds.mutual_fund_nav_backfill import MutualFundNAVBackfill
from pipelines.funds.mutual_fund_nav_analytics_etl import MutualFundNAVAnalyticsETL
from pipelines.funds.vcam_fund_nav_crawler import VcamNAVCrawler
from pipelines.funds.mutual_fund_nav_daily_etl import MutualFundNAVDailyETL
from pipelines.funds.mutual_fund_nav_price_chart import MutualFundNavPriceChart

@click.command()
def commands():
    logger.info("Fund: 1.0.0")


@click.command()
@click.option("--input_date", type=str)
@click.option("--fund_manager", type=int)
@click.option("--symbol", type=str)
def run_mutual_fund_nav_intraday_crawler(
    input_date=None, fund_manager=None, symbol=None
):
    MutualFundNAVCrawler().run(
        input_date=input_date, fund_manager=fund_manager, symbol=symbol
    )


@click.command()
@click.option("--input_date", type=str)
@click.option("--symbol", type=str)
@click.option("--fund_manager", type=int)
@click.option("--start_date", type=str)
@click.option("--end_date", type=str)
def run_mutual_fund_nav_backfill(
    input_date=None, symbol=None, fund_manager=None, start_date=None, end_date=None
):
    MutualFundNAVBackfill().run(
        input_date=input_date,
        symbol=symbol,
        fund_manager=fund_manager,
        start_date=start_date,
        end_date=end_date,
    )


@click.command()
@click.option("--input_date", type=str)
@click.option("--symbol", type=str)
@click.option("--from_date", type=str)
@click.option("--to_date", type=str)
def run_mutual_fund_nav_backfill_etl(
    input_date=None, symbol=None, from_date=None, to_date=None
):
    MutualFundNAVBackfill().run_etl(
        input_date=input_date, symbol=symbol, from_date=from_date, to_date=to_date
    )


@click.command()
@click.option("--input_date", type=str)
@click.option("--from_date", type=str)
@click.option("--backfill", count=True)
def run_mutual_fund_nav_daily_indexer(input_date=None, from_date=None, backfill=0):
    job = MutualFundNAVDailyETL()
    if backfill:
        job.run_backfilling(input_date=input_date, from_date=from_date)
    else:
        job.run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_mutual_fund_nav_analytics_indexer(input_date=None):
    MutualFundNAVAnalyticsETL().run(input_date=input_date)


@click.command()
@click.option("--fund_code", type=str)
@click.option("--input_date", type=str)
@click.option("--from_date", type=str)
@click.option("--to_date", type=str)
def run_mutual_fund_nav_crawler(
    fund_code, input_date=None, from_date=None, to_date=None
):
    VcamNAVCrawler().run(
        input_date=input_date, from_date=from_date, to_date=to_date, fund_code=fund_code
    )


@click.command()
@click.option("--input_date", "-d", type=str)
@click.option("--backfill", count=True)
def run_mutual_fund_nav_price_chart(input_date=None, backfill=0):
    job = MutualFundNavPriceChart()
    if backfill:
        job.parallel = 10
        job.run_backfilling(input_date)
    else:
        job.run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_mutual_fund_nav_bulk_exporter(input_date=None):
    FundNavBulkExporter().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_fund_intraday(input_date: str = None):
    logger.info("Running fund pipeline")

    MutualFundNAVCrawler().run(input_date=input_date, fund_manager=None, symbol=None)

    MutualFundNAVDailyETL().run(input_date=input_date)
    FundNavBulkExporter().run(input_date=input_date)
    MutualFundNavPriceChart().run(input_date=input_date)
    MutualFundNAVAnalyticsETL().run(input_date=input_date)


@click.command()
@click.option("--input_date", type=str)
def run_fund_initializer(input_date: str = None):
    logger.info("Running fund initializer")

    MutualFundNAVDailyETL().run(input_date=input_date)
    FundNavBulkExporter().run(input_date=input_date)
    MutualFundNavPriceChart().run(input_date=input_date)
    MutualFundNAVAnalyticsETL().run(input_date=input_date)

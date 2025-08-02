import logging
import os
import click

from utils.logger import logger, setup_logger

from cli import etf, fund, stock, market_index
from pipelines.funds.mutual_fund_nav import MutualFundNAVCrawler
from pipelines.funds.mutual_fund_nav_backfill import (
    MutualFundNAVBackfill,
)
from pipelines.cryptos.crypto_info_etl import CryptoInfoETL
from pipelines.cryptos.crypto_price_realtime_job import (
    CryptoPriceRealtimeJob,
)
from pipelines.fear_greed_index.computing_job import (
    FearGreedIndexComputingJob,
)
from pipelines.fear_greed_index.indexer_job import (
    FearGreedIndexIndexerJob,
)
from pipelines.funds.mutual_fund_nav_analytics_etl import (
    MutualFundNAVAnalyticsETL,
)
from pipelines.funds.vcam_fund_nav_crawler import VcamNAVCrawler
from pipelines.funds.mutual_fund_nav_daily_etl import (
    MutualFundNAVDailyETL,
)
from pipelines.funds.mutual_fund_nav_price_chart import (
    MutualFundNavPriceChart,
)
from pipelines.industry.industry_analytics_daily_job import (
    IndustryAnalyticsDailyJob,
)
from pipelines.market_index.market_analytics import (
    MarketPerformanceAnalyticsJob,
)
from pipelines.market_index.market_index_analytics_job import (
    MarketIndexAnalyticsJob,
)
from pipelines.market_index.market_index_intraday_job import (
    MarketIndexIntradayJob,
)
from pipelines.marketdb_exporter.fund_nav_bulk_exporter import (
    FundNavBulkExporter,
)
from pipelines.marketdb_exporter.stock_event_bulk_exporter import (
    StockEventBulkExporter,
)
from pipelines.marketdb_exporter.stock_exporter import (
    StockExporter,
)
from pipelines.marketdb_importer.industry_etl import IndustryETL

# marketdb import data, one off jobs
from pipelines.marketdb_importer.stock_brand_name_etl import (
    StockBrandNameETL,
)
from pipelines.search_indexer.search_indexing_job import (
    SearchIndexingJob,
)

from pipelines.etf_analytics.etf_price_analytics_job import (
    ETFPriceAnalyticsJob,
)
from pipelines.etf_analytics.etf_price_analytics_intraday_job import (
    ETFPriceAnalyticsIntradayJob,
)
from pipelines.stock_prices.stock_price_intraday import (
    StockPriceIntradayJob,
)
from pipelines.stock_prices.stock_price_bulk_transform_v3 import (
    StockPriceBulkTransformV3,
)
from pipelines.market_index.market_index_bulk_transform import (
    MarketIndexBulkTransform,
)
from pipelines.market_index.market_index_bulk_transform_v1 import (
    MarketIndexBulkTransformV1,
)
from pipelines.etf_analytics.etf_price_bulk_transform import (
    ETFPriceBulkTransform,
)

from pipelines.stocks.etf_info_initializer import (
    ETFInfoInitializer,
)
from pipelines.stocks.stock_corporate_action import (
    StockCorporateAction,
)
from pipelines.stocks.stock_events_etl import StockEventETL
from pipelines.stocks.stock_events_log_etl import StockEventLogETL
from pipelines.stocks.stock_info_initializer import (
    StockInfoInitializer,
)
from pipelines.stocks.stock_new_initializer import (
    StockNewInitializer,
)
from pipelines.trading_initialization_job import (
    TradingInitializationJob,
)
from pipelines.crawlers.crawler_cafef_market_data.main import (
    CafeFMarketDataCrawler,
)
from pipelines.crawlers.crawler_iboard_market_index_intraday.main import (
    IBoardMarketIndexIntraday,
)
from pipelines.crawlers.crawler_iboard_market_index_group.main import (
    IBoardMarketIndexGroup,
)
from pipelines.stock_prices.stock_price_history_backfill import (
    StockPriceHistoryBackfill,
)
from pipelines.marketdb_exporter.market_index_exporter import (
    MarketIndexExporter,
)

from dotenv import load_dotenv

load_dotenv(".env")


@click.group()
def cli():
    logging.info("commands for job runners")


@cli.command()
@click.option("--input_date", type=str)
def run_search_indexer(input_date):
    SearchIndexingJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_trading_initializer(input_date=None):
    TradingInitializationJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_exchange_intraday_indexer(input_date=None):
    StockPriceIntradayJob().run(input_date=input_date)
    MarketIndexIntradayJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_market_index_intraday_indexer(input_date=None):
    MarketIndexIntradayJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
@click.option("--fund_manager", type=int)
@click.option("--symbol", type=str)
def run_mutual_fund_nav_intraday_crawler(
    input_date=None, fund_manager=None, symbol=None
):
    MutualFundNAVCrawler().run(
        input_date=input_date, fund_manager=fund_manager, symbol=symbol
    )


@cli.command()
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


@cli.command()
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


@cli.command()
@click.option("--input_date", type=str)
@click.option("--from_date", type=str)
@click.option("--backfill", count=True)
def run_mutual_fund_nav_daily_indexer(input_date=None, from_date=None, backfill=0):
    job = MutualFundNAVDailyETL()
    if backfill:
        job.run_backfilling(input_date=input_date, from_date=from_date)
    else:
        job.run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_mutual_fund_nav_analytics_indexer(input_date=None):
    MutualFundNAVAnalyticsETL().run(input_date=input_date)


@cli.command()
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


@cli.command()
@click.option("--input_date", "-d", type=str)
@click.option("--backfill", count=True)
def run_mutual_fund_nav_price_chart(input_date=None, backfill=0):
    job = MutualFundNavPriceChart()
    if backfill:
        job.parallel = 10
        job.run_backfilling(input_date)
    else:
        job.run(input_date=input_date)


@cli.command()
def run_crypto_info_indexer():
    CryptoInfoETL().run()


@cli.command()
def run_crypto_price_realtime_indexer():
    CryptoPriceRealtimeJob().run()


@cli.command()
@click.option("--input_date", type=str)
def run_stock_exporter(input_date=None):
    MarketIndexExporter().run(input_date=input_date)
    StockExporter().run(input_date=input_date)


@cli.command()
def run_stock_event_bulk_exporter():
    StockEventBulkExporter().run()


@cli.command()
@click.option("--input_date", type=str)
def run_mutual_fund_nav_bulk_exporter(input_date=None):
    FundNavBulkExporter().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_industry_info_indexer(input_date=None):
    IndustryETL().run(input_date="2022/12/23" if not input_date else input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_industry_analytics(input_date=None):
    IndustryAnalyticsDailyJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_market_index_analytics(input_date=None):
    MarketIndexAnalyticsJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_market_performances(input_date=None):
    MarketPerformanceAnalyticsJob().run(input_date=input_date)


@cli.command()
@click.option("--from_date", type=str)
def get_market_performances(from_date=None):
    market_performance = MarketPerformanceAnalyticsJob().get_benchmark_performance(
        user_start_date=from_date
    )
    if market_performance:
        print(f"Market performance since user's first order: {from_date}")
        print(f"Total return: {market_performance['total_return']:.2%}")
        print(f"Holding period: {market_performance['trading_days']} days")
        print(market_performance)


@cli.command()
@click.option("--input_date", type=str)
@click.option("--from_date", type=str, default=None)
def run_fear_greed_index_indexer(input_date=None, from_date=None):
    if from_date:
        FearGreedIndexIndexerJob().run_backfilling(
            input_date=input_date, from_date=from_date
        )
    else:
        FearGreedIndexIndexerJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
@click.option("--from_date", type=str, default=None)
def run_fear_greed_index_computing(input_date=None, from_date=None):
    if from_date:
        FearGreedIndexComputingJob().run_backfilling(
            input_date=input_date, from_date=from_date
        )
    else:
        FearGreedIndexComputingJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_stock_info_initializer(input_date=None):
    StockInfoInitializer().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_etf_info_initializer(input_date=None):
    ETFInfoInitializer().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_stock_new_initializer(input_date=None):
    StockNewInitializer().run(input_date=input_date)


@cli.command()
def run_stock_brand_name_indexer():
    StockBrandNameETL().run()


@cli.command()
@click.option("--input_date", type=str)
def run_stock_event_indexer(input_date=None):
    StockEventETL().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_stock_event_log_indexer(input_date=None):
    StockEventLogETL().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
@click.option("--backfill", count=True)
def run_stock_corporate_action(input_date=None, backfill=0):
    if backfill:
        StockCorporateAction().run_backfilling(input_date)
    else:
        StockCorporateAction().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_stock_price_bulk_transform(input_date: str = None):
    StockPriceBulkTransformV3().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_market_index_bulk_transform(input_date: str = None):
    MarketIndexBulkTransform().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_market_index_bulk_transform_v1(input_date: str = None):
    MarketIndexBulkTransformV1().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_etf_price_bulk_transform(input_date: str = None):
    ETFPriceBulkTransform().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_etf_price_analytics_intraday(input_date: str = None):
    ETFPriceAnalyticsIntradayJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_etf_price_analytics(input_date: str = None):
    ETFPriceAnalyticsJob().run(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
@click.option("--adjusted", type=bool, default=True)
def run_crawler_cafef_market_data(input_date: str = None, adjusted: bool = True):
    CafeFMarketDataCrawler().pipeline(input_date=input_date, adjusted=adjusted)


@cli.command()
@click.option("--input_date", type=str)
def run_crawler_iboard_market_index_intraday(input_date: str = None):
    IBoardMarketIndexIntraday().pipeline(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_crawler_iboard_market_index_group(input_date: str = None):
    IBoardMarketIndexGroup().pipeline(input_date=input_date)


@cli.command()
@click.option("--input_date", type=str)
def run_stock_price_history_backfill(input_date: str = None):
    StockPriceHistoryBackfill().run(input_date=input_date)


cli.add_command(etf.commands)
cli.add_command(fund.commands)
cli.add_command(stock.commands)
cli.add_command(market_index.commands)


if __name__ == "__main__":
    setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))
    logger.info("CLI for local job runners")

    cli()

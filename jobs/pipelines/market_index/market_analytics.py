import logging

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from utils.logger import logger
from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE, get_date_str, str_to_datetime, ensure_tzaware_datetime,
)
from common.mdb.trading_calendar import TradingCalendar
from config import Config


class MarketPerformanceAnalyticsJob(MiniJobBase, TradingCalendar):
    """Enhanced Market Performance Analytics with Daily Metrics

    Computes market performance metrics on a daily trading basis for a given market index.
    for comparison with user portfolios of varying holding periods up to 2+ years.
    """

    def __init__(self):
        super().__init__()
        self.data_frame: pd.DataFrame = pd.DataFrame()
        self.daily_metrics: Dict = {}
        self.risk_free_rate: float = 0.05

    def _load_market_data(self, input_date: str, allowed_symbols: List[str]) -> bool:
        """
        Load market index data from GCS

        Args:
            input_date: Date string in format YYYY/MM/DD
            allowed_symbols: List of market symbols to analyze

        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            # Load data from GCS using parent class method
            df = self.load(
                input_date=input_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="marketdb/market_index_ohlc_bulk",
                file_name_prefix="market_index_ohlc_bulk.json",
            )

            # Filter and sort data
            df = df[df["symbol"].isin(allowed_symbols)]
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.set_index('date', inplace=True)

            # Store the dataframe and latest date
            self.data_frame = df
            self.latest_date = df.index.max().strftime('%Y/%m/%d')

            logger.info(f"Loaded market data up to {self.latest_date}")
            return True

        except Exception as ex:
            logger.error(f"Error loading market data: {str(ex)}")
            return False

    def pipeline(self, input_date: str = None, allowed_symbols=["VNINDEX"]) -> bool:
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logger.info(f"MarketPerformanceAnalytics: No trading today: {input_date}")
            return True

        if not self._load_market_data(input_date, allowed_symbols):
            return False

        self._compute_daily_metrics()
        self._export_results(input_date)

        logger.info("MarketPerformanceAnalytics is successfully executed.")
        return True

    def _compute_daily_metrics(self):
        """
        Compute market data and metrics for each trading day to the latest date.
        """
        all_rows = []

        for symbol in self.data_frame['symbol'].unique():
            df = self.data_frame[self.data_frame['symbol'] == symbol].copy()

            # Calculate daily returns
            df['daily_return'] = df['close'].pct_change()

            # Calculate metrics for each trading day
            for date in df.index:
                # Get all data points from this date to the latest date
                period_df = df[df.index >= date].copy()

                if len(period_df) > 0:
                    # Calculate metrics for this period
                    start_price = period_df['close'].iloc[0]
                    end_price = period_df['close'].iloc[-1]
                    total_return = (end_price / start_price) - 1
                    trading_days = len(period_df)

                    # Calculate annualized metrics
                    annual_factor = 252 / trading_days
                    annualized_return = (1 + total_return) ** annual_factor - 1
                    daily_returns = period_df['daily_return'].dropna()
                    annualized_vol = np.std(daily_returns) * np.sqrt(252)

                    # Calculate drawdown
                    peak = period_df['close'].expanding(min_periods=1).max()
                    drawdown = ((period_df['close'] - peak) / peak)
                    max_drawdown = float(drawdown.min())

                    # Create row with all metrics
                    row_data = {
                        'symbol': symbol,
                        'trading_date': date.strftime('%Y-%m-%d'),
                        'trading_days': trading_days,
                        'start_price': float(start_price),
                        'end_price': float(end_price),
                        'total_return': float(total_return),
                        'annualized_return': float(annualized_return),
                        'annualized_volatility': float(annualized_vol),
                        'max_drawdown': float(max_drawdown),
                        'positive_days': int(len(daily_returns[daily_returns > 0])),
                        'start_date': period_df.index[0].strftime('%Y-%m-%d'),
                        'end_date': period_df.index[-1].strftime('%Y-%m-%d')
                    }

                    all_rows.append(row_data)

        # Convert to DataFrame
        daily_df = pd.DataFrame(all_rows)
        # Sort by index
        daily_df.sort_index(inplace=True)

        # Store in class variable
        self.daily_metrics = daily_df

    def _calculate_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown for a price series"""
        peak = prices.expanding(min_periods=1).max()
        drawdown = (prices - peak) / peak
        return float(drawdown.min())

    def _export_results(self, input_date: str):
        """Export performance metrics to GCS"""
        output_path = f"marketdb/market_analytics/{self.latest_date}/market_performance_metrics.json"

        self.export_to_gcs(
            df=self.daily_metrics,
            bucket_name=Config.BUCKET_NAME,
            gcs_path=output_path
        )

    def get_benchmark_performance(self, user_start_date: str, symbol: str = "VNINDEX") -> Optional[Dict]:
        """
        Get benchmark performance metrics from GCS for comparison with user portfolio

        Args:
            user_start_date: First paid order date of the user in format 'YYYY/MM/DD'
            symbol: Market index symbol to use as benchmark

        Returns:
            Optional[Dict]: Benchmark performance metrics for the user's holding period,
                           or None if data cannot be retrieved
        """
        try:
            # Get latest available date
            latest_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)
            latest_date = (datetime.strptime(latest_date, "%Y/%m/%d") - timedelta(days=1)).strftime("%Y/%m/%d")

            # Find latest trading date
            while not self.is_trading_date(latest_date):
                latest_date = (datetime.strptime(latest_date, "%Y/%m/%d") - timedelta(days=1)).strftime("%Y/%m/%d")

            # Load metrics from GCS
            df = self.load(
                input_date=latest_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="marketdb/market_analytics",
                file_name_prefix="market_performance_metrics.json",
            )

            if df is None or df.empty:
                logger.error(f"No data available for date {latest_date}")
                return None

            # Convert user_start_date to YYYY-MM-DD format
            user_date_formatted = datetime.strptime(user_start_date, "%Y/%m/%d").strftime("%Y-%m-%d")

            # Get the row with the closest trading_date that's not after user's start date
            day_data = df[(df['trading_date'] <= user_date_formatted) &
                          (df['symbol'] == symbol)].sort_values('trading_date', ascending=False)

            if day_data.empty:
                logger.error(f"No market data available for date {user_start_date}")
                return None

            return day_data.iloc[0].to_dict()

        except Exception as ex:
            logger.error(f"Error getting benchmark performance: {str(ex)}")
            return None
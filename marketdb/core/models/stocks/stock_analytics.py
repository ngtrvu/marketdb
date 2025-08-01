from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel, Currency, Quarter, CompanyType


class MarcoIndicator(BaseModel):
    class Meta:
        db_table = "marco_indicator"
        app_label = "core"

    year = models.IntegerField(primary_key=True)
    risk_free_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Bond rate 5Yr/10Yr ???
    equity_risk_premium = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    corporate_tax_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True)


class StockFA(BaseModel):
    """Stock Fundamental Analysis
    """
    class Meta:
        db_table = "stock_fundamental_analysis"
        app_label = "core"

    symbol = models.CharField(max_length=50, unique=True)
    date = models.DateField(null=True, db_index=True)
    datetime = models.DateTimeField()  # data datetime

    # time feature dimension
    year = models.IntegerField()
    quarter = models.IntegerField(default=Quarter.Q0)

    # market info
    currency = models.CharField(max_length=10, default=Currency.VND)
    market_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # price on the 'date'
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # market capitalization
    volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # volume trading on market

    # outstanding_shares x market_value ~ market capitalization
    outstanding_shares = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    # measure of the volatility–or systematic risk, apply in CAPM
    beta = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # risk
    """ ratios """
    # pricing
    eps = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # earning per share
    diluted_eps = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # diluted earning per share
    bvps = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # book price per share
    pe = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # price-to–earnings ratio
    pb = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # price–to-book ratio
    ps = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # price-to-Sales per Share
    peg = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # price / earnings-to-growth
    # returns
    roa = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # return on assets
    roe = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # return on equity
    ros = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # return on sales

    # valuation variables
    revenue_growth_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # in revenue/sales avg 5 year
    earnings_growth_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # in net_income avg 5 year
    discount_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cost_of_debt = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    cost_of_equity = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    free_cash_flow = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    dcf_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # DCF
    graham_price = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Graham’s Formula

    # dividend
    dividend_yield = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # avg recent payouts
    dividend = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # dividend per share

    # forecasting
    roa_forecast_3yr = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    roe_forecast_3yr = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    growth_rate_forecast_3yr = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # in revenue
    revenue_forecast_3yr = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    # addition
    ev_ebitda = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # EV / EBITDA
    ev_sales = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # EV / Sales (Revenue)
    profit_margin = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # net income / annual sales
    gross_profit_to_sales = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # (sales - cogs) / annual sales
    roic = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # return on invested capital
    wacc = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # Weighted average cost of capital
    debt_to_equity = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # debt to equity
    debt_to_asset = models.DecimalField(max_digits=20, decimal_places=2, null=True)  # debt to asset
    quick_ratio = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    current_ratio = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    industry_name = models.CharField(max_length=200, null=True, blank=True)
    super_sector_name = models.CharField(max_length=200, null=True, blank=True)
    sector_name = models.CharField(max_length=200, null=True, blank=True)
    sub_sector_name = models.CharField(max_length=200, null=True, blank=True)
    company_type = models.CharField(max_length=50, default=CompanyType.COMPANY, null=True, blank=True)


class StockTA(BaseModel):
    """ Stock Technical Analysis

    Reference: https://mrjbq7.github.io/ta-lib/
    """
    class Meta:
        db_table = "stock_technical_analysis"
        app_label = "core"

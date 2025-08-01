from __future__ import unicode_literals

from django.db import models


class ContentStatusEnum:
    DRAFT = 1001
    PUBLISHED = 1002
    TRASH = 1003
    PRIVATE = 1004


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency:
    VND = 'vnd'
    USD = 'usd'


class Quarter:
    # quarter zero means all year, otherwise means quarter 1,2,3,4
    Q0 = 0
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4


class AssetType:
    STOCK = 'STOCK'
    MUTUAL_FUND = 'mutual_fund'
    ETF = 'ETF'
    CRYPTO = 'crypto'
    GOLD = 'gold'
    TERM_DEPOSIT = 'term_deposit'


class CompanyType:
    """
    CK, NH, BH, CT
    """
    SECURITIES = "SECURITIES"
    BANKING = "BANKING"
    INSURANCE = "INSURANCE"
    COMPANY = "COMPANY"

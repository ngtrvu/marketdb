# from datetime import datetime

# from common.tinydwh.datetime_util import (
#     ensure_tzaware_datetime,
#     VN_TIMEZONE,
# )

from pipelines.crawlers.crawler_mutual_funds_nav.config import (
    MutualFundNav,
    MutualFundSource,
    DRAGON_CAPITAL_SYMBOLS,
    VINA_CAPITAL_SYMBOLS,
    SSI_SYMBOLS,
    VN_DIRECT_SYMBOLS,
    VIET_CAPITAL_SYMBOLS,
    MIRAE_ASSET_SYMBOLS,
    VIETCOMBANK_SYMBOLS,
)


def to_dict_price(fund: MutualFundNav) -> dict:
    # crawl_time = datetime.strptime("16:00:00", "%H:%M:%S").time()
    # fund_date = datetime.strptime(fund.nav_date_str, "%Y-%m-%d")
    # fund_datetime = ensure_tzaware_datetime(
    #     datetime.combine(fund_date, crawl_time), tz=VN_TIMEZONE
    # )

    return {
        "symbol": fund.symbol,
        "date": fund.nav_date_str,
        # "datetime": fund_datetime.strftime("%Y-%m-%d %H:%M:%S%z"),
        "datetime": f"{fund.nav_date_str} 16:00:00",
        "nav": fund.nav,
    }


def get_source_from_symbol(symbol: str) -> MutualFundSource:
    if symbol in DRAGON_CAPITAL_SYMBOLS:
        return MutualFundSource.DRAGON_CAPITAL
    elif symbol in VINA_CAPITAL_SYMBOLS:
        return MutualFundSource.VINA_CAPITAL
    elif symbol in SSI_SYMBOLS:
        return MutualFundSource.SSI
    elif symbol in VN_DIRECT_SYMBOLS:
        return MutualFundSource.VN_DIRECT
    elif symbol in VIET_CAPITAL_SYMBOLS:
        return MutualFundSource.VIET_CAPITAL
        # return MutualFundSource.STAG_VCAM
    elif symbol in MIRAE_ASSET_SYMBOLS:
        return MutualFundSource.MIRAE_ASSET
    elif symbol in VIETCOMBANK_SYMBOLS:
        return MutualFundSource.VIETCOMBANK

    return MutualFundSource.UNKNOWN_FUND

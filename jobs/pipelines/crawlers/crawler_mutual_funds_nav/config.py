import enum
from dataclasses import dataclass
from datetime import datetime


# Mutual fund symbols
DRAGON_CAPITAL_SYMBOLS = ["DCDS", "DCDE", "DCBF", "VFMVSF", "DCIP"]
VINA_CAPITAL_SYMBOLS = ["VEOF", "VFF", "VIBF", "VESAF", "VLBF"]
SSI_SYMBOLS = ["SSI-SCA", "SSIBF", "VLGF"]
VN_DIRECT_SYMBOLS = ["VNDAF"]
VIET_CAPITAL_SYMBOLS = ["VCAMDF", "VCAMBF", "VCAMFI"]
MIRAE_ASSET_SYMBOLS = ["MAGEF", "MAFF"]
VIETCOMBANK_SYMBOLS = ["VCBF-BCF", "VCBF-MGF", "VCBF-FIF", "VCBF-TBF"]
ALL_SYMBOLS = (
    VIET_CAPITAL_SYMBOLS
    + MIRAE_ASSET_SYMBOLS
    + VIETCOMBANK_SYMBOLS
    + DRAGON_CAPITAL_SYMBOLS
    + VINA_CAPITAL_SYMBOLS
    + SSI_SYMBOLS
    + VN_DIRECT_SYMBOLS
)
STAG_SUPPORTED_SYMBOLS = VIET_CAPITAL_SYMBOLS + MIRAE_ASSET_SYMBOLS + VIETCOMBANK_SYMBOLS

# VNDAF history url, not sure what it is
VNDAF_HISTORY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSuhuAEtnIlPQpbsfEkeZoZaxsPX_3t-vFQ9QN_pweOsAaY05uB1h1cTxOfND448ElWckApBY7zyEE/pub?gid=0&single=true&output=csv"


class MutualFundSource(enum.Enum):
    UNKNOWN_FUND = 1
    DRAGON_CAPITAL = 2
    VINA_CAPITAL = 3
    SSI = 4
    VN_DIRECT = 5
    VIET_CAPITAL = 6
    STAG_VCAM = 7
    MIRAE_ASSET = 8
    VIETCOMBANK = 9
    # add more funds
    TECHCOMBANK = 10


ALL_FUND_MANAGERS = [
    MutualFundSource.DRAGON_CAPITAL,
    MutualFundSource.VINA_CAPITAL,
    MutualFundSource.SSI,
    MutualFundSource.VN_DIRECT,
    MutualFundSource.VIET_CAPITAL,
    MutualFundSource.MIRAE_ASSET,
    MutualFundSource.VIETCOMBANK,
]

LATEST_NAV_URLS = {
    MutualFundSource.DRAGON_CAPITAL: "https://api.dragoncapital.com.vn/nav/getLatestValue.php?trade_code={}",
    # MutualFundSource.VINA_CAPITAL: VINA_CAPITAL_HISTORY,
    MutualFundSource.SSI: "https://ssiam.com.vn/ssiam/hieu-qua-dau-tu-quy/compare-chart?page_id={0}&page_compare_id=vn_index&date_started={1}&date_ended={2}",
    MutualFundSource.VN_DIRECT: "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSuhuAEtnIlPQpbsfEkeZoZaxsPX_3t-vFQ9QN_pweOsAaY05uB1h1cTxOfND448ElWckApBY7zyEE/pub?gid=0&single=true&output=csv",
    MutualFundSource.VIET_CAPITAL: "https://vietcapital.com.vn/performance_chart?locale=vi",
    MutualFundSource.STAG_VCAM: "https://api.fmarket.vn/home/product/{}",
    MutualFundSource.MIRAE_ASSET: "https://api.fmarket.vn/home/product/{}",
    MutualFundSource.VIETCOMBANK: "https://api.fmarket.vn/home/product/{}",
}

SYMBOLS_BY_SOURCE = {
    MutualFundSource.DRAGON_CAPITAL: DRAGON_CAPITAL_SYMBOLS,
    MutualFundSource.VINA_CAPITAL: VINA_CAPITAL_SYMBOLS,
    MutualFundSource.SSI: SSI_SYMBOLS,
    MutualFundSource.VN_DIRECT: VN_DIRECT_SYMBOLS,
    MutualFundSource.VIET_CAPITAL: VIET_CAPITAL_SYMBOLS,
    MutualFundSource.STAG_VCAM: VIET_CAPITAL_SYMBOLS,
    MutualFundSource.MIRAE_ASSET: MIRAE_ASSET_SYMBOLS,
    MutualFundSource.VIETCOMBANK: VIETCOMBANK_SYMBOLS,
}

FMARKET_SYMBOLS = [
    "VMEEF",
    "SSISCA",
    "VLGF",
    "BVPF",
    "TBLF",
    "DCDS",
    "VCBF-MGF",
    "VEOF",
    "UVEEF",
    "MBVF",
    "VESAF",
    "DCDE",
    "MAFEQI",
    "VCBF-BCF",
    "MAGEF",
    "DCAF",
    "BVFED",
    "PHVSF",
    "VNDAF",
    "NTPPF",
    "VDEF",
    "TCGF",
    "LHCDF",
    "VCAMDF",
    "GFM-VIF",
    "LHBF",
    "PVBF",
    "BVBF",
    "MBBOND",
    "VNDBF",
    "VCBF-FIF",
    "SSIBF",
    "MAFF",
    "DCBF",
    "VFF",
    "VCAM-NHVABF",
    "VNDCF",
    "HDBOND",
    "ASBF",
    "ABBF",
    "DCIP",
    "VLBF",
    "DFIX",
    "ENF",
    "VIBF",
    "VCBF-TBF",
    "MAFBAL",
    "VCAMBF",
    "PBIF",
    "UVDIF",
    "MDI",
]


@dataclass
class MutualFundNav:
    symbol: str
    nav: float
    nav_date_str: str
    nav_datetime: datetime = None

    def __init__(self, symbol, nav, nav_date_str):
        self.symbol, self.nav, self.nav_date_str = symbol, nav, nav_date_str
        self.nav_datetime = datetime.fromisoformat(self.nav_date_str)

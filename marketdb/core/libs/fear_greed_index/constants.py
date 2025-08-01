# global config for OHLC fields
OPEN = 'open'
CLOSE = 'close'
HIGH = 'high'
LOW = 'low'
ADJUSTED_CLOSE = 'adj_close'
VOLUME = 'volume'
DATETIME = 'datetime'

# a hard code whitelist, need auto crawl daily later
VN30 = [
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
]
VN100 = [
    'AAA', 'ACB', 'AGG', 'ANV', 'ASM', 'BCG', 'BCM', 'BID', 'BMP', 'BVH',
    'BWE', 'CII', 'CMG', 'CRE', 'CTD', 'CTG', 'CTR', 'DBC', 'DCM', 'DGC',
    'DGW', 'DHC', 'DIG', 'DPM', 'DXG', 'DXS', 'EIB', 'FPT', 'FRT', 'FTS',
    'GAS', 'GEG', 'GEX', 'GMD', 'GVR', 'HAG', 'HCM', 'HDB', 'HDC', 'HDG',
    'HHV', 'HPG', 'HSG', 'HT1', 'IMP', 'KBC', 'KDC', 'KDH', 'KOS', 'LPB',
    'MBB', 'MSB', 'MSN', 'MWG', 'NKG', 'NLG', 'NT2', 'OCB', 'PAN', 'PC1',
    'PDR', 'PHR', 'PLX', 'PNJ', 'POW', 'PPC', 'PTB', 'PVD', 'PVT', 'REE',
    'SAB', 'SAM', 'SBT', 'SCS', 'SHB', 'SJS', 'SSB', 'SSI', 'STB', 'SZC',
    'TCB', 'TCH', 'TMS', 'TPB', 'VCB', 'VCG', 'VCI', 'VGC', 'VHC', 'VHM',
    'VIB', 'VIC', 'VIX', 'VJC', 'VND', 'VNM', 'VPB', 'VPI', 'VRE', 'VSH'
]

# config for VNINDEX fields
INDEX_DATE = 'date'
INDEX_VALUE = 'reference'
INDEX_DIFF = 'change'
INDEX_PCT_CHANGE = 'pct_change'
INDEX_HIGH = 'high'
INDEX_LOW = 'low'
INDEX_OPEN = 'open'
INDEX_CLOSE = 'close'
INDEX_VOLUME = 'volume'

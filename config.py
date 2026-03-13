"""대시보드 설정값."""

STATUS_ORDER = ["위험", "주의", "안정", "데이터 지연", "N/A"]

FREQUENCY_RULES = {
    "일간": {"max_lag_days": 3, "label": "일간"},
    "주간": {"max_lag_days": 10, "label": "주간"},
    "월간": {"max_lag_days": 45, "label": "월간"},
    "저빈도": {"max_lag_days": 120, "label": "저빈도"},
}

FRED_SERIES = {
    "VIX": "VIXCLS",
    "10Y2Y": "T10Y2Y",
    "FED_BALANCE": "WALCL",
    "RESERVE_BALANCES": "WRESBAL",
    "RRP": "RRPONTSYD",
    "TGA": "WTREGEN",
    "HY_SPREAD": "BAMLH0A0HYM2",
    "SOFR": "SOFR",
    "EFFR": "DFF",
    "IORB": "IORB",
    "MMF_TOTAL": "WMMFSL",
    "FSI": "STLFSI4",
}

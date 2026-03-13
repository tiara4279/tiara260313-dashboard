"""대시보드 설정값."""

# 상태 표시 순서 (대시보드 정렬용)
STATUS_ORDER = [
    "공포",
    "신용경색 위험",
    "경기침체 경고",
    "위험회피 증가",
    "위험투자 증가",
    "긴장",
    "주의",
    "중립",
    "안정",
    "참고",
    "데이터 지연",
    "N/A",
]


# 데이터 지연 판단 기준
FREQUENCY_RULES = {
    "일간": {
        "max_lag_days": 3,
        "label": "일간",
    },
    "주간": {
        "max_lag_days": 10,
        "label": "주간",
    },
    "월간": {
        "max_lag_days": 45,
        "label": "월간",
    },
    "저빈도": {
        "max_lag_days": 120,
        "label": "저빈도",
    },
}


# FRED 데이터 시리즈
FRED_SERIES = {

    # 시장 심리
    "VIX": "VIXCLS",

    # 경기 사이클
    "10Y2Y": "T10Y2Y",

    # 연준 유동성
    "FED_BALANCE": "WALCL",
    "RESERVE_BALANCES": "WRESBAL",

    # 단기 자금시장
    "RRP": "RRPONTSYD",
    "TGA": "WTREGEN",

    # 신용시장
    "HY_SPREAD": "BAMLH0A0HYM2",

    # 단기금리
    "SOFR": "SOFR",
    "EFFR": "DFF",
    "IORB": "IORB",

    # Money Market Fund
    "MMF_TOTAL": "WMMFSL",

    # 금융 스트레스
    "FSI": "STLFSI4",
}

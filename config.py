"""Macro Liquidity Dashboard Config"""

STATUS_ORDER = ["위험", "주의", "안정", "데이터 지연", "N/A"]

FREQUENCY_RULES = {
    "일간": {"max_lag_days": 3},
    "주간": {"max_lag_days": 10},
    "월간": {"max_lag_days": 45},
    "저빈도": {"max_lag_days": 120},
}

FRED_SERIES = {

    # 시장 리스크
    "VIX": "VIXCLS",
    "HY_SPREAD": "BAMLH0A0HYM2",
    "FSI": "STLFSI4",

    # 금리
    "SOFR": "SOFR",
    "EFFR": "DFF",
    "IORB": "IORB",

    # 수익률 곡선
    "10Y2Y": "T10Y2Y",

    # 유동성
    "FED_BALANCE": "WALCL",
    "RESERVE_BALANCES": "WRESBAL",
    "RRP": "RRPONTSYD",
    "TGA": "WTREGEN",

    # Money Market Funds
    "MMF_TOTAL": "MMMFFAQ027S"
}

LIQUIDITY_SIGNALS = {

    "MMF_TREND": {
        "name": "MMF 총잔액 흐름",
        "type": "trend",
        "series": ["MMF_TOTAL"]
    },

    "MMF_RRP_FLOW": {
        "name": "MMF vs 역레포",
        "type": "flow",
        "series": ["MMF_TOTAL", "RRP"]
    },

    "MMF_WEEKLY_FLOW": {
        "name": "MMF 주간 증감",
        "type": "delta",
        "series": ["MMF_TOTAL"]
    },

    "NET_LIQUIDITY": {
        "name": "연준 순유동성",
        "type": "net_liquidity",
        "series": ["FED_BALANCE", "RRP", "TGA"]
    },

    "CREDIT_STRESS": {
        "name": "Credit Spread 상태",
        "type": "spread",
        "series": ["HY_SPREAD"]
    }
}

SIGNAL_MESSAGES = {

    "MMF_TREND": {
        "increase": "위험 회피 증가",
        "decrease": "위험 자산 이동",
        "neutral": "중립"
    },

    "MMF_RRP_FLOW": {
        "mmf": "기관 자금 MMF 이동",
        "rrp": "기관 자금 역레포 이동",
        "neutral": "기관 자금 중립"
    },

    "MMF_WEEKLY_FLOW": {
        "inflow": "단기 자금 유입",
        "outflow": "단기 자금 유출",
        "neutral": "변화 없음"
    },

    "NET_LIQUIDITY": {
        "increase": "시장 유동성 확대",
        "decrease": "시장 유동성 축소",
        "neutral": "변화 미미"
    },

    "CREDIT_STRESS": {
        "low": "금융 스트레스 완화",
        "high": "금융 스트레스 확대",
        "neutral": "중립"
    },

    "RISK_STATE": {
        "risk_on": "Risk On",
        "risk_off": "Risk Off",
        "neutral": "중립"
    }
}

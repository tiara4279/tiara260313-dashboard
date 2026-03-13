"""표시/검증 유틸리티."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from config import FREQUENCY_RULES


def now_utc_date() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc).date())


def validate_date(latest_date: pd.Timestamp, frequency: str) -> tuple[bool, int]:
    """주기별 지연 여부를 반환한다."""
    rule = FREQUENCY_RULES.get(frequency, FREQUENCY_RULES["저빈도"])
    lag_days = (now_utc_date() - pd.Timestamp(latest_date).normalize()).days
    return lag_days <= rule["max_lag_days"], lag_days


def format_date(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def format_billions(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value / 1_000:.2f}십억 달러"


def format_trillions(value: float | None) -> str:
    if value is None:
        return "N/A"

    # 기본 단위: 백만 달러
    trillion_value = value / 1_000_000      # 조 달러
    billion_value = value / 1_000           # 십억 달러
    eok_value = value / 100                 # 억 달러

    if trillion_value >= 1:
        return f"{trillion_value:.2f}조 달러"
    if billion_value >= 1:
        return f"{billion_value:.2f}십억 달러"
    return f"{eok_value:.2f}억 달러"


def default_indicator(name: str, frequency: str, source: str, note: str) -> dict:
    return {
        "지표": name,
        "값": "N/A",
        "상태": "N/A",
        "주기": frequency,
        "최신 기준일": "N/A",
        "출처": source,
        "비고": note,
    }

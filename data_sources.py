"""외부 데이터 소스 조회 모듈."""

from __future__ import annotations

from io import StringIO
from typing import Optional, Tuple

import pandas as pd
import requests


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


class DataFetchError(Exception):
    """데이터 조회 실패."""


def fetch_fred_series(series_id: str, timeout: int = 20) -> pd.Series:
    """FRED CSV 엔드포인트에서 시계열을 조회한다."""
    url = FRED_CSV_URL.format(series_id=series_id)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    frame = pd.read_csv(StringIO(response.text))
    if frame.shape[1] < 2:
        raise DataFetchError(f"시리즈 형식 오류: {series_id}")

    frame.columns = ["date", "value"]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"]).sort_values("date")

    if frame.empty:
        raise DataFetchError(f"시리즈 데이터 없음: {series_id}")

    return pd.Series(frame["value"].values, index=frame["date"], name=series_id)


def latest_point(series: pd.Series) -> Tuple[pd.Timestamp, float]:
    """최신 시점과 값을 반환한다."""
    if series.empty:
        raise DataFetchError("빈 시리즈")
    latest_idx = series.index.max()
    return pd.Timestamp(latest_idx), float(series.loc[latest_idx])


def previous_point(series: pd.Series) -> Optional[Tuple[pd.Timestamp, float]]:
    """직전 시점과 값을 반환한다."""
    if len(series) < 2:
        return None
    ordered = series.sort_index()
    prev_idx = ordered.index[-2]
    return pd.Timestamp(prev_idx), float(ordered.iloc[-2])

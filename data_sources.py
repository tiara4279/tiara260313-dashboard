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

def fetch_fear_greed_optional() -> tuple[pd.Timestamp | None, float | None]:
    """
    CNN Fear & Greed 비공식 JSON 엔드포인트 시도.
    실패하면 (None, None) 반환.
    """
    import requests
    import pandas as pd

    urls = [
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
    }

    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # 가장 자주 쓰이는 현재값 위치
            score = None
            score_date = None

            if isinstance(data, dict):
                if "fear_and_greed" in data and isinstance(data["fear_and_greed"], dict):
                    fg = data["fear_and_greed"]
                    score = fg.get("score")
                    score_date = fg.get("rating_update") or fg.get("timestamp")

                if score is None and "score" in data:
                    score = data.get("score")
                    score_date = data.get("rating_update") or data.get("timestamp")

            if score is None:
                continue

            try:
                score = float(score)
            except Exception:
                continue

            if score_date is not None:
                try:
                    ts = pd.to_datetime(score_date, utc=True).tz_localize(None)
                except Exception:
                    ts = pd.Timestamp.utcnow().tz_localize(None)
            else:
                ts = pd.Timestamp.utcnow().tz_localize(None)

            return ts, score

        except Exception:
            continue

    return None, None

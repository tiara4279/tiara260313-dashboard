"""지표 계산 로직."""

from __future__ import annotations

from typing import Callable
import pandas as pd

from config import FRED_SERIES
from data_sources import DataFetchError, fetch_fred_series, latest_point, previous_point
from utils import default_indicator, format_billions, format_date, format_trillions, validate_date


def _build(name: str, frequency: str, source: str, note: str, value: str, status: str, ref_date: pd.Timestamp) -> dict:
    is_fresh, _ = validate_date(ref_date, frequency)

    if not is_fresh and status != "N/A":
        status = "데이터 지연"

    return {
        "지표": name,
        "값": value,
        "상태": status,
        "주기": frequency,
        "최신 기준일": format_date(ref_date),
        "출처": source,
        "비고": note,
    }


def _safe_indicator(builder: Callable[[], dict], fallback: dict) -> dict:
    try:
        return builder()
    except Exception:
        fallback["비고"] = "데이터 조회 실패"
        return fallback


# -------------------------
# 시장 심리
# -------------------------

def indicator_vix() -> dict:
    fallback = default_indicator("VIX", "일간", "FRED (VIXCLS)", "옵션시장 변동성")

    def _run():
        series = fetch_fred_series(FRED_SERIES["VIX"])
        date, value = latest_point(series)

        if value >= 30:
            status = "공포"
        elif value >= 20:
            status = "긴장"
        else:
            status = "안정"

        return _build("VIX", "일간", "FRED (VIXCLS)", "옵션시장 변동성", f"{value:.2f}", status, date)

    return _safe_indicator(_run, fallback)


def indicator_hy_spread() -> dict:
    fallback = default_indicator("하이일드 스프레드", "일간", "FRED", "신용 위험")

    def _run():
        series = fetch_fred_series(FRED_SERIES["HY_SPREAD"])
        date, value = latest_point(series)

        if value > 6:
            status = "신용경색 위험"
        elif value > 4:
            status = "주의"
        else:
            status = "안정"

        return _build("하이일드 스프레드", "일간", "FRED", "회사채 신용스프레드", f"{value:.2f}%p", status, date)

    return _safe_indicator(_run, fallback)


# -------------------------
# 경기 사이클
# -------------------------

def indicator_10y2y() -> dict:
    fallback = default_indicator("10Y-2Y 스프레드", "일간", "FRED", "장단기 금리차")

    def _run():
        series = fetch_fred_series(FRED_SERIES["10Y2Y"])
        date, value = latest_point(series)

        if value < -0.5:
            status = "경기침체 경고"
        elif value < 0:
            status = "금리 역전"
        else:
            status = "정상"

        return _build("10Y-2Y 스프레드", "일간", "FRED", "음수 심화 시 경기침체 가능", f"{value:.2f}%p", status, date)

    return _safe_indicator(_run, fallback)


# -------------------------
# 유동성
# -------------------------

def indicator_fed_balance() -> dict:
    fallback = default_indicator("연준 대차대조표", "주간", "FRED", "연준 총자산")

    def _run():
        series = fetch_fred_series(FRED_SERIES["FED_BALANCE"])
        date, value = latest_point(series)

        return _build("연준 대차대조표", "주간", "FRED", "Fed Balance Sheet", format_trillions(value), "참고", date)

    return _safe_indicator(_run, fallback)


def indicator_rrp() -> dict:
    fallback = default_indicator("RRP", "일간", "FRED", "역레포")

    def _run():
        series = fetch_fred_series(FRED_SERIES["RRP"])
        date, value = latest_point(series)

        if value > 1_000_000:
            status = "유동성 흡수 증가"
        elif value > 300_000:
            status = "중립"
        else:
            status = "시장 유입 가능"

        return _build("RRP", "일간", "FRED", "연준 초과 유동성 흡수", format_trillions(value), status, date)

    return _safe_indicator(_run, fallback)


def indicator_tga() -> dict:
    fallback = default_indicator("TGA", "주간", "FRED", "재무부 계정")

    def _run():
        series = fetch_fred_series(FRED_SERIES["TGA"])
        date, value = latest_point(series)

        if value > 900_000:
            status = "시장 유동성 흡수"
        elif value > 300_000:
            status = "중립"
        else:
            status = "시장 유동성 공급"

        return _build("TGA", "주간", "FRED", "재무부 일반계정", format_billions(value), status, date)

    return _safe_indicator(_run, fallback)


# -------------------------
# MMF 핵심
# -------------------------

def indicator_mmf_total() -> dict:
    fallback = default_indicator("MMF 총자산", "주간", "FRED", "머니마켓 자산")

    def _run():
        series = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        date, value = latest_point(series)
        prev = previous_point(series)

        delta = value - prev[1]

        if delta > 20_000:
            status = "위험회피 증가"
        elif delta < -20_000:
            status = "위험투자 증가"
        else:
            status = "중립"

        return _build("MMF 총자산", "주간", "FRED", "자금 피난처 지표", format_trillions(value), status, date)

    return _safe_indicator(_run, fallback)


def indicator_mmf_wow() -> dict:
    fallback = default_indicator("MMF 주간 변화", "주간", "FRED", "MMF 흐름")

    def _run():
        series = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        date, value = latest_point(series)
        prev = previous_point(series)

        delta = value - prev[1]

        if delta > 50_000:
            status = "강한 위험회피"
        elif delta > 10_000:
            status = "위험회피"
        elif delta < -50_000:
            status = "강한 위험투자"
        elif delta < -10_000:
            status = "위험투자"
        else:
            status = "중립"

        return _build("MMF 주간 변화", "주간", "FRED", "단기 투자심리", f"{delta/1000:.2f}십억$", status, date)

    return _safe_indicator(_run, fallback)


def indicator_mmf_vs_rrp() -> dict:
    fallback = default_indicator("MMF vs RRP", "주간", "FRED", "기관 자금 흐름")

    def _run():
        mmf = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        rrp = fetch_fred_series(FRED_SERIES["RRP"])

        mmf_w = mmf.resample("W-FRI").last()
        rrp_w = rrp.resample("W-FRI").last()

        combined = pd.concat([mmf_w.rename("mmf"), rrp_w.rename("rrp")], axis=1).dropna()

        date = combined.index.max()
        mmf_val = combined.loc[date, "mmf"]
        rrp_val = combined.loc[date, "rrp"]

        prev = combined.iloc[-2]

        mmf_delta = mmf_val - prev["mmf"]
        rrp_delta = rrp_val - prev["rrp"]

        if mmf_delta > 0 and rrp_delta > 0:
            status = "위험회피 증가"
        elif mmf_delta < 0 and rrp_delta < 0:
            status = "위험자산 이동"
        else:
            status = "혼합"

        ratio = mmf_val / rrp_val if rrp_val > 0 else 0

        return _build("MMF vs RRP", "주간", "FRED", "기관 단기자금 흐름", f"{ratio:.2f}배", status, pd.Timestamp(date))

    return _safe_indicator(_run, fallback)


# -------------------------
# Net Liquidity
# -------------------------

def indicator_net_liquidity() -> dict:
    fallback = default_indicator("Net Liquidity", "주간", "FRED", "시장 유동성")

    def _run():
        fed = fetch_fred_series(FRED_SERIES["FED_BALANCE"])
        rrp = fetch_fred_series(FRED_SERIES["RRP"])
        tga = fetch_fred_series(FRED_SERIES["TGA"])

        combined = pd.concat([
            fed.rename("fed"),
            rrp.rename("rrp"),
            tga.rename("tga")
        ], axis=1).dropna()

        date = combined.index.max()

        fed_val = combined.loc[date, "fed"]
        rrp_val = combined.loc[date, "rrp"]
        tga_val = combined.loc[date, "tga"]

        net = fed_val - rrp_val - tga_val

        return _build(
            "Net Liquidity",
            "주간",
            "Fed 계산",
            "Fed - RRP - TGA",
            format_trillions(net),
            "참고",
            pd.Timestamp(date),
        )

    return _safe_indicator(_run, fallback)


# -------------------------
# 전체 지표
# -------------------------

def build_all_indicators() -> list[dict]:

    indicators = [
        indicator_vix,
        indicator_hy_spread,
        indicator_10y2y,
        indicator_fed_balance,
        indicator_rrp,
        indicator_tga,
        indicator_mmf_total,
        indicator_mmf_wow,
        indicator_mmf_vs_rrp,
        indicator_net_liquidity,
    ]

    return [fn() for fn in indicators]

"""지표 계산 로직."""

from __future__ import annotations

from typing import Callable

import pandas as pd

from config import FRED_SERIES
from data_sources import DataFetchError, fetch_fred_series, latest_point, previous_point
from utils import default_indicator, format_billions, format_date, format_trillions, validate_date


def _status_from_threshold(value: float, good: float, warn: float, reverse: bool = False) -> str:
    if reverse:
        if value <= good:
            return "안정"
        if value <= warn:
            return "주의"
        return "위험"
    if value >= good:
        return "안정"
    if value >= warn:
        return "주의"
    return "위험"


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


def _safe_indicator(builder: Callable[[], dict], fallback: dict, error_note: str | None = None) -> dict:
    try:
        return builder()
    except Exception as exc:  # pylint: disable=broad-except
        _ = exc
        if error_note:
            fallback["비고"] = error_note
        else:
            fallback["비고"] = "데이터 조회 실패로 N/A 처리"
        return fallback


def indicator_vix() -> dict:
    fallback = default_indicator("VIX", "일간", "FRED (VIXCLS)", "변동성 지수")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["VIX"])
        date, value = latest_point(series)
        status = _status_from_threshold(value, good=20, warn=30, reverse=True)
        return _build("VIX", "일간", "FRED (VIXCLS)", "낮을수록 안정", f"{value:.2f}", status, date)

    return _safe_indicator(_run, fallback)


def indicator_10y2y() -> dict:
    fallback = default_indicator("10Y-2Y 스프레드", "일간", "FRED (T10Y2Y)", "장단기 금리차")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["10Y2Y"])
        date, value = latest_point(series)
        status = "안정" if value > 0 else "주의" if value > -0.5 else "위험"
        return _build("10Y-2Y 스프레드", "일간", "FRED (T10Y2Y)", "음수 심화 시 경기 우려", f"{value:.2f}%p", status, date)

    return _safe_indicator(_run, fallback)


def indicator_fed_balance() -> dict:
    fallback = default_indicator("연준 대차대조표", "주간", "FRED (WALCL)", "연준 총자산")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["FED_BALANCE"])
        date, value = latest_point(series)
        return _build("연준 대차대조표", "주간", "FRED (WALCL)", "저빈도 지표", format_trillions(value), "안정", date)

    return _safe_indicator(_run, fallback)


def _apply_reserve_stale_policy(result: dict, ref_date: pd.Timestamp) -> dict:
    is_fresh, lag_days = validate_date(ref_date, "주간")
    strict_fresh = lag_days <= 9
    if (not is_fresh) or (not strict_fresh):
        result["상태"] = "데이터 지연"
        result["비고"] = f"지급준비금 최신 기준일 지연({lag_days}일)으로 데이터 지연 처리"
    return result


def indicator_reserve_balances() -> dict:
    fallback = default_indicator("지급준비금", "주간", "FRED (WRESBAL)", "연준 지급준비금 시리즈")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["RESERVE_BALANCES"])
        date, value = latest_point(series)
        status = "안정" if value >= 3_000_000 else "주의" if value >= 2_500_000 else "위험"
        result = _build("지급준비금", "주간", "FRED (WRESBAL)", "백만 달러 기준", format_trillions(value), status, date)
        return _apply_reserve_stale_policy(result, date)

    return _safe_indicator(_run, fallback)


def indicator_reserve_balances_wow() -> dict:
    fallback = default_indicator("지급준비금 주간 변화", "주간", "FRED (WRESBAL)", "동일 지급준비금 시리즈 기반 주간 변화")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["RESERVE_BALANCES"])
        date, value = latest_point(series)
        prev = previous_point(series)
        if prev is None:
            raise DataFetchError("직전 데이터 부족")
        delta = value - prev[1]
        status = "안정" if delta >= 0 else "주의" if delta >= -100_000 else "위험"
        result = _build("지급준비금 주간 변화", "주간", "FRED (WRESBAL)", "백만 달러 기준 증감", f"{delta / 1_000:.2f}십억 달러", status, date)
        return _apply_reserve_stale_policy(result, date)

    return _safe_indicator(_run, fallback)


def indicator_rrp() -> dict:
    fallback = default_indicator("RRP", "일간", "FRED (RRPONTSYD)", "역레포 잔액")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["RRP"])
        date, value = latest_point(series)
        status = "안정" if value <= 300_000 else "주의" if value <= 700_000 else "위험"
        return _build("RRP", "일간", "FRED (RRPONTSYD)", "백만 달러 기준", format_trillions(value), status, date)

    return _safe_indicator(_run, fallback)


def indicator_tga() -> dict:
    fallback = default_indicator("TGA", "주간", "FRED (WTREGEN)", "재무부 일반계정")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["TGA"])
        date, value = latest_point(series)
        status = "주의" if value >= 900_000 else "안정" if value >= 300_000 else "위험"
        return _build("TGA", "주간", "FRED (WTREGEN)", "백만 달러 기준", format_billions(value), status, date)

    return _safe_indicator(_run, fallback)


def indicator_tga_wow() -> dict:
    fallback = default_indicator("TGA 주간 변화", "주간", "FRED (WTREGEN)", "동일 시리즈 주간 변화")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["TGA"])
        weekly = series.resample("W-FRI").last().dropna()
        date, value = latest_point(weekly)
        prev = previous_point(weekly)
        if prev is None:
            raise DataFetchError("직전 주간 데이터 부족")
        delta = value - prev[1]
        status = "주의" if delta >= 100_000 else "안정" if delta >= -100_000 else "위험"
        return _build("TGA 주간 변화", "주간", "FRED (WTREGEN)", "백만 달러 기준 주간 증감", f"{delta / 1_000:.2f}십억 달러", status, date)

    return _safe_indicator(_run, fallback)


def indicator_hy_spread() -> dict:
    fallback = default_indicator("하이일드 스프레드", "일간", "FRED (BAMLH0A0HYM2)", "회사채 신용스프레드")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["HY_SPREAD"])
        date, value = latest_point(series)
        status = "안정" if value <= 4 else "주의" if value <= 6 else "위험"
        return _build("하이일드 스프레드", "일간", "FRED (BAMLH0A0HYM2)", "낮을수록 신용환경 양호", f"{value:.2f}%p", status, date)

    return _safe_indicator(_run, fallback)


def indicator_sofr_effr() -> dict:
    fallback = default_indicator("SOFR-EFFR 스프레드", "일간", "FRED (SOFR, DFF)", "단기자금시장 괴리")

    def _run() -> dict:
        sofr = fetch_fred_series(FRED_SERIES["SOFR"])
        effr = fetch_fred_series(FRED_SERIES["EFFR"])
        combined = pd.concat([sofr.rename("sofr"), effr.rename("effr")], axis=1).dropna()
        date = combined.index.max()
        spread = float(combined.loc[date, "sofr"] - combined.loc[date, "effr"])
        abs_spread = abs(spread)
        status = "안정" if abs_spread <= 0.05 else "주의" if abs_spread <= 0.15 else "위험"
        return _build("SOFR-EFFR 스프레드", "일간", "FRED (SOFR, DFF)", "절대값 기준", f"{spread:.3f}%p", status, pd.Timestamp(date))

    return _safe_indicator(_run, fallback)


def indicator_sofr_iorb() -> dict:
    fallback = default_indicator("SOFR-IORB 스프레드", "일간", "FRED (SOFR, IORB)", "정책금리 하단 괴리")

    def _run() -> dict:
        sofr = fetch_fred_series(FRED_SERIES["SOFR"])
        iorb = fetch_fred_series(FRED_SERIES["IORB"])
        combined = pd.concat([sofr.rename("sofr"), iorb.rename("iorb")], axis=1).dropna()
        date = combined.index.max()
        spread = float(combined.loc[date, "sofr"] - combined.loc[date, "iorb"])
        abs_spread = abs(spread)
        status = "안정" if abs_spread <= 0.1 else "주의" if abs_spread <= 0.2 else "위험"
        return _build("SOFR-IORB 스프레드", "일간", "FRED (SOFR, IORB)", "절대값 기준", f"{spread:.3f}%p", status, pd.Timestamp(date))

    return _safe_indicator(_run, fallback)


def optional_mmf_total() -> dict:
    fallback = default_indicator("MMF 총자산", "주간", "FRED (WMMFSL)", "선택 지표")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        date, value = latest_point(series)
        return _build("MMF 총자산", "주간", "FRED (WMMFSL)", "백만 달러 기준", format_trillions(value), "저빈도", date)

    return _safe_indicator(_run, fallback, "공식/안정적 소스 미확인으로 N/A 처리")


def optional_mmf_vs_rrp() -> dict:
    fallback = default_indicator("MMF 대비 RRP", "주간", "FRED (WMMFSL, RRPONTSYD)", "선택 지표")

    def _run() -> dict:
        mmf = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        rrp = fetch_fred_series(FRED_SERIES["RRP"])
        mmf_w = mmf.resample("W-FRI").last().dropna().rename("mmf")
        rrp_w = rrp.resample("W-FRI").last().dropna().rename("rrp")
        combined = pd.concat([mmf_w, rrp_w], axis=1).dropna()
        date = combined.index.max()
        rrp_val = combined.loc[date, "rrp"]
        if rrp_val == 0:
            raise DataFetchError("RRP 값이 0")
        ratio = float(combined.loc[date, "mmf"] / rrp_val)
        status = "안정" if ratio >= 10 else "주의" if ratio >= 5 else "위험"
        return _build("MMF 대비 RRP", "주간", "FRED (WMMFSL, RRPONTSYD)", "배수", f"{ratio:.2f}배", status, pd.Timestamp(date))

    return _safe_indicator(_run, fallback, "공식/안정적 소스 미확인으로 N/A 처리")


def optional_mmf_wow() -> dict:
    fallback = default_indicator("MMF 주간 변화", "주간", "FRED (WMMFSL)", "선택 지표")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["MMF_TOTAL"])
        date, value = latest_point(series)
        prev = previous_point(series)
        if prev is None:
            raise DataFetchError("직전 데이터 부족")
        delta = value - prev[1]
        status = "안정" if delta >= 0 else "주의" if delta >= -50_000 else "위험"
        return _build("MMF 주간 변화", "주간", "FRED (WMMFSL)", "백만 달러 기준 증감", f"{delta / 1_000:.2f}십억 달러", status, date)

    return _safe_indicator(_run, fallback, "공식/안정적 소스 미확인으로 N/A 처리")


def optional_fsi() -> dict:
    fallback = default_indicator("금융스트레스지수", "주간", "FRED (STLFSI4)", "선택 지표")

    def _run() -> dict:
        series = fetch_fred_series(FRED_SERIES["FSI"])
        date, value = latest_point(series)
        status = "안정" if value < 0 else "주의" if value < 1 else "위험"
        return _build("금융스트레스지수", "주간", "FRED (STLFSI4)", "0 상회 시 스트레스 증가", f"{value:.2f}", status, date)

    return _safe_indicator(_run, fallback)


def optional_fear_greed() -> dict:
    return default_indicator(
        "공포·탐욕 지수",
        "일간",
        "CNN Fear & Greed",
        "공식·안정적 공개 API 부재로 N/A 처리",
    )


def build_all_indicators() -> list[dict]:
    required = [
        indicator_vix,
        indicator_10y2y,
        indicator_fed_balance,
        indicator_reserve_balances,
        indicator_reserve_balances_wow,
        indicator_rrp,
        indicator_tga,
        indicator_tga_wow,
        indicator_hy_spread,
        indicator_sofr_effr,
        indicator_sofr_iorb,
    ]
    optional = [
        optional_mmf_total,
        optional_mmf_vs_rrp,
        optional_mmf_wow,
        optional_fsi,
        optional_fear_greed,
    ]
    return [fn() for fn in required + optional]

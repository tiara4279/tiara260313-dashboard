# app.py — 섹터 로테이션 분석 대시보드
# 실행: streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import datetime

# ─────────────────────────────────────────────
# 0. 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="급등 섹터 로테이션 대시보드",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1. 샘플 데이터 (테스트용)
# ─────────────────────────────────────────────
SAMPLE_CSV = """date,sector,theme,ticker,name,change
2026-04-15,코로나,백신 진단키트,065560,수젠텍,18.5
2026-04-15,코로나,백신 진단키트,049660,셀리드,15.2
2026-04-15,반도체,머스크 테라팹,093370,후성,12.0
2026-04-15,반도체,머스크 테라팹,139480,에이치엠넥스,9.5
2026-04-15,방산,미이란 협상,100090,STX엔진,11.0
2026-04-15,방산,미이란 협상,093380,퍼스텍,8.2
2026-04-15,우주,K문샷,413640,미래에셋벤처투자,7.3
2026-04-15,우주,K문샷,286750,나노팀,5.1
2026-04-16,코로나,백신 진단키트,065560,수젠텍,22.0
2026-04-16,코로나,백신 진단키트,049660,셀리드,19.5
2026-04-16,코로나,백신 진단키트,019170,신풍제약,16.8
2026-04-16,반도체,머스크 테라팹,093370,후성,20.5
2026-04-16,반도체,머스크 테라팹,139480,에이치엠넥스,18.1
2026-04-16,방산,미이란 협상,100090,STX엔진,25.0
2026-04-16,방산,미이란 협상,093380,퍼스텍,14.2
2026-04-16,통신장비,젠슨황 미래기술,399720,기가레인,22.0
2026-04-16,통신장비,젠슨황 미래기술,082660,빛과전자,18.9
2026-04-16,우주,K문샷,413640,미래에셋벤처투자,12.0
2026-04-17,코로나,백신 진단키트,065560,수젠텍,30.0
2026-04-17,코로나,백신 진단키트,049660,셀리드,29.98
2026-04-17,코로나,백신 진단키트,019170,신풍제약,26.48
2026-04-17,코로나,백신 진단키트,060960,오상헬스케어,25.98
2026-04-17,코로나,백신 진단키트,039470,아이진,23.21
2026-04-17,반도체,머스크 테라팹,093370,후성,22.3
2026-04-17,반도체,머스크 테라팹,139480,에이치엠넥스,20.31
2026-04-17,반도체,머스크 테라팹,153460,고영,11.49
2026-04-17,반도체,머스크 테라팹,034020,두산테스나,11.24
2026-04-17,반도체,장비,166090,케이씨텍,8.07
2026-04-17,방산,미이란 협상,100090,STX엔진,29.99
2026-04-17,방산,미이란 협상,093380,퍼스텍,14.92
2026-04-17,방산,미이란 협상,026040,RF시스템즈,13.17
2026-04-17,방산,미이란 협상,170790,빅텍,12.64
2026-04-17,통신장비,젠슨황 미래기술,399720,기가레인,30.0
2026-04-17,통신장비,젠슨황 미래기술,082660,빛과전자,29.93
2026-04-17,통신장비,젠슨황 미래기술,shown,파이버프로,10.88
2026-04-17,보안,앤트로픽 오퍼스4.7,035600,한국정보통신,23.03
2026-04-17,보안,앤트로픽 오퍼스4.7,163730,파인텍,12.35
2026-04-17,바이오,로봇바이오 4대특구,084990,휴온스글로벌,17.91
2026-04-17,바이오,로봇바이오 4대특구,234920,녹십자웰빙,11.46
2026-04-17,우주,K문샷 데이터센터,413640,미래에셋벤처투자,19.64
2026-04-17,우주,K문샷 데이터센터,286750,나노팀,14.9
2026-04-17,우주,K문샷 데이터센터,035480,아주IB투자,8.75
2026-04-17,2차전지,양극재 수출,042700,엘앤에프,9.09
2026-04-17,2차전지,양극재 수출,006110,이수스페셜티케미컬,8.91
2026-04-17,2차전지,양극재 수출,006400,삼성SDI,7.0
2026-04-17,조선,중동 위기 톤마일,012450,한화엔진,16.39
2026-04-17,조선,중동 위기 톤마일,267250,HD현대마린엔진,5.85
"""

# ─────────────────────────────────────────────
# 2. 데이터 로딩 & 전처리 함수
# ─────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_sample_data() -> pd.DataFrame:
    """내장 샘플 데이터를 DataFrame으로 반환"""
    df = pd.read_csv(StringIO(SAMPLE_CSV))
    df["date"] = pd.to_datetime(df["date"])
    df["change"] = pd.to_numeric(df["change"], errors="coerce")
    return df.dropna(subset=["change"])


def load_uploaded_data(uploaded_files) -> pd.DataFrame:
    """업로드된 CSV 파일(들)을 하나의 DataFrame으로 병합"""
    dfs = []
    for f in uploaded_files:
        try:
            df = pd.read_csv(f)
            required_cols = {"date", "sector", "theme", "ticker", "name", "change"}
            missing = required_cols - set(df.columns)
            if missing:
                st.warning(f"[{f.name}] 필수 컬럼 누락: {missing} — 건너뜀")
                continue
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["change"] = pd.to_numeric(df["change"], errors="coerce")
            df = df.dropna(subset=["date", "change"])
            dfs.append(df)
        except Exception as e:
            st.error(f"[{f.name}] 파싱 오류: {e}")
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True).drop_duplicates()


def validate_dataframe(df: pd.DataFrame) -> bool:
    """DataFrame이 유효한지 확인"""
    if df is None or df.empty:
        return False
    required = {"date", "sector", "change"}
    return required.issubset(df.columns)


# ─────────────────────────────────────────────
# 3. 섹터 강도 계산 함수
# ─────────────────────────────────────────────

def calc_sector_strength(df: pd.DataFrame, date: pd.Timestamp) -> pd.DataFrame:
    """특정 날짜의 섹터별 평균 등락률 계산"""
    day_df = df[df["date"] == date]
    if day_df.empty:
        return pd.DataFrame(columns=["sector", "avg_change", "count", "top_stock", "top_change"])

    grouped = (
        day_df.groupby("sector")
        .agg(
            avg_change=("change", "mean"),
            count=("name", "count"),
        )
        .reset_index()
        .sort_values("avg_change", ascending=False)
    )

    # 섹터별 최고 종목
    top_stocks = (
        day_df.sort_values("change", ascending=False)
        .groupby("sector")
        .first()[["name", "change"]]
        .rename(columns={"name": "top_stock", "change": "top_change"})
        .reset_index()
    )
    result = grouped.merge(top_stocks, on="sector", how="left")
    result["avg_change"] = result["avg_change"].round(2)
    result["top_change"] = result["top_change"].round(2)
    return result


def calc_sector_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """날짜 x 섹터 피벗 테이블 (평균 등락률)"""
    ts = (
        df.groupby(["date", "sector"])["change"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"change": "avg_change"})
    )
    return ts


# ─────────────────────────────────────────────
# 4. 패턴 탐지 함수
# ─────────────────────────────────────────────

def detect_patterns(df: pd.DataFrame, today: pd.Timestamp):
    """
    죽은 섹터: 최근 2일 평균 > 5% AND 오늘 <= 0%
    새로 뜨는 섹터: 전일 평균 < 2% AND 오늘 > 7%
    """
    sorted_dates = sorted(df["date"].unique())
    today_idx = list(sorted_dates).index(today) if today in sorted_dates else -1

    dead_sectors = []
    rising_sectors = []

    if today_idx < 1:
        return dead_sectors, rising_sectors

    yesterday = sorted_dates[today_idx - 1]
    two_days_ago = sorted_dates[today_idx - 2] if today_idx >= 2 else None

    today_avg = (
        df[df["date"] == today]
        .groupby("sector")["change"].mean()
    )
    yesterday_avg = (
        df[df["date"] == yesterday]
        .groupby("sector")["change"].mean()
    )

    # 죽은 섹터
    if two_days_ago is not None:
        two_days_avg = (
            df[df["date"] == two_days_ago]
            .groupby("sector")["change"].mean()
        )
        for sector in today_avg.index:
            t = today_avg.get(sector, None)
            y = yesterday_avg.get(sector, None)
            td = two_days_avg.get(sector, None)
            if t is not None and y is not None and td is not None:
                recent2_avg = (y + td) / 2
                if recent2_avg > 5 and t <= 0:
                    dead_sectors.append({
                        "sector": sector,
                        "recent_2d_avg": round(recent2_avg, 2),
                        "today_avg": round(t, 2),
                    })

    # 새로 뜨는 섹터
    for sector in today_avg.index:
        t = today_avg.get(sector, None)
        y = yesterday_avg.get(sector, None)
        if t is not None and (y is None or y < 2) and t > 7:
            rising_sectors.append({
                "sector": sector,
                "yesterday_avg": round(y, 2) if y is not None else 0.0,
                "today_avg": round(t, 2),
            })

    return dead_sectors, rising_sectors


# ─────────────────────────────────────────────
# 5. 차트 렌더 함수
# ─────────────────────────────────────────────

SECTOR_COLORS = px.colors.qualitative.Bold


def render_strength_bar(strength_df: pd.DataFrame, title: str = "섹터 강도 (평균 등락률 %)"):
    """섹터 강도 가로 바 차트"""
    if strength_df.empty:
        st.info("해당 날짜의 섹터 데이터가 없습니다.")
        return

    fig = go.Figure()
    colors = [
        f"rgba(220,50,50,0.85)" if v >= 0 else "rgba(50,100,220,0.85)"
        for v in strength_df["avg_change"]
    ]
    fig.add_trace(
        go.Bar(
            x=strength_df["avg_change"],
            y=strength_df["sector"],
            orientation="h",
            marker_color=colors,
            text=[f"+{v}%" if v >= 0 else f"{v}%" for v in strength_df["avg_change"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "평균 등락률: %{x:.2f}%<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#1a1a2e")),
        xaxis=dict(
            title="평균 등락률 (%)",
            zeroline=True,
            zerolinecolor="#888",
            ticksuffix="%",
        ),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="#f8f9fc",
        paper_bgcolor="#f8f9fc",
        height=max(300, len(strength_df) * 42),
        margin=dict(l=10, r=60, t=50, b=30),
        font=dict(family="Noto Sans KR, sans-serif", size=13),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_flow_line(ts_df: pd.DataFrame, selected_sectors: list):
    """섹터 흐름 라인 차트 (핵심)"""
    if ts_df.empty:
        st.info("흐름 분석을 위한 데이터가 부족합니다.")
        return

    filtered = ts_df[ts_df["sector"].isin(selected_sectors)] if selected_sectors else ts_df

    fig = px.line(
        filtered,
        x="date",
        y="avg_change",
        color="sector",
        markers=True,
        labels={"avg_change": "평균 등락률 (%)", "date": "날짜", "sector": "섹터"},
        color_discrete_sequence=SECTOR_COLORS,
        hover_data={"avg_change": ":.2f"},
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#aaa",
        annotation_text="기준선(0%)",
        annotation_position="bottom right",
    )
    fig.add_hrect(y0=7, y1=filtered["avg_change"].max() + 5 if not filtered.empty else 35,
                  fillcolor="rgba(220,50,50,0.04)", line_width=0,
                  annotation_text="강세 구간", annotation_position="top right")
    fig.update_layout(
        title=dict(text="섹터 로테이션 흐름 차트", font=dict(size=17, color="#1a1a2e")),
        plot_bgcolor="#f8f9fc",
        paper_bgcolor="#f8f9fc",
        legend=dict(
            orientation="v",
            x=1.01,
            y=1,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#ddd",
            borderwidth=1,
        ),
        xaxis=dict(showgrid=True, gridcolor="#e0e0e0", tickformat="%m/%d"),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            ticksuffix="%",
            zeroline=True,
            zerolinecolor="#888",
        ),
        height=460,
        margin=dict(l=10, r=160, t=55, b=30),
        font=dict(family="Noto Sans KR, sans-serif", size=13),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sector_table(df: pd.DataFrame, date: pd.Timestamp, sector_filter: list):
    """섹터별 종목 테이블"""
    day_df = df[df["date"] == date].copy()
    if sector_filter:
        day_df = day_df[day_df["sector"].isin(sector_filter)]
    if day_df.empty:
        st.info("선택한 날짜/섹터에 데이터가 없습니다.")
        return

    day_df = day_df.sort_values(["sector", "change"], ascending=[True, False])
    day_df["change_str"] = day_df["change"].apply(
        lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%"
    )
    display_df = day_df[["sector", "theme", "ticker", "name", "change_str"]].rename(
        columns={
            "sector": "섹터",
            "theme": "이슈/테마",
            "ticker": "종목코드",
            "name": "종목명",
            "change_str": "등락률",
        }
    )

    # 섹터별 색 구분 렌더
    sectors = display_df["섹터"].unique()
    for sec in sectors:
        sec_df = display_df[display_df["섹터"] == sec].reset_index(drop=True)
        avg = day_df[day_df["sector"] == sec]["change"].mean()
        avg_str = f"+{avg:.2f}%" if avg >= 0 else f"{avg:.2f}%"
        color = "#dc3232" if avg >= 0 else "#2264dc"
        st.markdown(
            f"""
            <div style='
                display:flex; align-items:center; gap:10px;
                margin: 18px 0 6px 0;
            '>
                <span style='
                    font-size:15px; font-weight:700;
                    color:{color}; background:rgba(220,50,50,0.08);
                    padding:3px 12px; border-radius:20px;
                    border:1.5px solid {color};
                '>{sec}</span>
                <span style='font-size:13px; color:#666;'>섹터 평균: <b style="color:{color}">{avg_str}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            sec_df.drop(columns=["섹터"]),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────────────────────────
# 6. 사이드바 구성 함수
# ─────────────────────────────────────────────

def build_sidebar(df: pd.DataFrame):
    """사이드바: 날짜 선택 + 섹터 필터 반환"""
    st.sidebar.markdown(
        """
        <div style='text-align:center; padding:8px 0 16px 0;'>
            <div style='font-size:20px; font-weight:800; color:#1a1a2e;'>
                급등 섹터 분석
            </div>
            <div style='font-size:12px; color:#888; margin-top:2px;'>
                Sector Rotation Dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    available_dates = sorted(df["date"].unique(), reverse=True)
    date_options = [d.strftime("%Y-%m-%d") for d in available_dates]

    selected_date_str = st.sidebar.selectbox(
        "분석 날짜 선택",
        options=date_options,
        index=0,
        help="오늘 기준 분석에 사용할 날짜",
    )
    selected_date = pd.Timestamp(selected_date_str)

    st.sidebar.markdown("---")
    all_sectors = sorted(df["sector"].unique().tolist())
    selected_sectors = st.sidebar.multiselect(
        "섹터 필터 (비워두면 전체)",
        options=all_sectors,
        default=[],
        help="흐름 차트 및 테이블에 적용됩니다",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='font-size:11px; color:#aaa; text-align:center;'>"
        f"총 {len(df)}행 | {df['date'].nunique()}일치 | {df['sector'].nunique()}개 섹터"
        f"</div>",
        unsafe_allow_html=True,
    )

    return selected_date, selected_sectors


# ─────────────────────────────────────────────
# 7. 패턴 탐지 렌더 함수
# ─────────────────────────────────────────────

def render_patterns(dead: list, rising: list):
    """패턴 탐지 결과 UI 렌더"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<div style='font-size:15px; font-weight:700; color:#c0392b; margin-bottom:8px;'>"
            "[ 죽은 섹터 ] — 과열 후 소멸</div>",
            unsafe_allow_html=True,
        )
        if not dead:
            st.success("감지된 죽은 섹터 없음")
        else:
            for item in dead:
                st.markdown(
                    f"""
                    <div style='
                        background:#fff5f5; border-left:4px solid #e74c3c;
                        padding:10px 14px; border-radius:6px; margin-bottom:8px;
                        font-size:13px;
                    '>
                        <b style="color:#c0392b">{item['sector']}</b><br>
                        최근 2일 평균: <b>+{item['recent_2d_avg']}%</b>
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        오늘: <b style="color:#2980b9">{item['today_avg']}%</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col2:
        st.markdown(
            "<div style='font-size:15px; font-weight:700; color:#27ae60; margin-bottom:8px;'>"
            "[ 새로 뜨는 섹터 ] — 폭발적 급등</div>",
            unsafe_allow_html=True,
        )
        if not rising:
            st.info("감지된 신흥 섹터 없음")
        else:
            for item in rising:
                st.markdown(
                    f"""
                    <div style='
                        background:#f0fff4; border-left:4px solid #27ae60;
                        padding:10px 14px; border-radius:6px; margin-bottom:8px;
                        font-size:13px;
                    '>
                        <b style="color:#27ae60">{item['sector']}</b><br>
                        전일 평균: <b>{item['yesterday_avg']}%</b>
                        &nbsp;&nbsp;|&nbsp;&nbsp;
                        오늘: <b style="color:#e74c3c">+{item['today_avg']}%</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────
# 8. 메인 앱 진입점
# ─────────────────────────────────────────────

def main():
    # ── 헤더
    st.markdown(
        """
        <div style='
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
            padding: 28px 32px 20px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
        '>
            <div style='font-size:26px; font-weight:800; color:#e8e8f0; letter-spacing:-0.5px;'>
                급등 이슈 섹터 로테이션 대시보드
            </div>
            <div style='font-size:13px; color:#a0a8c0; margin-top:6px;'>
                Daily Market Brief — Sector Strength &amp; Rotation Analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── CSV 업로드
    with st.expander("CSV 파일 업로드 (여러 파일 동시 업로드 가능)", expanded=False):
        st.markdown(
            "**필수 컬럼**: `date`, `sector`, `theme`, `ticker`, `name`, `change`"
        )
        uploaded_files = st.file_uploader(
            "CSV 파일 선택",
            type=["csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

    # ── 데이터 로딩
    use_sample = True
    df = pd.DataFrame()

    if uploaded_files:
        df_uploaded = load_uploaded_data(uploaded_files)
        if validate_dataframe(df_uploaded):
            df = df_uploaded
            use_sample = False
            st.success(f"업로드 완료: {len(df)}행 로드됨")
        else:
            st.warning("업로드 데이터 오류. 샘플 데이터로 대체합니다.")

    if use_sample:
        df = load_sample_data()
        st.info("샘플 데이터로 실행 중입니다. CSV를 업로드하면 실제 데이터로 전환됩니다.")

    if not validate_dataframe(df):
        st.error("유효한 데이터가 없습니다. CSV 파일을 확인해주세요.")
        st.stop()

    # ── 사이드바
    selected_date, selected_sectors = build_sidebar(df)

    # ── 오늘 날짜 기준 섹터 강도
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:18px; font-weight:700; color:#1a1a2e; margin-bottom:4px;'>"
        f"TODAY: {selected_date.strftime('%Y-%m-%d')} 기준 섹터 강도</div>",
        unsafe_allow_html=True,
    )

    strength_df = calc_sector_strength(df, selected_date)

    if not strength_df.empty:
        # ── KPI: TOP5 섹터
        top5 = strength_df.head(5)
        cols = st.columns(len(top5))
        for i, (_, row) in enumerate(top5.iterrows()):
            sign = "+" if row["avg_change"] >= 0 else ""
            color = "#dc3232" if row["avg_change"] >= 0 else "#2264dc"
            cols[i].markdown(
                f"""
                <div style='
                    background:#fff; border:1.5px solid {color};
                    border-radius:10px; padding:14px 10px; text-align:center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                '>
                    <div style='font-size:14px; font-weight:700; color:#1a1a2e;'>
                        {row['sector']}
                    </div>
                    <div style='font-size:22px; font-weight:800; color:{color}; margin:6px 0;'>
                        {sign}{row['avg_change']:.2f}%
                    </div>
                    <div style='font-size:11px; color:#888;'>
                        {row['count']}종목 | 대장: {row['top_stock']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # 필터 적용
        display_strength = (
            strength_df[strength_df["sector"].isin(selected_sectors)]
            if selected_sectors
            else strength_df
        )
        render_strength_bar(display_strength)

    # ── 섹터 흐름 라인 차트
    st.markdown("---")
    ts_df = calc_sector_timeseries(df)
    all_sectors_list = ts_df["sector"].unique().tolist()

    flow_sectors = selected_sectors
    st.markdown("---")
    st.markdown(
        "<div style='font-size:18px; font-weight:700; color:#1a1a2e; margin-bottom:12px;'>"
        "패턴 탐지</div>",
        unsafe_allow_html=True,
    )
    dead_sectors, rising_sectors = detect_patterns(df, selected_date)
    render_patterns(dead_sectors, rising_sectors)

    # ── 섹터별 종목 테이블
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:18px; font-weight:700; color:#1a1a2e; margin-bottom:4px;'>"
        f"{selected_date.strftime('%Y-%m-%d')} 섹터별 종목 상세</div>",
        unsafe_allow_html=True,
    )
    render_sector_table(df, selected_date, selected_sectors)

    # ── 원본 데이터 다운로드
    st.markdown("---")
    csv_export = df.copy()
    csv_export["date"] = csv_export["date"].dt.strftime("%Y-%m-%d")
    st.download_button(
        label="전체 데이터 CSV 다운로드",
        data=csv_export.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"sector_data_{datetime.date.today()}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()

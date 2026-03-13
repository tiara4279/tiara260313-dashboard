from __future__ import annotations

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from indicators import build_all_indicators

load_dotenv()

st.set_page_config(page_title="미국 유동성·리스크 대시보드", layout="wide")
st.title("미국 유동성·리스크 대시보드")
st.caption("최신 공개 데이터 기반으로 미국 유동성/리스크 지표를 점검합니다.")

indicators = build_all_indicators()
df = pd.DataFrame(indicators)

status_counts = df["상태"].value_counts()
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 지표", len(df))
col2.metric("위험", int(status_counts.get("위험", 0)))
col3.metric("주의", int(status_counts.get("주의", 0)))
col4.metric("데이터 지연/N/A", int(status_counts.get("데이터 지연", 0) + status_counts.get("N/A", 0)))

st.subheader("핵심 지표 카드")
for i in range(0, len(indicators), 3):
    cols = st.columns(3)
    chunk = indicators[i : i + 3]
    for col, item in zip(cols, chunk):
        col.markdown(
            f"""
### {item['지표']}
- **값:** {item['값']}
- **상태:** {item['상태']}
- **주기:** {item['주기']}
- **최신 기준일:** {item['최신 기준일']}
- **출처:** {item['출처']}
- **비고:** {item['비고']}
"""
        )

st.subheader("전체 지표 표")
st.dataframe(
    df[["지표", "값", "상태", "주기", "최신 기준일", "출처", "비고"]],
    use_container_width=True,
    hide_index=True,
)

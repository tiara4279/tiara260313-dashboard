# tiara260313-dashboard

## 미국 유동성·리스크 대시보드

개인용 일일 모니터링을 위한 Streamlit 대시보드입니다. 데이터 정확성을 우선하며, 각 지표는 최신 기준일과 주기 기반 지연 여부를 명시합니다.

## 기술 스택
- Python
- Streamlit
- pandas
- requests
- python-dotenv

## 실행 방법
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 지표 구성
### 필수 지표
- VIX (FRED: VIXCLS)
- 10Y-2Y 스프레드 (FRED: T10Y2Y)
- 연준 대차대조표 (FRED: WALCL)
- 지급준비금 (FRED: TOTRESNS)
- 지급준비금 주간 변화 (FRED: TOTRESNS)
- RRP (FRED: RRPONTSYD)
- TGA (FRED: WTREGEN)
- TGA 주간 변화 (FRED: WTREGEN)
- 하이일드 스프레드 (FRED: BAMLH0A0HYM2)
- SOFR-EFFR 스프레드 (FRED: SOFR, DFF)
- SOFR-IORB 스프레드 (FRED: SOFR, IORB)

### 선택 지표
- MMF 총자산 (FRED: WMMFSL)
- MMF 대비 RRP (FRED: WMMFSL, RRPONTSYD)
- MMF 주간 변화 (FRED: WMMFSL)
- 금융스트레스지수 (FRED: STLFSI4)
- 공포·탐욕 지수 (공식/안정 API 부재로 기본 N/A)

## 데이터 검증 원칙
- 일간/주간/월간(저빈도 포함) 주기별 허용 지연일을 별도로 검증합니다.
- 허용 지연일을 초과하면 상태를 `데이터 지연`으로 강제 표기합니다.
- 일부 지표 조회 실패 시 앱 전체를 중단하지 않고 해당 지표를 `N/A`로 표시합니다.
- 종료/유지보수 중인 구(舊) 시리즈를 최신값처럼 표시하지 않습니다.

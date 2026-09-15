import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/seoul.csv"
)

# 제목
st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write("서울의 일별 기온 데이터를 이용해 연평균 기온의 변화를 살펴봅니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 분석에 필요한 데이터만 남김
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


df = load_data()

# 연도별 유효한 관측일 수 계산
year_count = (
    df.groupby("연도")["평균기온"]
    .count()
    .reset_index(name="관측일수")
)

# 300일 이상 자료가 있는 해를 완전한 연도로 간주
complete_years = year_count.loc[
    year_count["관측일수"] >= 300, "연도"
]

# 최근 100개의 완전한 연도 선택
selected_years = complete_years.sort_values().tail(100).tolist()

annual_temp = (
    df[df["연도"].isin(selected_years)]
    .groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

annual_temp["연도"] = annual_temp["연도"].astype(str)
annual_temp = annual_temp.set_index("연도")

# 주요 정보
start_year = selected_years[0]
end_year = selected_years[-1]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("분석 기간", f"{start_year}~{end_year}")

with col2:
    st.metric("분석 연도 수", f"{len(selected_years)}년")

with col3:
    change = (
        annual_temp["평균기온"].iloc[-1]
        - annual_temp["평균기온"].iloc[0]
    )
    st.metric("첫해 대비 마지막 해", f"{change:+.1f}℃")

# 그래프
st.subheader("연도별 평균기온")

st.line_chart(
    annual_temp,
    y="평균기온",
    x_label="연도",
    y_label="평균기온 (℃)",
    use_container_width=True
)

st.caption(
    "※ 각 연도의 일별 평균기온을 평균하여 연평균 기온을 계산했습니다. "
    "연간 300일 이상 관측된 해만 분석 대상으로 사용했습니다."
)

# 원자료 보기
with st.expander("연도별 평균기온 데이터 보기"):
    display_df = annual_temp.reset_index()
    display_df.columns = ["연도", "평균기온 (℃)"]
    display_df["평균기온 (℃)"] = display_df["평균기온 (℃)"].round(2)
    st.dataframe(display_df, use_container_width=True)

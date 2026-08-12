from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# 기본 경로
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# 금리 데이터 로딩
# =====================================================

@st.cache_data
def load_interest_rate():

    data_path = (
        BASE_DIR
        / "data"
        / "interest_rate.csv"
    )

    # =================================================
    # CSV 읽기
    # =================================================

    try:

        df = pd.read_csv(
            data_path,
            encoding="utf-8-sig",
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            data_path,
            encoding="cp949",
        )

    # =================================================
    # 컬럼명 정리
    # =================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # =================================================
    # 필요한 컬럼 확인
    # =================================================

    required_cols = [
        "년월",
        "정부대출금금리",
    ]

    missing_cols = [
        col
        for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:

        raise ValueError(
            "interest_rate.csv에 "
            f"필요한 컬럼이 없습니다: {missing_cols}"
        )

    # =================================================
    # 날짜 변환
    #
    # 실제 데이터:
    #
    # Jan.16
    # Feb.16
    # Mar.16
    #
    # → 2016-01-01
    # → 2016-02-01
    # → 2016-03-01
    # =================================================

    df["년월"] = (
        df["년월"]
        .astype(str)
        .str.strip()
    )

    df["년월"] = pd.to_datetime(
        df["년월"],
        format="%b.%y",
        errors="coerce",
    )

    # =================================================
    # 금리 숫자 변환
    # =================================================

    df["정부대출금금리"] = pd.to_numeric(
        df["정부대출금금리"],
        errors="coerce",
    )

    # =================================================
    # 유효 데이터만 사용
    # =================================================

    df = df.dropna(
        subset=[
            "년월",
            "정부대출금금리",
        ]
    ).copy()

    # =================================================
    # 날짜순 정렬
    # =================================================

    df = (
        df
        .sort_values("년월")
        .reset_index(drop=True)
    )

    return df


# =====================================================
# 금리 UI
# =====================================================

def render_interest_rate():

    st.markdown(
        "### 📈 최근 6개월 정부대출금금리"
    )

    st.caption(
        "월별 정부대출금금리 흐름을 참고 지표로 제공합니다."
    )

    # =================================================
    # 데이터 불러오기
    # =================================================

    try:

        df = load_interest_rate()

    except FileNotFoundError:

        st.warning(
            "⚠️ interest_rate.csv 파일을 찾을 수 없습니다."
        )

        return

    except Exception:

        st.warning(
            "⚠️ 금리 데이터를 불러올 수 없습니다."
        )

        return

    # =================================================
    # 데이터가 없는 경우
    # =================================================

    if df.empty:

        st.info(
            "금리 데이터가 없습니다."
        )

        return

    # =================================================
    # 최근 6개월
    #
    # 10년치 데이터 중 가장 최근 6개월
    # =================================================

    recent = (
        df
        .tail(6)
        .copy()
    )

    # =================================================
    # 현재 금리
    # =================================================

    current_rate = recent[
        "정부대출금금리"
    ].iloc[-1]

    current_date = recent[
        "년월"
    ].iloc[-1]

    # =================================================
    # 6개월 전 금리
    # =================================================

    first_rate = recent[
        "정부대출금금리"
    ].iloc[0]

    change = current_rate - first_rate

    # =================================================
    # 상단 요약
    # =================================================

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "최근 금리",
            f"{current_rate:.3f}%",
            help=(
                f"{current_date.strftime('%Y년 %m월')} "
                "기준"
            ),
        )

    with col2:

        st.metric(
            "6개월 전 대비",
            f"{change:+.3f}%p",
            delta_color="inverse",
        )

    # =================================================
    # 금리 차트
    #
    # 문자열 표시월을 만들지 않고
    # datetime 자체를 x축으로 사용
    # =================================================

    fig = px.line(
        recent,
        x="년월",
        y="정부대출금금리",
        markers=True,
    )

    # =================================================
    # 선 / 마커 스타일
    # =================================================

    fig.update_traces(

        line=dict(
            color="#2563EB",
            width=3,
        ),

        marker=dict(
            size=8,
            color="#2563EB",
        ),

        hovertemplate=(
            "%{x|%Y.%m}<br>"
            "정부대출금금리: %{y:.3f}%"
            "<extra></extra>"
        ),
    )

    # =================================================
    # 차트 스타일
    # =================================================

    fig.update_layout(

        height=280,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),

        xaxis_title=None,

        yaxis_title=None,

        showlegend=False,

        hovermode="x unified",

        plot_bgcolor="white",

        paper_bgcolor="white",
    )

    # =================================================
    # Y축
    # =================================================

    fig.update_yaxes(

        ticksuffix="%",
        
        showgrid=True,

        gridcolor="#EEF1F5",

        tickformat=".3f",
    )

    # =================================================
    # X축
    #
    # 2025.07 같은 날짜 형식으로 표시
    # =================================================

    fig.update_xaxes(

        showgrid=False,

        tickformat="%Y.%m",

        dtick="M1",

        tickangle=0,
    )

    # =================================================
    # 차트 출력
    # =================================================

    st.plotly_chart(

        fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        },
    )

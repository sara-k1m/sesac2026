# interest_rate.py
# components/interest_rate.py

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


@st.cache_data
def load_interest_rate():

    data_path = (
        BASE_DIR
        / "data"
        / "interest_rate.csv"
    )

    df = pd.read_csv(
        data_path,
        encoding="utf-8-sig"
    )

    # =====================================================
    # 날짜 변환
    # 예: 16.Jan → 2016-01-01
    # =====================================================

    df["년월"] = pd.to_datetime(
        df["년월"],
        format="%y.%b",
        errors="coerce"
    )

    # =====================================================
    # 금리 숫자 변환
    # =====================================================

    df["정부대출금금리"] = pd.to_numeric(
        df["정부대출금금리"],
        errors="coerce"
    )

    # =====================================================
    # 유효 데이터만 사용
    # =====================================================

    df = df.dropna(
        subset=[
            "년월",
            "정부대출금금리"
        ]
    ).copy()

    # 날짜순 정렬
    df = df.sort_values("년월")

    return df


def render_interest_rate():

    st.markdown(
        "### 📈 최근 6개월 정부대출금금리"
    )

    st.caption(
        "월별 정부대출금금리 흐름을 참고 지표로 제공합니다."
    )

    try:

        df = load_interest_rate()

    except FileNotFoundError:

        st.warning(
            "⚠️ interest_rate.csv 파일을 찾을 수 없습니다."
        )

        return

    # =====================================================
    # 최근 6개월
    # =====================================================

    recent = (
        df
        .tail(6)
        .copy()
    )

    if len(recent) == 0:

        st.info(
            "금리 데이터를 불러올 수 없습니다."
        )

        return

    # =====================================================
    # 현재 금리
    # =====================================================

    current_rate = recent[
        "정부대출금금리"
    ].iloc[-1]

    current_date = recent[
        "년월"
    ].iloc[-1]

    # =====================================================
    # 6개월 전 금리
    # =====================================================

    first_rate = recent[
        "정부대출금금리"
    ].iloc[0]

    change = current_rate - first_rate

    # =====================================================
    # 상단 요약
    # =====================================================

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

    # =====================================================
    # 차트용 날짜 표시
    # =====================================================

    recent["표시월"] = recent[
        "년월"
    ].dt.strftime("%y.%m")

    # =====================================================
    # 금리 차트
    # =====================================================

    fig = px.line(
        recent,
        x="표시월",
        y="정부대출금금리",
        markers=True,
    )

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
            "%{x}<br>"
            "정부대출금금리: %{y:.3f}%"
            "<extra></extra>"
        ),
    )

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

    fig.update_yaxes(
        ticksuffix="%",
        showgrid=True,
        gridcolor="#EEF1F5",
    )

    fig.update_xaxes(
        showgrid=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )
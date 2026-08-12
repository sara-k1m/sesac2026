# charts.py
# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import plotly.express as px


def render_summary(f, min_count):

    st.markdown(
        "#### 💡 조건에 맞는 추천 지역 · 역"
    )

    st.caption(
        f"거래 건수가 {min_count}건 미만인 곳은 "
        "통계 신뢰도가 낮아 제외했습니다."
    )

    # =====================================================
    # 자치구 순위
    # =====================================================

    district_rank = (
        f.groupby("자치구명")
        .agg(
            거래건수=("임대료(만원)", "size"),
            평균월세=("임대료(만원)", "mean"),
            평균보증금=("보증금(만원)", "mean"),
            평균거리=("최근접역_거리(m)", "mean"),
        )
        .reset_index()
    )

    district_rank = (
        district_rank[
            district_rank["거래건수"] >= min_count
        ]
        .sort_values("평균월세")
    )

    # =====================================================
    # 역 순위
    # =====================================================

    station_rank = (
        f.groupby(
            [
                "최근접역",
                "최근접역_호선",
            ]
        )
        .agg(
            거래건수=("임대료(만원)", "size"),
            평균월세=("임대료(만원)", "mean"),
            평균보증금=("보증금(만원)", "mean"),
            평균거리=("최근접역_거리(m)", "mean"),
        )
        .reset_index()
    )

    station_rank = (
        station_rank[
            station_rank["거래건수"] >= min_count
        ]
        .sort_values("평균월세")
    )

    col1, col2 = st.columns(2)

    # =====================================================
    # 자치구 TOP 5
    # =====================================================

    with col1:

        st.markdown(
            "**자치구 TOP 5 (월세 저렴한 순)**"
        )

        if len(district_rank) == 0:

            st.info(
                "조건을 만족하는 자치구가 없습니다."
            )

        else:

            st.dataframe(
                district_rank.head(5).style.format(
                    {
                        "평균월세": "{:.1f}",
                        "평균보증금": "{:,.0f}",
                        "평균거리": "{:.0f}",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )

    # =====================================================
    # 역 TOP 5
    # =====================================================

    with col2:

        st.markdown(
            "**지하철역 TOP 5 (월세 저렴한 순)**"
        )

        if len(station_rank) == 0:

            st.info(
                "조건을 만족하는 역이 없습니다."
            )

        else:

            st.dataframe(
                station_rank.head(5)[
                    [
                        "최근접역",
                        "최근접역_호선",
                        "거래건수",
                        "평균월세",
                        "평균거리",
                    ]
                ].style.format(
                    {
                        "평균월세": "{:.1f}",
                        "평균거리": "{:.0f}",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )

    # =====================================================
    # 가성비 TOP 5
    # =====================================================

    st.markdown(
        "**가성비 TOP 5 "
        "(저렴함 60% + 역세권 40% 가중 점수)**"
    )

    if len(station_rank) == 0:

        st.info(
            "표시할 데이터가 없습니다."
        )

        return

    eff = station_rank.copy()

    if (
        eff["평균월세"].max() > 0
        and eff["평균거리"].max() > 0
    ):

        eff["효율점수"] = (
            (
                eff["평균월세"]
                / eff["평균월세"].max()
            ) * 0.6
            +
            (
                eff["평균거리"]
                / eff["평균거리"].max()
            ) * 0.4
        )

        eff = (
            eff
            .sort_values("효율점수")
            .head(5)
        )

        st.dataframe(
            eff[
                [
                    "최근접역",
                    "최근접역_호선",
                    "거래건수",
                    "평균월세",
                    "평균거리",
                ]
            ].style.format(
                {
                    "평균월세": "{:.1f}",
                    "평균거리": "{:.0f}",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )


# =========================================================
# 지역별 분석
# =========================================================

def render_region_analysis(
    f,
    view_type,
    selected_place,
    distance_order,
):

    if view_type == "district":

        st.markdown(
            "#### 자치구별 평균 월세"
        )

    elif view_type == "line":

        st.markdown(
            f"#### {selected_place} 노선 역별 평균 월세"
        )

    else:

        st.markdown(
            f"#### {selected_place} 주변 월세 분석"
        )

    # =====================================================
    # 메인 차트
    # =====================================================

    if view_type == "district":

        dist_summary = (
            f.groupby("자치구명")
            .agg(
                평균월세=("임대료(만원)", "mean"),
                거래건수=("임대료(만원)", "size"),
            )
            .reset_index()
            .sort_values("평균월세")
        )

        fig = px.bar(
            dist_summary,
            x="평균월세",
            y="자치구명",
            orientation="h",
            color="평균월세",
            color_continuous_scale="Blues",
            labels={
                "평균월세": "평균 월세 (만원)",
                "자치구명": "",
            },
        )

        fig.update_layout(
            height=650,
            coloraxis_showscale=False,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    elif view_type == "line":

        line_summary = (
            f.groupby("최근접역")
            .agg(
                평균월세=("임대료(만원)", "mean"),
                거래건수=("임대료(만원)", "size"),
            )
            .reset_index()
            .sort_values("평균월세")
        )

        fig = px.bar(
            line_summary,
            x="평균월세",
            y="최근접역",
            orientation="h",
            color="평균월세",
            color_continuous_scale="Blues",
            labels={
                "평균월세": "평균 월세 (만원)",
                "최근접역": "지하철역",
            },
        )

        fig.update_layout(
            height=650,
            coloraxis_showscale=False,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        distance_summary = (
            f.groupby("거리구간")
            .agg(
                평균월세=("임대료(만원)", "mean"),
                거래건수=("임대료(만원)", "size"),
            )
            .reset_index()
        )

        distance_summary["거리구간"] = pd.Categorical(
            distance_summary["거리구간"],
            categories=distance_order,
            ordered=True,
        )

        distance_summary = (
            distance_summary
            .sort_values("거리구간")
        )

        fig = px.bar(
            distance_summary,
            x="거리구간",
            y="평균월세",
            color="평균월세",
            color_continuous_scale="Blues",
            labels={
                "거리구간": "역까지 거리",
                "평균월세": "평균 월세 (만원)",
            },
        )

        fig.update_layout(
            height=500,
            coloraxis_showscale=False,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # =====================================================
    # 월세 분포 / 건물 용도
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "#### 월세 분포"
        )

        fig_hist = px.histogram(
            f,
            x="임대료(만원)",
            nbins=30,
        )

        fig_hist.update_layout(
            height=380,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True,
        )

    with c2:

        st.markdown(
            "#### 건물 용도별 거래 비중"
        )

        use_counts = (
            f["건물용도"]
            .value_counts()
            .reset_index()
        )

        use_counts.columns = [
            "건물용도",
            "거래건수",
        ]

        fig_pie = px.pie(
            use_counts,
            names="건물용도",
            values="거래건수",
            hole=0.4,
        )

        fig_pie.update_layout(
            height=380,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True,
        )
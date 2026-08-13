# charts.py
# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 공통 Plotly 설정
# =========================================================

def clean_chart(fig, height=400):
    fig.update_layout(
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# =========================================================
# 요약 · 추천
# =========================================================

def render_summary(f, min_count):

    # =====================================================
    # 추천 데이터 계산
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

    # =====================================================
    # 효율 점수
    # =====================================================

    eff = station_rank.copy()

    if (
        len(eff) > 0
        and eff["평균월세"].max() > 0
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
            .reset_index(drop=True)
        )

    # =====================================================
    # 핵심 추천 3개
    # =====================================================

    col1, col2, col3 = st.columns(3)

    # -----------------------------------------------------
    # 가장 저렴한 지역
    # -----------------------------------------------------

    with col1:

        with st.container(border=True):

            st.markdown(
                "<span style='color:#0f766e; font-weight:700;'>"
                " 가장 저렴한 지역"
                "</span>",
                unsafe_allow_html=True,
            )

            if len(district_rank) > 0:

                best_district = district_rank.iloc[0]

                st.metric(
                    label=best_district["자치구명"],
                    value=f"{best_district['평균월세']:.1f}만원",
                    delta=f"거래 {int(best_district['거래건수']):,}건",
                    delta_color="off",
                )

            else:

                st.info("데이터 없음")

    # -----------------------------------------------------
    # 가장 저렴한 역
    # -----------------------------------------------------

    with col2:

        with st.container(border=True):

            st.markdown(
                "<span style='color:#2563eb; font-weight:700;'>"
                " 가장 저렴한 역"
                "</span>",
                unsafe_allow_html=True,
            )

            if len(station_rank) > 0:

                best_station = station_rank.iloc[0]

                st.metric(
                    label=best_station["최근접역"],
                    value=f"{best_station['평균월세']:.1f}만원",
                    delta=f"거래 {int(best_station['거래건수']):,}건",
                    delta_color="off",
                )

            else:

                st.info("데이터 없음")

    # -----------------------------------------------------
    # 가성비 1위
    # -----------------------------------------------------

    with col3:

        with st.container(border=True):

            st.markdown(
                "<span style='color:#d97706; font-weight:700;'>"
                " 가성비 1위"
                "</span>",
                unsafe_allow_html=True,
            )

            if len(eff) > 0:

                best_eff = eff.iloc[0]

                st.metric(
                    label=best_eff["최근접역"],
                    value=f"{best_eff['평균월세']:.1f}만원",
                    delta=f"역까지 {best_eff['평균거리']:.0f}m",
                    delta_color="off",
                )

            else:

                st.info("데이터 없음")

    # =====================================================
    # TOP 5
    # =====================================================

    st.markdown("")

    col1, col2 = st.columns(2)

    # =====================================================
    # 자치구 TOP 5
    # =====================================================

    with col1:

        with st.container(border=True):

            st.markdown("#### 🏙️ 자치구 TOP 5")

            if len(district_rank) == 0:

                st.info(
                    "조건을 만족하는 자치구가 없습니다."
                )

            else:

                district_display = (
                    district_rank
                    .head(5)
                    [
                        [
                            "자치구명",
                            "거래건수",
                            "평균월세",
                        ]
                    ]
                    .copy()
                )

                district_display.columns = [
                    "지역",
                    "거래",
                    "평균 월세",
                ]

                st.dataframe(
                    district_display.style.format(
                        {
                            "거래": "{:,.0f}",
                            "평균 월세": "{:.1f}만원",
                        }
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

    # =====================================================
    # 역 TOP 5
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown("#### 🚇 지하철역 TOP 5")

            if len(station_rank) == 0:

                st.info(
                    "조건을 만족하는 역이 없습니다."
                )

            else:

                station_display = (
                    station_rank
                    .head(5)
                    [
                        [
                            "최근접역",
                            "최근접역_호선",
                            "거래건수",
                            "평균월세",
                        ]
                    ]
                    .copy()
                )

                station_display.columns = [
                    "역",
                    "노선",
                    "거래",
                    "평균 월세",
                ]

                st.dataframe(
                    station_display.style.format(
                        {
                            "거래": "{:,.0f}",
                            "평균 월세": "{:.1f}만원",
                        }
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

    # =====================================================
    # 가성비 TOP 5
    # =====================================================

    with st.container(border=True):

        st.markdown("#### ⭐ 가성비 TOP 5")

        st.caption(
            "평균 월세 60% + 역까지 거리 40%를 기준으로 계산했습니다."
        )

        if len(eff) == 0:

            st.info("표시할 데이터가 없습니다.")

        else:

            eff_display = (
                eff
                .head(5)
                [
                    [
                        "최근접역",
                        "최근접역_호선",
                        "거래건수",
                        "평균월세",
                        "평균거리",
                    ]
                ]
                .copy()
            )

            eff_display.columns = [
                "역",
                "노선",
                "거래",
                "평균 월세",
                "역까지",
            ]

            st.dataframe(
                eff_display.style.format(
                    {
                        "거래": "{:,.0f}",
                        "평균 월세": "{:.1f}만원",
                        "역까지": "{:,.0f}m",
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

    # =====================================================
    # 제목
    # =====================================================

    if view_type == "district":

        section_title = "자치구별 평균 월세"

    elif view_type == "line":

        section_title = f"{selected_place} 노선 역별 평균 월세"

    else:

        section_title = f"{selected_place} 주변 월세 분석"

    # =====================================================
    # 메인 차트
    # =====================================================

    with st.container(border=True):

        st.markdown(
            f"#### {section_title}"
        )

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

            fig = clean_chart(fig, 650)

            fig.update_layout(
                coloraxis_showscale=False,
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

            fig = clean_chart(fig, 650)

            fig.update_layout(
                coloraxis_showscale=False,
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

            fig = clean_chart(fig, 500)

            fig.update_layout(
                coloraxis_showscale=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    # =====================================================
    # 월세 분포 / 건물 용도
    # =====================================================

    c1, c2 = st.columns(2)

    # =====================================================
    # 월세 분포
    # =====================================================

    with c1:

        with st.container(border=True):

            st.markdown("#### 월세 분포")

            fig_hist = px.histogram(
                f,
                x="임대료(만원)",
                nbins=30,
            )

            fig_hist = clean_chart(fig_hist, 380)

            st.plotly_chart(
                fig_hist,
                use_container_width=True,
            )

    # =====================================================
    # 건물 용도
    # =====================================================

    with c2:

        with st.container(border=True):

            st.markdown("#### 건물 용도별 거래 비중")

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

            fig_pie = clean_chart(fig_pie, 380)

            st.plotly_chart(
                fig_pie,
                use_container_width=True,
            )
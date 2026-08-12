# charts.py
# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import plotly.express as px


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
        .reset_index(drop=True)
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
        .reset_index(drop=True)
    )

    # =====================================================
    # 섹션 제목
    # =====================================================

    st.markdown(
        "#### 💡 지금 조건에서 눈여겨볼 곳"
    )

    st.caption(
        f"거래 건수 {min_count}건 미만인 지역과 역은 "
        "통계 신뢰도를 고려해 추천에서 제외했습니다."
    )

    # =====================================================
    # 추천 카드
    # =====================================================

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # 가장 저렴한 지역
    # -----------------------------------------------------

    with col1:

        if len(district_rank) > 0:

            best_district = district_rank.iloc[0]

            st.markdown(
                f"""
                <div style="
                    padding: 1.2rem 1.3rem;
                    border: 1px solid #E5E7EB;
                    border-radius: 14px;
                    background: #FFFFFF;
                ">

                    <div style="
                        color: #6B7280;
                        font-size: 0.85rem;
                        font-weight: 600;
                        margin-bottom: 0.45rem;
                    ">
                        🏙️ 가장 저렴한 지역
                    </div>

                    <div style="
                        color: #111827;
                        font-size: 1.25rem;
                        font-weight: 750;
                        margin-bottom: 0.3rem;
                    ">
                        {best_district["자치구명"]}
                    </div>

                    <div style="
                        color: #2563EB;
                        font-size: 1rem;
                        font-weight: 700;
                    ">
                        평균 월세 {best_district["평균월세"]:.1f}만원
                    </div>

                    <div style="
                        color: #9CA3AF;
                        font-size: 0.8rem;
                        margin-top: 0.35rem;
                    ">
                        거래 {int(best_district["거래건수"]):,}건
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "조건을 만족하는 자치구가 없습니다."
            )

    # -----------------------------------------------------
    # 가장 저렴한 역
    # -----------------------------------------------------

    with col2:

        if len(station_rank) > 0:

            best_station = station_rank.iloc[0]

            st.markdown(
                f"""
                <div style="
                    padding: 1.2rem 1.3rem;
                    border: 1px solid #E5E7EB;
                    border-radius: 14px;
                    background: #FFFFFF;
                ">

                    <div style="
                        color: #6B7280;
                        font-size: 0.85rem;
                        font-weight: 600;
                        margin-bottom: 0.45rem;
                    ">
                        🚇 가장 저렴한 역
                    </div>

                    <div style="
                        color: #111827;
                        font-size: 1.25rem;
                        font-weight: 750;
                        margin-bottom: 0.3rem;
                    ">
                        {best_station["최근접역"]}
                    </div>

                    <div style="
                        color: #2563EB;
                        font-size: 1rem;
                        font-weight: 700;
                    ">
                        평균 월세 {best_station["평균월세"]:.1f}만원
                    </div>

                    <div style="
                        color: #9CA3AF;
                        font-size: 0.8rem;
                        margin-top: 0.35rem;
                    ">
                        {best_station["최근접역_호선"]}
                        · 역까지 평균 {best_station["평균거리"]:.0f}m
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "조건을 만족하는 역이 없습니다."
            )

    # =====================================================
    # 가성비 추천
    # =====================================================

    if len(station_rank) > 0:

        eff = station_rank.copy()

        max_rent = eff["평균월세"].max()
        max_distance = eff["평균거리"].max()

        if max_rent > 0 and max_distance > 0:

            eff["효율점수"] = (
                (
                    eff["평균월세"]
                    / max_rent
                ) * 0.6
                +
                (
                    eff["평균거리"]
                    / max_distance
                ) * 0.4
            )

            eff = (
                eff
                .sort_values("효율점수")
                .reset_index(drop=True)
            )

            best_eff = eff.iloc[0]

            st.markdown(
                "<div style='height: 1rem;'></div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="
                    padding: 1.25rem 1.3rem;
                    border: 1px solid #DBEAFE;
                    border-radius: 14px;
                    background: #F8FBFF;
                ">

                    <div style="
                        color: #2563EB;
                        font-size: 0.85rem;
                        font-weight: 700;
                        margin-bottom: 0.45rem;
                    ">
                        ⭐ 가성비 추천
                    </div>

                    <div style="
                        color: #111827;
                        font-size: 1.2rem;
                        font-weight: 750;
                    ">
                        {best_eff["최근접역"]}
                    </div>

                    <div style="
                        color: #6B7280;
                        font-size: 0.85rem;
                        margin-top: 0.3rem;
                    ">
                        {best_eff["최근접역_호선"]}
                        · 평균 월세 {best_eff["평균월세"]:.1f}만원
                        · 역까지 {best_eff["평균거리"]:.0f}m
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            # =================================================
            # 전체 순위
            # =================================================

            with st.expander(
                "전체 추천 순위 보기"
            ):

                st.dataframe(
                    eff[
                        [
                            "최근접역",
                            "최근접역_호선",
                            "거래건수",
                            "평균월세",
                            "평균거리",
                        ]
                    ].head(10).style.format(
                        {
                            "평균월세": "{:.1f}",
                            "평균거리": "{:.0f}",
                        }
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

    # =====================================================
    # 자치구 / 역 전체 순위
    # =====================================================

    with st.expander(
        "자치구 · 역 전체 순위 보기"
    ):

        rank_col1, rank_col2 = st.columns(2)

        # -------------------------------------------------
        # 자치구
        # -------------------------------------------------

        with rank_col1:

            st.markdown("**자치구 순위**")

            if len(district_rank) == 0:

                st.info(
                    "표시할 데이터가 없습니다."
                )

            else:

                st.dataframe(
                    district_rank[
                        [
                            "자치구명",
                            "거래건수",
                            "평균월세",
                            "평균보증금",
                        ]
                    ]
                    .head(10)
                    .style.format(
                        {
                            "평균월세": "{:.1f}",
                            "평균보증금": "{:,.0f}",
                        }
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

        # -------------------------------------------------
        # 역
        # -------------------------------------------------

        with rank_col2:

            st.markdown("**지하철역 순위**")

            if len(station_rank) == 0:

                st.info(
                    "표시할 데이터가 없습니다."
                )

            else:

                st.dataframe(
                    station_rank[
                        [
                            "최근접역",
                            "최근접역_호선",
                            "거래건수",
                            "평균월세",
                        ]
                    ]
                    .head(10)
                    .style.format(
                        {
                            "평균월세": "{:.1f}",
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

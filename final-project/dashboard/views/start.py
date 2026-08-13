# pages/start.py
# -*- coding: utf-8 -*-

import streamlit as st

def render_start():

    st.markdown(
        """
        <div class="start-page">

            <div class="start-header">

                <div class="start-eyebrow">
                    SEOUL RENTAL MARKET · 2025
                </div>

                <h1 class="start-title">
                    서울 청년 월세 시장을<br>
                    원하는 기준으로 분석하세요
                </h1>

                <p class="start-description">
                    분석 기준을 선택하면 해당 조건에 맞는
                    서울 월세 시장을 단계적으로 살펴볼 수 있습니다.
                </p>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # 자치구별
    # =====================================================

    with col1:

        st.markdown(
            """
            <div class="choice-col choice-col--district">

                <div class="choice-card">

                    <div class="choice-card__badge">
                        🏙️
                    </div>

                    <div class="choice-card__tag">
                        DISTRICT
                    </div>

                    <h3 class="choice-card__title">
                        자치구별 보기
                    </h3>

                    <p class="choice-card__desc">
                        서울 25개 자치구를 기준으로
                        지역별 월세 수준과 시장 특성을 비교합니다.
                    </p>

                    <div class="choice-card__meta">
                        25 DISTRICTS
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "자치구별 보기 →",
            use_container_width=True,
            type="primary",
            key="start_district",
        ):
            st.session_state.view_type = "district"
            st.session_state.page = 2
            st.rerun()

    # =====================================================
    # 노선별
    # =====================================================

    with col2:

        st.markdown(
            """
            <div class="choice-col choice-col--line">

                <div class="choice-card">

                    <div class="choice-card__badge">
                        🚇
                    </div>

                    <div class="choice-card__tag">
                        SUBWAY LINE
                    </div>

                    <h3 class="choice-card__title">
                        지하철 노선별 보기
                    </h3>

                    <p class="choice-card__desc">
                        지하철 노선을 기준으로
                        역세권 월세 수준과 노선별 차이를 비교합니다.
                    </p>

                    <div class="choice-card__meta">
                        SUBWAY NETWORK
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "노선별 보기 →",
            use_container_width=True,
            type="primary",
            key="start_line",
        ):
            st.session_state.view_type = "line"
            st.session_state.page = 2
            st.rerun()

    # =====================================================
    # 역별
    # =====================================================

    with col3:

        st.markdown(
            """
            <div class="choice-col choice-col--station">

                <div class="choice-card">

                    <div class="choice-card__badge">
                        📍
                    </div>

                    <div class="choice-card__tag">
                        STATION
                    </div>

                    <h3 class="choice-card__title">
                        지하철역별 보기
                    </h3>

                    <p class="choice-card__desc">
                        특정 지하철역을 기준으로
                        주변 월세 시장을 세밀하게 분석합니다.
                    </p>

                    <div class="choice-card__meta">
                        STATION LEVEL
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "역별 보기 →",
            use_container_width=True,
            type="primary",
            key="start_station",
        ):
            st.session_state.view_type = "station"
            st.session_state.page = 2
            st.rerun()

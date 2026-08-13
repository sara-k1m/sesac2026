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
                    자치구, 지하철 노선, 지하철역 중 하나를 선택하면
                    해당 기준에 맞는 월세 시장 데이터를 단계별로 분석할 수 있습니다.
                </p>

            </div>

            <div class="choice-grid">

                <!-- 자치구 -->
                <div class="choice-col choice-col--district">

                    <div class="choice-card">

                        <div class="choice-card__badge">
                            🏙️
                        </div>

                        <div class="choice-card__tag">
                            DISTRICT
                        </div>

                        <h2 class="choice-card__title">
                            자치구별 분석
                        </h2>

                        <p class="choice-card__desc">
                            서울 25개 자치구를 비교하여
                            지역별 월세 수준과 시장 특성을 확인합니다.
                        </p>

                        <div class="choice-card__meta">
                            25 DISTRICTS
                        </div>

                    </div>

                </div>


                <!-- 노선 -->
                <div class="choice-col choice-col--line">

                    <div class="choice-card">

                        <div class="choice-card__badge">
                            🚇
                        </div>

                        <div class="choice-card__tag">
                            SUBWAY LINE
                        </div>

                        <h2 class="choice-card__title">
                            지하철 노선별 분석
                        </h2>

                        <p class="choice-card__desc">
                            지하철 노선을 기준으로 역세권의
                            월세 수준과 노선별 차이를 비교합니다.
                        </p>

                        <div class="choice-card__meta">
                            SUBWAY NETWORK
                        </div>

                    </div>

                </div>


                <!-- 역 -->
                <div class="choice-col choice-col--station">

                    <div class="choice-card">

                        <div class="choice-card__badge">
                            📍
                        </div>

                        <div class="choice-card__tag">
                            STATION
                        </div>

                        <h2 class="choice-card__title">
                            지하철역별 분석
                        </h2>

                        <p class="choice-card__desc">
                            특정 역을 중심으로 주변 월세 시장을
                            보다 세밀하게 확인합니다.
                        </p>

                        <div class="choice-card__meta">
                            STATION LEVEL
                        </div>

                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "자치구별 분석 시작 →",
            use_container_width=True,
            type="primary",
            key="start_district",
        ):
            st.session_state.view_type = "district"
            st.session_state.page = 2
            st.rerun()

    with col2:
        if st.button(
            "노선별 분석 시작 →",
            use_container_width=True,
            type="primary",
            key="start_line",
        ):
            st.session_state.view_type = "line"
            st.session_state.page = 2
            st.rerun()

    with col3:
        if st.button(
            "역별 분석 시작 →",
            use_container_width=True,
            type="primary",
            key="start_station",
        ):
            st.session_state.view_type = "station"
            st.session_state.page = 2
            st.rerun()

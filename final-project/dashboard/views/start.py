# pages/start.py
# -*- coding: utf-8 -*-

import streamlit as st


def render_start():
    
    # =====================================================
    # HEADER
    # =====================================================
    
    st.markdown(
        """
        <style>
        .start-hero {
            background: #0d1117;
            color: #ffffff;
            padding: 3rem 2rem 3.2rem;
            margin: -0.75rem -2rem 2.5rem;
            text-align: center;
            border-bottom: 1px solid #232c38;
        }
    
        .start-hero-eyebrow {
            color: #8fb3c4;
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }
    
        .start-hero-title {
            margin: 0;
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.25;
            letter-spacing: -0.05em;
        }
    
        .start-hero-description {
            max-width: 620px;
            margin: 1rem auto 0;
            color: #9aa5b1;
            font-size: 0.92rem;
            line-height: 1.7;
        }
    
        @media (max-width: 900px) {
            .start-hero {
                padding: 2.2rem 1rem 2.5rem;
                margin: -0.75rem -1rem 2rem;
            }
    
            .start-hero-title {
                font-size: 1.9rem;
            }
        }
        </style>
    
        <div class="start-hero">
    
            <div class="start-hero-eyebrow">
                SEOUL RENTAL MARKET · 2025
            </div>
    
            <h1 class="start-hero-title">
                서울 청년 월세 시장을 분석하세요
            </h1>
    
            <p class="start-hero-description">
                분석 기준을 선택하면 다음 단계에서
                원하는 조건을 설정하고 상세 데이터를 확인할 수 있습니다.
            </p>
    
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # CHOICES
    # =====================================================

    col1, col2, col3 = st.columns(3, gap="medium")

    # =====================================================
    # 자치구
    # =====================================================

    with col1:

        with st.container(border=True):

            st.markdown(
                """
                <div style="
                    width: 48px;
                    height: 48px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #eaf1f5;
                    border: 1px solid #c9dbe3;
                    border-radius: 12px;
                    font-size: 1.4rem;
                    margin-bottom: 0.8rem;
                ">
                    🏙️
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption("DISTRICT")

            st.markdown(
                "### 자치구별 보기"
            )

            st.write(
                "서울의 각 자치구를 기준으로 "
                "월세 수준과 지역별 시장 특성을 비교합니다."
            )

            st.markdown("")

            if st.button(
                "자치구별 분석 시작 →",
                use_container_width=True,
                type="primary",
                key="start_district",
            ):
                st.session_state.view_type = "district"
                st.session_state.page = 2
                st.rerun()

    # =====================================================
    # 노선
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown(
                """
                <div style="
                    width: 48px;
                    height: 48px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #fbf2df;
                    border: 1px solid #eaceA0;
                    border-radius: 12px;
                    font-size: 1.4rem;
                    margin-bottom: 0.8rem;
                ">
                    🚇
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption("SUBWAY LINE")

            st.markdown(
                "### 지하철 노선별 보기"
            )

            st.write(
                "지하철 노선을 기준으로 "
                "역세권 월세 수준과 노선별 차이를 비교합니다."
            )

            st.markdown("")

            if st.button(
                "노선별 분석 시작 →",
                use_container_width=True,
                type="primary",
                key="start_line",
            ):
                st.session_state.view_type = "line"
                st.session_state.page = 2
                st.rerun()

    # =====================================================
    # 역
    # =====================================================

    with col3:

        with st.container(border=True):

            st.markdown(
                """
                <div style="
                    width: 48px;
                    height: 48px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #f8ecf1;
                    border: 1px solid #e6c9d5;
                    border-radius: 12px;
                    font-size: 1.4rem;
                    margin-bottom: 0.8rem;
                ">
                    📍
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption("STATION")

            st.markdown(
                "### 지하철역별 보기"
            )

            st.write(
                "특정 지하철역을 기준으로 "
                "주변 월세 시장을 세밀하게 분석합니다."
            )

            st.markdown("")

            if st.button(
                "역별 분석 시작 →",
                use_container_width=True,
                type="primary",
                key="start_station",
            ):
                st.session_state.view_type = "station"
                st.session_state.page = 2
                st.rerun()

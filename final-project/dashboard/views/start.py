# pages/start.py
# -*- coding: utf-8 -*-

import streamlit as st


def render_start():

    # =====================================================
    # PAGE 1 BACKGROUND
    # -----------------------------------------------------
    # 첫 화면에서만 적용되는 배경.
    # 기존 CSS 파일은 수정하지 않아도 됨.
    # =====================================================

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 12% 0%,
                    rgba(23, 71, 95, 0.18),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 92% 15%,
                    rgba(125, 51, 80, 0.07),
                    transparent 25%
                ),
                linear-gradient(
                    135deg,
                    #0d1117 0%,
                    #18232d 14%,
                    #e9eef1 42%,
                    #ffffff 72%
                ) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        "### SEOUL RENTAL MARKET · 2025"
    )

    st.markdown(
        "## 서울 청년 월세 시장을 분석하세요"
    )

    st.caption(
        "분석 기준을 선택하면 다음 단계에서 "
        "원하는 조건을 설정하고 상세 데이터를 확인할 수 있습니다."
    )

    st.markdown("")

    # =====================================================
    # CHOICE CARDS
    # =====================================================

    col1, col2, col3 = st.columns(
        3,
        gap="medium",
    )

    # =====================================================
    # 자치구별
    # =====================================================

    with col1:

        with st.container(border=True):

            st.markdown("### 🏙️")

            st.caption("DISTRICT")

            st.markdown(
                "#### 자치구별 보기"
            )

            st.write(
                "서울의 각 자치구를 기준으로 "
                "월세 수준과 지역별 시장 특성을 비교합니다."
            )

            st.markdown("")

            st.caption("25 DISTRICTS")

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
    # 노선별
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown("### 🚇")

            st.caption("SUBWAY LINE")

            st.markdown(
                "#### 지하철 노선별 보기"
            )

            st.write(
                "지하철 노선을 기준으로 "
                "역세권 월세 수준과 노선별 차이를 비교합니다."
            )

            st.markdown("")

            st.caption("SUBWAY NETWORK")

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
    # 역별
    # =====================================================

    with col3:

        with st.container(border=True):

            st.markdown("### 📍")

            st.caption("STATION")

            st.markdown(
                "#### 지하철역별 보기"
            )

            st.write(
                "특정 지하철역을 기준으로 "
                "주변 월세 시장을 세밀하게 분석합니다."
            )

            st.markdown("")

            st.caption("STATION LEVEL")

            if st.button(
                "역별 분석 시작 →",
                use_container_width=True,
                type="primary",
                key="start_station",
            ):
                st.session_state.view_type = "station"
                st.session_state.page = 2
                st.rerun()

    # =====================================================
    # FOOTER SPACE
    # =====================================================

    st.markdown("")
    st.markdown("")

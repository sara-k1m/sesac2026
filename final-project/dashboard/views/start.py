# pages/start.py
# -*- coding: utf-8 -*-

import streamlit as st


def render_start():

    st.markdown(
        "## 🏠 2025 서울 청년 월세 분석"
    )

    st.markdown(
        "### 무엇을 기준으로 분석할까요?"
    )

    st.caption(
        "분석하고 싶은 기준을 선택하면 다음 단계에서 "
        "상세 조건을 설정할 수 있습니다."
    )

    st.markdown("")

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # 자치구별
    # =====================================================

    with col1:

        st.markdown(
            """
            <div class="start-box">

            <h2>🏙️</h2>

            <h3>자치구별 보기</h3>

            <p>
            서울의 각 자치구를 기준으로
            월세 시장을 분석합니다.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "자치구별 보기 →",
            use_container_width=True,
            type="primary",
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
            <div class="start-box">

            <h2>🚇</h2>

            <h3>지하철 노선별 보기</h3>

            <p>
            지하철 노선을 기준으로
            역세권 월세 시장을 분석합니다.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "지하철 노선별 보기 →",
            use_container_width=True,
            type="primary",
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
            <div class="start-box">

            <h2>📍</h2>

            <h3>지하철역별 보기</h3>

            <p>
            특정 지하철역을 기준으로
            주변 월세 시장을 분석합니다.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "지하철역별 보기 →",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.view_type = "station"
            st.session_state.page = 2
            st.rerun()
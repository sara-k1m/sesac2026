# pages/start.py
# -*- coding: utf-8 -*-

import streamlit as st


def render_start():

    # =====================================================
    # HEADER
    # =====================================================

    # HTML을 쓰지 않고 Streamlit Markdown만 사용
    #
    # 왼쪽 배경이 어두우므로 제목은 흰색 계열을 사용.
    # 실제 색상은 아래 CSS가 아니라 Streamlit의 기본
    # markdown 렌더링을 이용하므로 구조가 깨지지 않음.

    st.markdown(
        "### SEOUL RENTAL MARKET · 2025"
    )

    st.markdown(
        "## 2025 서울시 월세 시장 분석 대시보드"
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

            st.markdown(
                "#### 자치구별 보기"
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
    # 노선별
    # =====================================================

    with col2:

        with st.container(border=True):

            st.markdown("### 🚇")

            st.markdown(
                "#### 지하철 노선별 보기"
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
    # 역별
    # =====================================================

    with col3:

        with st.container(border=True):

            st.markdown("### 📍")

            st.markdown(
                "#### 지하철역별 보기"
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

    # =====================================================
    # BOTTOM SPACE
    # =====================================================

    st.markdown("")
    st.markdown("")

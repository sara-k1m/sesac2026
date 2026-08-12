# pages/dashboard.py

# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd

from utils.filtering import apply_filters

from components.interest_rate import render_interest_rate
from components.sidebar import render_sidebar
from components.kpi import render_kpi

from components.charts import (
    render_summary,
    render_region_analysis,
)

from components.map import render_map


def render_dashboard(
    df,
    distance_order,
    min_count,
):

    # =====================================================
    # 1. 분석 기준
    # =====================================================

    view_type = st.session_state.view_type

    # =====================================================
    # 2. 현재 조건
    # =====================================================

    selected_place = st.session_state.selected_place
    selected_rent = st.session_state.selected_rent
    selected_deposit = st.session_state.selected_deposit
    selected_area = st.session_state.selected_area
    selected_distance = st.session_state.selected_distance

    # =====================================================
    # 3. Sidebar
    #
    # 대시보드 안에서 조건을 바로 수정할 수 있도록 유지
    # =====================================================

    (
        selected_place,
        selected_rent,
        selected_deposit,
        selected_area,
        selected_distance,
    ) = render_sidebar(
        df=df,
        distance_order=distance_order,
        view_type=view_type,
        selected_place=selected_place,
        selected_rent=selected_rent,
        selected_deposit=selected_deposit,
        selected_area=selected_area,
        selected_distance=selected_distance,
    )

    # =====================================================
    # 4. 변경된 조건 session_state 반영
    # =====================================================

    st.session_state.selected_place = selected_place
    st.session_state.selected_rent = selected_rent
    st.session_state.selected_deposit = selected_deposit
    st.session_state.selected_area = selected_area
    st.session_state.selected_distance = selected_distance

    # =====================================================
    # 5. 기본 필터
    # =====================================================

    if view_type == "district":

        title = f"🏙️ {selected_place} 월세 분석"

        base_filter = (
            df["자치구명"] == selected_place
        )

        analysis_label = "자치구"

    elif view_type == "line":

        title = f"🚇 {selected_place} 역세권 월세 분석"

        base_filter = (
            df["최근접역_호선"] == selected_place
        )

        analysis_label = "지하철 노선"

    else:

        title = f"📍 {selected_place} 주변 월세 분석"

        base_filter = (
            df["최근접역"] == selected_place
        )

        analysis_label = "지하철역"

    # =====================================================
    # 6. 필터 적용
    # =====================================================

    f = apply_filters(
        df=df,
        base_filter=base_filter,
        selected_rent=selected_rent,
        selected_deposit=selected_deposit,
        selected_area=selected_area,
        selected_distance=selected_distance,
    )

    # =====================================================
    # 7. 데이터 없음
    # =====================================================

    if len(f) == 0:

        st.markdown(
            f"## {title}"
        )

        st.warning(
            "⚠️ 현재 조건에 해당하는 거래가 없습니다."
        )

        st.markdown(
            "### 조건을 변경해보세요."
        )

        st.caption(
            "왼쪽 필터에서 조건을 변경한 뒤 다시 적용해주세요."
        )

        return

    # =====================================================
    # 8. Header
    # =====================================================

    st.markdown(
        f"## {title}"
    )

    st.caption(
        f"2025년 서울 월세 실거래 · "
        f"{analysis_label} 기준 · "
        f"현재 조건 {len(f):,}건"
    )

    # =====================================================
    # 9. 핵심 KPI
    # =====================================================

    st.markdown(
        "### 핵심 지표"
    )

    render_kpi(f)

    # =====================================================
    # 10. 추천 / 한눈에 보기
    #
    # 기존에는 탭 안에 있었지만,
    # 이제 대시보드 첫 화면에서 바로 보여준다.
    # =====================================================

    st.markdown("")

    render_summary(
        f=f,
        min_count=min_count,
    )

    # =====================================================
    # 11. 금리 참고 지표
    #
    # 핵심 분석 결과가 아니라 보조 정보이므로
    # 추천 영역 아래에 배치
    # =====================================================

    st.markdown("")

    with st.expander(
        "📈 참고 지표 · 정부대출금금리",
        expanded=False,
    ):

        render_interest_rate()

    # =====================================================
    # 12. 상세 분석 영역
    # =====================================================

    st.markdown("")

    st.markdown(
        "### 상세 분석"
    )

    (
        tab_region,
        tab_map,
        tab_data,
    ) = st.tabs(
        [
            "📊 시장 분석",
            "🗺️ 거래 지도",
            "📋 거래 데이터",
        ]
    )

    # =====================================================
    # TAB 1
    # 시장 분석
    # =====================================================

    with tab_region:

        render_region_analysis(
            f=f,
            view_type=view_type,
            selected_place=selected_place,
            distance_order=distance_order,
        )

    # =====================================================
    # TAB 2
    # 지도
    # =====================================================

    with tab_map:

        render_map(
            df=df,
            f=f,
            view_type=view_type,
            selected_place=selected_place,
        )

    # =====================================================
    # TAB 3
    # 상세 데이터
    # =====================================================

    with tab_data:

        st.markdown(
            "#### 📋 상세 데이터"
        )

        st.caption(
            f"현재 조건에 해당하는 {len(f):,}건의 실거래 데이터입니다."
        )

        display_cols = [
            "자치구명",
            "법정동명",
            "계약일",
            "건물용도",
            "임대면적",
            "보증금(만원)",
            "임대료(만원)",
            "최근접역",
            "최근접역_호선",
            "최근접역_거리(m)",
            "거리구간",
        ]

        display_cols = [
            c
            for c in display_cols
            if c in f.columns
        ]

        st.dataframe(
            f[display_cols]
            .sort_values(
                "계약일",
                ascending=False,
            ),
            hide_index=True,
            use_container_width=True,
        )

        # -------------------------------------------------
        # CSV 다운로드
        # -------------------------------------------------

        csv = f.to_csv(
            index=False,
            encoding="utf-8-sig",
        )

        st.download_button(
            "⬇️ 현재 조건 데이터 다운로드",
            data=csv,
            file_name="filtered_rent_data.csv",
            mime="text/csv",
            use_container_width=False,
        )

    # =====================================================
    # 하단 액션
    # =====================================================

    st.markdown("---")

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # 조건 변경
    # -----------------------------------------------------

    with col1:

        if st.button(
            "⚙️ 조건 설정으로 돌아가기",
            use_container_width=True,
        ):

            st.session_state.page = 2

            st.rerun()

    # -----------------------------------------------------
    # 처음으로
    # -----------------------------------------------------

    with col2:

        if st.button(
            "🏠 분석 기준 다시 선택",
            use_container_width=True,
        ):

            st.session_state.page = 1

            st.session_state.view_type = None

            st.rerun()

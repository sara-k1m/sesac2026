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
    # 분석 기준
    # =====================================================

    view_type = st.session_state.view_type

    # =====================================================
    # 현재 조건
    # =====================================================

    selected_place = st.session_state.selected_place
    selected_rent = st.session_state.selected_rent
    selected_deposit = st.session_state.selected_deposit
    selected_area = st.session_state.selected_area
    selected_distance = st.session_state.selected_distance

    # =====================================================
    # Sidebar
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
    # 변경된 조건 session_state 반영
    # =====================================================

    st.session_state.selected_place = selected_place
    st.session_state.selected_rent = selected_rent
    st.session_state.selected_deposit = selected_deposit
    st.session_state.selected_area = selected_area
    st.session_state.selected_distance = selected_distance

    # =====================================================
    # 기본 필터
    # =====================================================

    if view_type == "district":

        title = f"🏙️ {selected_place} 월세 분석"

        base_filter = (
            df["자치구명"] == selected_place
        )

    elif view_type == "line":

        title = f"🚇 {selected_place} 역세권 월세 분석"

        base_filter = (
            df["최근접역_호선"] == selected_place
        )

    else:

        title = f"📍 {selected_place} 주변 월세 분석"

        base_filter = (
            df["최근접역"] == selected_place
        )

    # =====================================================
    # 제목
    # =====================================================

    st.markdown(
        f"## {title}"
    )

    st.caption(
        "선택한 조건에 해당하는 2025년 서울 월세 실거래 데이터를 분석합니다."
    )

    # =====================================================
    # 필터 적용
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
    # 데이터 없음
    # =====================================================

    if len(f) == 0:

        st.warning(
            "⚠️ 현재 조건에 해당하는 거래가 없습니다."
        )

        st.markdown(
            "조건을 왼쪽 필터에서 변경해보세요."
        )

        return

    # =====================================================
    # KPI
    # =====================================================

    render_kpi(f)

    # =====================================================
    # Tabs
    # =====================================================

    (
        tab_summary,
        tab_region,
        tab_map,
        tab_interest,
        tab_data,
    ) = st.tabs(
        [
            "📊 요약 · 추천",
            "🏙️ 지역별 분석",
            "🗺️ 지도",
            "📈 금리",
            "📋 상세 데이터",
        ]
    )

    # =====================================================
    # TAB 1
    # 요약 · 추천
    # =====================================================

    with tab_summary:

        render_summary(
            f=f,
            min_count=min_count,
        )

    # =====================================================
    # TAB 2
    # 지역별 분석
    # =====================================================

    with tab_region:

        render_region_analysis(
            f=f,
            view_type=view_type,
            selected_place=selected_place,
            distance_order=distance_order,
        )

    # =====================================================
    # TAB 3
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
    # TAB 4
    # 금리
    # =====================================================

    with tab_interest:

        render_interest_rate()

    # =====================================================
    # TAB 5
    # 상세 데이터
    # =====================================================

    with tab_data:

        st.markdown(
            "#### 📋 상세 데이터"
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

        csv = f.to_csv(
            index=False,
            encoding="utf-8-sig",
        )

        st.download_button(
            "⬇️ 현재 조건 데이터 다운로드",
            data=csv,
            file_name="filtered_rent_data.csv",
            mime="text/csv",
        )

    # =====================================================
    # 하단 버튼
    # =====================================================

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← 조건 다시 설정",
            use_container_width=True,
        ):

            st.session_state.page = 2
            st.rerun()

    with col2:

        if st.button(
            "🏠 처음으로 돌아가기",
            use_container_width=True,
        ):

            st.session_state.page = 1
            st.session_state.view_type = None

            st.rerun()

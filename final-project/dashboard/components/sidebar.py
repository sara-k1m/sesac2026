# components/sidebar.py

# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd


def render_sidebar(
    df,
    distance_order,
    view_type,
    selected_place,
    selected_rent,
    selected_deposit,
    selected_area,
    selected_distance,
):
    """
    3페이지 Dashboard의 Sidebar 필터

    - 2페이지에서 설정한 조건을 기본값으로 사용
    - 3페이지에서 직접 조건 변경 가능
    - 변경된 값은 st.session_state에 즉시 반영
    """

    st.sidebar.markdown("## 🏠 분석 조건")

    # =====================================================
    # 분석 기준
    # =====================================================

    if view_type == "district":

        analysis_type = "자치구"

    elif view_type == "line":

        analysis_type = "지하철 노선"

    else:

        analysis_type = "지하철역"

    st.sidebar.metric(
        "분석 기준",
        analysis_type,
    )

    st.sidebar.markdown("---")

    # =====================================================
    # 선택 대상
    # =====================================================

    st.sidebar.markdown("**선택 대상**")

    # -----------------------------------------------------
    # 자치구
    # -----------------------------------------------------

    if view_type == "district":

        districts = sorted(
            df["자치구명"]
            .dropna()
            .unique()
            .tolist()
        )

        if selected_place not in districts and districts:

            selected_place = districts[0]

        sidebar_place = st.sidebar.selectbox(
            "자치구",
            districts,
            index=(
                districts.index(selected_place)
                if selected_place in districts
                else 0
            ),
            key="sidebar_district",
        )

    # -----------------------------------------------------
    # 노선
    # -----------------------------------------------------

    elif view_type == "line":

        lines = sorted(
            df["최근접역_호선"]
            .dropna()
            .unique()
            .tolist()
        )

        if selected_place not in lines and lines:

            selected_place = lines[0]

        sidebar_place = st.sidebar.selectbox(
            "지하철 노선",
            lines,
            index=(
                lines.index(selected_place)
                if selected_place in lines
                else 0
            ),
            key="sidebar_line",
        )

    # -----------------------------------------------------
    # 역
    # -----------------------------------------------------

    else:

        station_lines = sorted(
            df["최근접역_호선"]
            .dropna()
            .unique()
            .tolist()
        )

        current_line = st.session_state.get(
            "sidebar_station_line",
            None,
        )

        # 현재 선택된 역의 호선을 찾아 기본값으로 사용
        if (
            current_line not in station_lines
            and selected_place
        ):

            matched_lines = (
                df.loc[
                    df["최근접역"] == selected_place,
                    "최근접역_호선",
                ]
                .dropna()
                .unique()
                .tolist()
            )

            if matched_lines:

                current_line = matched_lines[0]

        if current_line not in station_lines:

            current_line = (
                station_lines[0]
                if station_lines
                else None
            )

        if station_lines:

            sidebar_station_line = st.sidebar.selectbox(
                "지하철 호선",
                station_lines,
                index=station_lines.index(
                    current_line
                ),
                key="sidebar_station_line",
            )

            line_stations = sorted(
                df.loc[
                    df["최근접역_호선"]
                    == sidebar_station_line,
                    "최근접역",
                ]
                .dropna()
                .unique()
                .tolist()
            )

        else:

            sidebar_station_line = None
            line_stations = []

        if selected_place not in line_stations:

            selected_place = (
                line_stations[0]
                if line_stations
                else None
            )

        sidebar_place = st.sidebar.selectbox(
            "지하철역",
            line_stations,
            index=(
                line_stations.index(selected_place)
                if selected_place in line_stations
                else 0
            ),
            key="sidebar_station",
        )

    # =====================================================
    # 선택 대상 session_state 반영
    # =====================================================

    st.session_state.selected_place = sidebar_place

    # =====================================================
    # 월세
    # =====================================================

    st.sidebar.markdown("---")

    st.sidebar.markdown("**월세**")

    rent_min = 10
    rent_max = 1000

    current_rent_min = max(
        rent_min,
        min(
            rent_max,
            selected_rent[0],
        ),
    )

    current_rent_max = max(
        rent_min,
        min(
            rent_max,
            selected_rent[1],
        ),
    )

    if current_rent_min > current_rent_max:

        current_rent_min = rent_min
        current_rent_max = rent_max

    sidebar_rent = st.sidebar.slider(
        "월세 (만원)",
        min_value=rent_min,
        max_value=rent_max,
        value=(
            current_rent_min,
            current_rent_max,
        ),
        step=10,
        key="sidebar_rent",
    )

    st.session_state.selected_rent = sidebar_rent

    # =====================================================
    # 보증금
    # =====================================================

    st.sidebar.markdown("**보증금**")

    deposit_min = 0
    deposit_max = 10000

    current_deposit_min = max(
        deposit_min,
        min(
            deposit_max,
            selected_deposit[0],
        ),
    )

    current_deposit_max = max(
        deposit_min,
        min(
            deposit_max,
            selected_deposit[1],
        ),
    )

    if current_deposit_min > current_deposit_max:

        current_deposit_min = deposit_min
        current_deposit_max = deposit_max

    sidebar_deposit = st.sidebar.slider(
        "보증금 (만원)",
        min_value=deposit_min,
        max_value=deposit_max,
        value=(
            current_deposit_min,
            current_deposit_max,
        ),
        step=100,
        key="sidebar_deposit",
    )

    st.session_state.selected_deposit = sidebar_deposit

    # =====================================================
    # 면적
    # =====================================================

    st.sidebar.markdown("**임대면적**")

    # 1평 = 3.305785㎡
    PYEONG_M2 = 3.305785

    # -----------------------------------------------------
    # 실제 데이터의 면적 범위
    # -----------------------------------------------------

    area_series = pd.to_numeric(
        df["임대면적"],
        errors="coerce",
    ).dropna()

    if len(area_series) > 0:

        area_min = float(area_series.min())
        area_max = float(area_series.max())

    else:

        area_min = 0.0
        area_max = 200.0


    # -----------------------------------------------------
    # 기존 선택값
    # -----------------------------------------------------

    current_area_min = max(
        area_min,
        min(
            area_max,
            float(selected_area[0]),
        ),
    )

    current_area_max = max(
        area_min,
        min(
            area_max,
            float(selected_area[1]),
        ),
    )

    if current_area_min > current_area_max:

        current_area_min = area_min
        current_area_max = area_max


    # -----------------------------------------------------
    # ㎡ 슬라이더
    # -----------------------------------------------------

    sidebar_area = st.sidebar.slider(
        "임대면적 (㎡)",

        min_value=area_min,
        max_value=area_max,

        value=(
            current_area_min,
            current_area_max,
        ),

        step=0.1,

        key="sidebar_area",
    )


    # -----------------------------------------------------
    # 선택된 면적
    # -----------------------------------------------------

    area_min_selected = sidebar_area[0]
    area_max_selected = sidebar_area[1]


    # -----------------------------------------------------
    # 평으로 변환
    # -----------------------------------------------------

    pyeong_min = (
        area_min_selected / PYEONG_M2
    )

    pyeong_max = (
        area_max_selected / PYEONG_M2
    )


    # -----------------------------------------------------
    # 선택된 ㎡ 범위 표시
    # -----------------------------------------------------

    st.sidebar.caption(
        f"{area_min_selected:.1f}㎡ ~ "
        f"{area_max_selected:.1f}㎡"
    )


    # -----------------------------------------------------
    # 평 환산 표시
    # -----------------------------------------------------

    st.sidebar.info(
        f"📐 약 **{pyeong_min:.1f}평 ~ "
        f"{pyeong_max:.1f}평**"
    )


    # -----------------------------------------------------
    # 실제 필터에는 ㎡ 사용
    # -----------------------------------------------------

    st.session_state.selected_area = sidebar_area

    # =====================================================
    # 역까지 거리
    # =====================================================

    st.sidebar.markdown("**역까지 거리**")

    valid_distance = [
        distance
        for distance in distance_order
        if distance
    ]

    current_distance = [
        distance
        for distance in selected_distance
        if distance in valid_distance
    ]

    sidebar_distance = st.sidebar.multiselect(
        "역까지 거리",
        valid_distance,
        default=current_distance,
        key="sidebar_distance",
        placeholder="거리 구간을 선택하세요",
    )

    st.session_state.selected_distance = sidebar_distance

    # =====================================================
    # 현재 조건 표시
    # =====================================================

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "조건을 변경하면 대시보드가 자동으로 업데이트됩니다."
    )

    return (
        st.session_state.selected_place,
        st.session_state.selected_rent,
        st.session_state.selected_deposit,
        st.session_state.selected_area,
        st.session_state.selected_distance,
    )
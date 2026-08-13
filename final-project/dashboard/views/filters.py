# pages/filters.py
# -*- coding: utf-8 -*-

import streamlit as st


def render_filters(
    df,
    filter_options,
    distance_order,
):

    districts = filter_options["districts"]
    lines = filter_options["lines"]
    stations = filter_options["stations"]

    area_min = filter_options["area_min"]
    area_max = filter_options["area_max"]

    view_type = st.session_state.view_type

    # =====================================================
    # PAGE HEADER
    # =====================================================

    st.markdown(
        "## 분석 조건 설정"
    )

    st.caption(
        "분석 기준을 선택하고 예산·주거 조건을 설정하세요."
    )

    # =====================================================
    # 분석 방식 안내
    # =====================================================

    if view_type == "district":

        st.info(
            "🏙️ **자치구별 분석** — 분석할 자치구를 선택해주세요."
        )

    elif view_type == "line":

        st.info(
            "🚇 **지하철 노선별 분석** — 분석할 노선을 선택해주세요."
        )

    elif view_type == "station":

        st.info(
            "📍 **지하철역별 분석** — 분석할 역을 선택해주세요."
        )

    st.markdown("")

    # =====================================================
    # 1. 분석 대상
    # =====================================================

    st.markdown(
        "### 1. 분석 대상"
    )

    # -----------------------------------------------------
    # 자치구
    # -----------------------------------------------------

    if view_type == "district":

        selected_place = st.selectbox(
            "자치구",
            districts,
            index=(
                districts.index(
                    st.session_state.selected_place
                )
                if st.session_state.selected_place in districts
                else 0
            ),
            placeholder="자치구를 선택하세요",
        )

    # -----------------------------------------------------
    # 노선
    # -----------------------------------------------------

    elif view_type == "line":

        selected_place = st.selectbox(
            "지하철 노선",
            lines,
            index=(
                lines.index(
                    st.session_state.selected_place
                )
                if st.session_state.selected_place in lines
                else 0
            ),
            placeholder="지하철 노선을 선택하세요",
        )

    # -----------------------------------------------------
    # 역
    # -----------------------------------------------------

    else:

        station_lines = sorted(
            df["최근접역_호선"]
            .dropna()
            .unique()
        )

        selected_line = st.selectbox(
            "지하철 호선",
            station_lines,
            placeholder="먼저 호선을 선택하세요",
            key="station_line_select",
        )

        st.session_state.selected_station_line = selected_line

        if selected_line:

            line_stations = sorted(
                df.loc[
                    df["최근접역_호선"] == selected_line,
                    "최근접역",
                ]
                .dropna()
                .unique()
            )

            selected_place = st.selectbox(
                "지하철역",
                line_stations,
                placeholder="역을 선택하세요",
                key="station_select",
            )

        else:

            selected_place = None

    # =====================================================
    # 2. 예산 조건
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 2. 예산 조건"
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # 월세
    # -----------------------------------------------------

    with col1:

        selected_rent = st.slider(
            "월세 (만원)",
            min_value=10,
            max_value=1000,
            value=(
                max(
                    10,
                    st.session_state.selected_rent[0],
                ),
                min(
                    1000,
                    max(
                        300,
                        st.session_state.selected_rent[1],
                    ),
                ),
            ),
            step=10,
            help="10만원 단위로 선택할 수 있습니다.",
        )

        st.caption(
            f"선택 범위  ·  "
            f"{selected_rent[0]:,}만원 ~ "
            f"{selected_rent[1]:,}만원"
        )

    # -----------------------------------------------------
    # 보증금
    # -----------------------------------------------------

    with col2:

        selected_deposit = st.slider(
            "보증금 (만원)",
            min_value=0,
            max_value=10000,
            value=(
                max(
                    0,
                    st.session_state.selected_deposit[0],
                ),
                min(
                    10000,
                    st.session_state.selected_deposit[1],
                ),
            ),
            step=100,
            help="100만원 단위로 선택할 수 있습니다. 최대 1억원입니다.",
        )

        # ---------------------------------------------
        # 보증금 표시용 함수
        # ---------------------------------------------

        def format_deposit(value):

            if value >= 10000:

                억 = value // 10000
                만원 = value % 10000

                if 만원 == 0:
                    return f"{억}억원"

                return f"{억}억 {만원:,}만원"

            return f"{value:,}만원"

        st.caption(
            f"선택 범위  ·  "
            f"{format_deposit(selected_deposit[0])} ~ "
            f"{format_deposit(selected_deposit[1])}"
        )

    # =====================================================
    # 3. 주거 조건
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 3. 주거 조건"
    )

    # -----------------------------------------------------
    # 평 ↔ ㎡ 변환
    # -----------------------------------------------------

    PYUNG_TO_SQM = 3.3058

    # 기존 session_state의 ㎡ 값을 평으로 변환
    saved_area_min = round(
        st.session_state.selected_area[0]
        / PYUNG_TO_SQM
    )

    saved_area_max = round(
        st.session_state.selected_area[1]
        / PYUNG_TO_SQM
    )

    # 실제 데이터 범위를 평으로 변환
    data_area_min = max(
        1,
        int(area_min / PYUNG_TO_SQM),
    )

    data_area_max = min(
        60,
        int(area_max / PYUNG_TO_SQM),
    )

    # 데이터 범위가 비정상적인 경우 방어
    data_area_max = max(
        data_area_min,
        data_area_max,
    )

    # 저장된 기본값을 실제 데이터 범위 안으로 보정
    saved_area_min = max(
        data_area_min,
        min(
            data_area_max,
            saved_area_min,
        ),
    )

    saved_area_max = max(
        saved_area_min,
        min(
            data_area_max,
            saved_area_max,
        ),
    )

    # -----------------------------------------------------
    # 평 단위 슬라이더
    # -----------------------------------------------------

    selected_area_pyung = st.slider(
        "임대면적 (평)",
        min_value=data_area_min,
        max_value=data_area_max,
        value=(
            saved_area_min,
            saved_area_max,
        ),
        step=1,
        help="1평 단위로 선택할 수 있으며 최대 60평까지 선택할 수 있습니다.",
    )

    # -----------------------------------------------------
    # 평 → ㎡ 변환
    # -----------------------------------------------------

    selected_area = (
        round(
            selected_area_pyung[0]
            * PYUNG_TO_SQM,
            2,
        ),
        round(
            selected_area_pyung[1]
            * PYUNG_TO_SQM,
            2,
        ),
    )

    st.caption(
        f"선택 범위  ·  "
        f"{selected_area_pyung[0]}평 "
        f"({selected_area[0]:,.1f}㎡) ~ "
        f"{selected_area_pyung[1]}평 "
        f"({selected_area[1]:,.1f}㎡)"
    )

    # =====================================================
    # 4. 지하철 접근 거리
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 4. 지하철 접근 거리"
    )

    selected_distance = st.multiselect(
        "역까지 거리",
        distance_order,
        default=st.session_state.selected_distance,
        placeholder="거리 구간을 선택하세요",
    )

    # =====================================================
    # ACTION BUTTONS
    # =====================================================

    st.markdown("")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    # -----------------------------------------------------
    # 이전 단계
    # -----------------------------------------------------

    with col1:

        if st.button(
            "← 분석 기준 다시 선택",
            use_container_width=True,
        ):

            st.session_state.page = 1
            st.rerun()

    # -----------------------------------------------------
    # 결과 보기
    # -----------------------------------------------------

    with col3:

        if st.button(
            "분석 결과 보기 →",
            use_container_width=True,
            type="primary",
        ):

            # ---------------------------------------------
            # 선택값 저장
            # ---------------------------------------------

            st.session_state.selected_place = (
                selected_place
            )

            st.session_state.selected_rent = (
                selected_rent
            )

            st.session_state.selected_deposit = (
                selected_deposit
            )

            # 내부 저장값은 ㎡ 기준
            st.session_state.selected_area = (
                selected_area
            )

            st.session_state.selected_distance = (
                selected_distance
            )

            # ---------------------------------------------
            # Page 3
            # ---------------------------------------------

            st.session_state.page = 3

            st.rerun()

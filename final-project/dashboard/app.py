# app.py
# -*- coding: utf-8 -*-

import streamlit as st

from utils.data import load_data, get_filter_options
from views.start import render_start
from views.filters import render_filters
from views.dashboard import render_dashboard
from streamlit_scroll_to_top import scroll_to_here


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="2025 서울 청년 월세 대시보드",
    page_icon="🏠",
    layout="wide",
)


# =========================================================
# CSS
# =========================================================

def load_css():
    with open("assets/style.css", "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()


# =========================================================
# 기본 설정
# =========================================================

def scroll_to_top():

    st.markdown(
        """
        <script>
            window.parent.scrollTo({
                top: 0,
                behavior: "instant"
            });
        </script>
        """,
        unsafe_allow_html=True,
    )

DISTANCE_ORDER = [
    "250m 이하",
    "250m 초과 ~ 500m 이하",
    "500m 초과 ~ 1km 이하",
    "1km 초과 ~ 1.5km 이하",
    "1.5km 초과",
]

MIN_COUNT = 10


# =========================================================
# 데이터
# =========================================================

try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "⚠️ rent_2025_final_dashboard.csv 파일을 찾을 수 없습니다."
    )

    st.info(
        "data/rent_2025_final_dashboard.csv 위치에 "
        "CSV 파일을 넣어주세요."
    )

    st.stop()


# =========================================================
# 필터 선택지
# =========================================================

filter_options = get_filter_options(
    df,
    DISTANCE_ORDER,
)


# =========================================================
# Session State 초기화
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "view_type" not in st.session_state:
    st.session_state.view_type = None

if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if "selected_rent" not in st.session_state:
    st.session_state.selected_rent = (10, 100)

if "selected_deposit" not in st.session_state:
    st.session_state.selected_deposit = (0, 10000)

if "selected_area" not in st.session_state:
    st.session_state.selected_area = (
        filter_options["area_min"],
        filter_options["area_max"],
    )

if "selected_distance" not in st.session_state:
    st.session_state.selected_distance = DISTANCE_ORDER.copy()

if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False


# =========================================================
# 페이지 라우팅
# =========================================================

if st.session_state.page == 1:

    render_start()


elif st.session_state.page == 2:

    render_filters(
        df=df,
        filter_options=filter_options,
        distance_order=DISTANCE_ORDER,
    )


elif st.session_state.page == 3:

    if st.session_state.scroll_to_top:

        scroll_to_here(0, key="dashboard_top")

        st.session_state.scroll_to_top = False

    render_dashboard(
        df=df,
        distance_order=DISTANCE_ORDER,
        min_count=MIN_COUNT,
    )
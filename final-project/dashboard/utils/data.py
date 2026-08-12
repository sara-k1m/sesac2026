# utils/data.py
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


DISTANCE_ORDER = [
    "250m 이하",
    "250m 초과 ~ 500m 이하",
    "500m 초과 ~ 1km 이하",
    "1km 초과 ~ 1.5km 이하",
    "1.5km 초과",
]


@st.cache_data
def load_data():

    data_path = (
        BASE_DIR
        / "data"
        / "rent_2025_final_dashboard.parquet"
    )

    df = pd.read_parquet(data_path)

    # =====================================================
    # 계약일
    # =====================================================

    if "계약일" in df.columns:

        df["계약일"] = pd.to_datetime(
            df["계약일"],
            format="%Y%m%d",
            errors="coerce"
        )

    # =====================================================
    # 숫자형
    # =====================================================

    numeric_cols = [
        "보증금(만원)",
        "임대료(만원)",
        "임대면적",
        "월세_㎡당",
        "위도",
        "경도",
        "최근접역_거리(m)",
        "최근접역_위도",
        "최근접역_경도",
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # =====================================================
    # 문자형
    # =====================================================

    string_cols = [
        "자치구명",
        "법정동명",
        "최근접역",
        "최근접역_호선",
        "건물용도",
        "거리구간",
    ]

    for col in string_cols:

        if col in df.columns:

            df[col] = (
                df[col]
                .astype("string")
                .str.strip()
            )

    # =====================================================
    # 거리구간
    # =====================================================

    if "거리구간" in df.columns:

        df["거리구간"] = pd.Categorical(
            df["거리구간"],
            categories=DISTANCE_ORDER,
            ordered=True
        )

    return df


def get_filter_options(
    df,
    distance_order=None,
):

    if distance_order is None:
        distance_order = DISTANCE_ORDER

    districts = sorted(
        df["자치구명"]
        .dropna()
        .unique()
    )

    lines = sorted(
        df["최근접역_호선"]
        .dropna()
        .unique()
    )

    stations = sorted(
        df["최근접역"]
        .dropna()
        .unique()
    )

    area_min = float(
        df["임대면적"]
        .dropna()
        .min()
    )

    area_max = float(
        df["임대면적"]
        .dropna()
        .max()
    )

    return {
        "districts": districts,
        "lines": lines,
        "stations": stations,
        "area_min": area_min,
        "area_max": area_max,
        "distance_order": distance_order,
    }

# utils/filtering.py
# -*- coding: utf-8 -*-

import pandas as pd


def apply_filters(
    df,
    base_filter,
    selected_rent,
    selected_deposit,
    selected_area,
    selected_distance,
):

    filtered = df[
        base_filter
        & df["거리구간"].isin(
            selected_distance
        )
        & df["임대료(만원)"].between(
            selected_rent[0],
            selected_rent[1],
        )
        & df["보증금(만원)"].between(
            selected_deposit[0],
            selected_deposit[1],
        )
        & df["임대면적"].between(
            selected_area[0],
            selected_area[1],
        )
    ].copy()

    return filtered
# -*- coding: utf-8 -*-

import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

GEOJSON_PATH = (
    BASE_DIR
    / "assets"
    / "seoul_gu.geojson"
)


def render_map(
    df,
    f,
    view_type,
    selected_place,
):

    st.markdown(
        "#### 🗺️ 거래 위치 지도"
    )

    try:

        with open(
            GEOJSON_PATH,
            "r",
            encoding="utf-8",
        ) as geojson_file:

            seoul_geojson = json.load(
                geojson_file
            )

    except FileNotFoundError:

        st.error(
            "seoul_gu.geojson 파일을 찾을 수 없습니다."
        )

        return

    # =====================================================
    # 거래 데이터
    # =====================================================

    map_df = f[
        [
            "위도",
            "경도",
            "자치구명",
            "최근접역",
            "최근접역_호선",
            "임대료(만원)",
            "보증금(만원)",
            "임대면적",
            "최근접역_거리(m)",
        ]
    ].dropna(
        subset=[
            "위도",
            "경도",
        ]
    ).copy()

    if len(map_df) > 15000:

        map_df = map_df.sample(
            15000,
            random_state=42,
        )

    # =====================================================
    # 자치구
    # =====================================================

    if view_type == "district":

        st.caption(
            f"📍 {selected_place}의 행정구역 경계와 "
            "해당 지역의 월세 거래를 표시합니다."
        )

        selected_features = []

        for feature in seoul_geojson["features"]:

            properties = feature.get(
                "properties",
                {}
            )

            geo_name = (
                properties.get("SIG_KOR_NM")
                or properties.get("name")
                or properties.get("자치구명")
            )

            if geo_name == selected_place:

                selected_features.append(
                    feature
                )

        selected_boundary = {
            "type": "FeatureCollection",
            "features": selected_features,
        }

        map_df = map_df[
            map_df["자치구명"] == selected_place
        ].copy()

        if len(map_df) > 0:

            center_lat = map_df["위도"].mean()
            center_lon = map_df["경도"].mean()

        else:

            center_lat = 37.5172
            center_lon = 127.0473

        boundary_layer = pdk.Layer(
            "GeoJsonLayer",
            data=selected_boundary,
            get_fill_color=[
                70,
                130,
                180,
                70,
            ],
            get_line_color=[
                30,
                80,
                130,
                220,
            ],
            get_line_width=5,
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        )

        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[경도, 위도]",
            get_radius=35,
            get_fill_color=[
                220,
                70,
                70,
                180,
            ],
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12,
            pitch=0,
        )

        tooltip = {
            "html": (
                "<b>{자치구명}</b><br/>"
                "최근접역: {최근접역}<br/>"
                "호선: {최근접역_호선}<br/>"
                "월세: {임대료(만원)}만원<br/>"
                "보증금: {보증금(만원)}만원<br/>"
                "면적: {임대면적}㎡<br/>"
                "역까지 거리: {최근접역_거리(m)}m"
            ),
            "style": {
                "backgroundColor": "white",
                "color": "#172033",
            },
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[
                    boundary_layer,
                    point_layer,
                ],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_provider="carto",
                map_style="light",
            ),
            use_container_width=True,
            height=750,
        )

    # =====================================================
    # 노선
    # =====================================================

    elif view_type == "line":

        st.caption(
            f"🚇 {selected_place}의 역세권 거래 위치를 표시합니다."
        )

        map_df = map_df[
            map_df["최근접역_호선"]
            .str.contains(
                selected_place,
                na=False,
            )
        ].copy()

        if len(map_df) > 0:

            center_lat = map_df["위도"].mean()
            center_lon = map_df["경도"].mean()

        else:

            center_lat = 37.5665
            center_lon = 126.9780

        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[경도, 위도]",
            get_radius=35,
            get_fill_color=[
                50,
                120,
                200,
                180,
            ],
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12.5,
            pitch=0,
        )

        tooltip = {
            "html": (
                "<b>{자치구명}</b><br/>"
                "최근접역: {최근접역}<br/>"
                "호선: {최근접역_호선}<br/>"
                "월세: {임대료(만원)}만원<br/>"
                "보증금: {보증금(만원)}만원<br/>"
                "면적: {임대면적}㎡"
            ),
            "style": {
                "backgroundColor": "white",
                "color": "#172033",
            },
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[
                    point_layer,
                ],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_provider="carto",
                map_style="light",
            ),
            use_container_width=True,
        )

    # =====================================================
    # 역
    # =====================================================

    else:

        st.caption(
            f"📍 {selected_place} 주변 거래 위치를 표시합니다."
        )

        map_df = map_df[
            map_df["최근접역"] == selected_place
        ].copy()

        if len(map_df) > 0:

            center_lat = map_df["위도"].mean()
            center_lon = map_df["경도"].mean()

        else:

            station_info = df[
                df["최근접역"] == selected_place
            ][
                [
                    "최근접역_위도",
                    "최근접역_경도",
                ]
            ].dropna()

            if len(station_info) > 0:

                center_lat = station_info[
                    "최근접역_위도"
                ].iloc[0]

                center_lon = station_info[
                    "최근접역_경도"
                ].iloc[0]

            else:

                center_lat = 37.5665
                center_lon = 126.9780

        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[경도, 위도]",
            get_radius=30,
            get_fill_color=[
                220,
                70,
                70,
                180,
            ],
            pickable=True,
            auto_highlight=True,
        )

        station_info = df[
            df["최근접역"] == selected_place
        ][
            [
                "최근접역_위도",
                "최근접역_경도",
            ]
        ].dropna().drop_duplicates()

        station_layer = pdk.Layer(
            "ScatterplotLayer",
            data=station_info,
            get_position="[최근접역_경도, 최근접역_위도]",
            get_radius=100,
            get_fill_color=[
                30,
                80,
                200,
                255,
            ],
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=14,
            pitch=0,
        )

        tooltip = {
            "html": (
                "<b>{자치구명}</b><br/>"
                "최근접역: {최근접역}<br/>"
                "월세: {임대료(만원)}만원<br/>"
                "보증금: {보증금(만원)}만원<br/>"
                "면적: {임대면적}㎡<br/>"
                "역까지 거리: {최근접역_거리(m)}m"
            ),
            "style": {
                "backgroundColor": "white",
                "color": "#172033",
            },
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[
                    point_layer,
                    station_layer,
                ],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_provider="carto",
                map_style="light",
            ),
            use_container_width=True,
        )
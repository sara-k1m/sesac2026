# -*- coding: utf-8 -*-

import colorsys
import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
from shapely.geometry import Point, shape


# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GEOJSON_PATH = (
    BASE_DIR
    / "assets"
    / "seoul_gu.geojson"
)

SUBWAY_STATIONS_PATH = (
    BASE_DIR
    / "assets"
    / "subway_stations_.csv"
)


# =========================================================
# 지하철 노선 색상
# =========================================================

_OFFICIAL_LINE_COLORS = {

    # -----------------------------------------
    # 수도권 1~9호선
    # -----------------------------------------

    "1호선": [0, 82, 164],
    "2호선": [0, 168, 77],
    "3호선": [239, 124, 28],
    "4호선": [0, 165, 222],
    "5호선": [153, 108, 172],
    "6호선": [205, 124, 47],
    "7호선": [116, 127, 0],
    "8호선": [230, 24, 108],
    "9호선": [189, 176, 146],

    # -----------------------------------------
    # 수도권 광역철도
    # -----------------------------------------

    "경의중앙선": [119, 196, 163],
    "수인분당선": [250, 190, 0],
    "신분당선": [212, 0, 59],
    "경춘선": [12, 142, 114],
    "경강선": [0, 61, 165],
    "서해선": [143, 195, 31],

    # -----------------------------------------
    # 기타 수도권 노선
    # -----------------------------------------

    "공항철도": [0, 144, 210],
    "우이신설선": [176, 206, 24],
    "신림선": [103, 137, 202],
    "김포골드라인": [173, 134, 5],

    # -----------------------------------------
    # 인천
    # -----------------------------------------

    "인천1호선": [124, 168, 213],
    "인천2호선": [237, 139, 0],
}


# =========================================================
# 자동 색상 생성
# =========================================================

def _hsv_to_rgb255(h, s, v):

    r, g, b = colorsys.hsv_to_rgb(
        h,
        s,
        v,
    )

    return [
        int(r * 255),
        int(g * 255),
        int(b * 255),
    ]


def _build_color_palette(line_groups):

    color_map = {}

    remaining = []

    # -----------------------------------------------------
    # 공식 색상이 있는 노선
    # -----------------------------------------------------

    for line_group in line_groups:

        if line_group in _OFFICIAL_LINE_COLORS:

            color_map[line_group] = (
                _OFFICIAL_LINE_COLORS[line_group]
            )

        else:

            remaining.append(
                line_group
            )

    # -----------------------------------------------------
    # 공식 색상이 없는 노선은 자동 색상
    # -----------------------------------------------------

    n = len(remaining)

    for idx, line_group in enumerate(
        remaining
    ):

        hue = idx / max(n, 1)

        color_map[line_group] = (
            _hsv_to_rgb255(
                hue,
                0.55,
                0.85,
            )
        )

    return color_map


# =========================================================
# 지하철역 데이터 로드
# =========================================================

@st.cache_data(
    show_spinner=False
)
def _load_subway_stations(
    path_str,
    geojson_path_str,
):

    path = Path(
        path_str
    )

    geojson_path = Path(
        geojson_path_str
    )

    # =====================================================
    # 파일 존재 여부
    # =====================================================

    if not path.exists():

        return pd.DataFrame(
            columns=[
                "station",
                "line",
                "lat",
                "lon",
                "color",
            ]
        )

    # =====================================================
    # CSV 읽기
    # =====================================================

    subway = pd.read_csv(
        path,
        encoding="utf-8-sig",
    )

    # =====================================================
    # 컬럼명 변경
    # =====================================================

    subway = subway.rename(
        columns={
            "역명": "station",
            "호선": "line",
            "경도": "lon",
            "위도": "lat",
        }
    )

    # =====================================================
    # 필요한 컬럼만 사용
    # =====================================================

    subway = subway[
        [
            "station",
            "line",
            "lon",
            "lat",
        ]
    ].copy()

    # =====================================================
    # 숫자 변환
    # =====================================================

    subway["lon"] = pd.to_numeric(
        subway["lon"],
        errors="coerce",
    )

    subway["lat"] = pd.to_numeric(
        subway["lat"],
        errors="coerce",
    )

    # =====================================================
    # 결측치 제거
    # =====================================================

    subway = subway.dropna(
        subset=[
            "station",
            "line",
            "lon",
            "lat",
        ]
    ).copy()

    # =====================================================
    # 문자열 정리
    # =====================================================

    subway["station"] = (
        subway["station"]
        .astype(str)
        .str.strip()
    )

    subway["line"] = (
        subway["line"]
        .astype(str)
        .str.strip()
    )

    # =====================================================
    # 서울시 GeoJSON 읽기
    # =====================================================

    with open(
        geojson_path,
        "r",
        encoding="utf-8",
    ) as geojson_file:

        seoul_geojson = json.load(
            geojson_file
        )

    # =====================================================
    # 서울시 polygon 생성
    # =====================================================

    seoul_polygons = []

    for feature in seoul_geojson.get(
        "features",
        []
    ):

        geometry = feature.get(
            "geometry"
        )

        if geometry:

            try:

                seoul_polygons.append(
                    shape(geometry)
                )

            except Exception:

                continue

    # =====================================================
    # 서울시 내부 역만 추출
    # =====================================================

    def is_in_seoul(row):

        point = Point(
            row["lon"],
            row["lat"],
        )

        return any(
            polygon.contains(point)
            or polygon.touches(point)
            for polygon in seoul_polygons
        )

    subway["서울시_내부"] = subway.apply(
        is_in_seoul,
        axis=1,
    )

    subway = subway[
        subway["서울시_내부"]
    ].copy()

    subway = subway.drop(
        columns=[
            "서울시_내부"
        ]
    )

    # =====================================================
    # 호선별 색상 생성
    # =====================================================

    line_groups = sorted(
        subway["line"].unique()
    )

    color_map = (
        _build_color_palette(
            line_groups
        )
    )

    subway["color"] = (
        subway["line"]
        .map(color_map)
    )

    return subway


# =========================================================
# 역 표시용 데이터 생성
# =========================================================

def _prepare_station_display_data(
    subway
):

    if subway.empty:

        return pd.DataFrame(
            columns=[
                "station",
                "lat",
                "lon",
                "lines",
                "line_count",
            ]
        )

    station_groups = []

    for station, group in subway.groupby(
        "station"
    ):

        # -------------------------------------------------
        # 같은 역의 좌표 평균
        # -------------------------------------------------

        lon = group["lon"].mean()
        lat = group["lat"].mean()

        # -------------------------------------------------
        # 환승 호선
        # -------------------------------------------------

        lines = (
            group["line"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        station_groups.append(
            {
                "station": station,
                "lat": lat,
                "lon": lon,
                "lines": ", ".join(lines),
                "line_count": len(lines),
            }
        )

    return pd.DataFrame(
        station_groups
    )


# =========================================================
# 지하철역 Layer
# =========================================================

def _get_subway_station_layers(
    subway
):

    if subway.empty:

        return []

    station_df = (
        _prepare_station_display_data(
            subway
        )
    )

    layers = []

    # =====================================================
    # 1. 역 기본 점
    #
    # 흰색으로 크게 덮지 않고
    # 작은 흰색 점 + 얇은 테두리만 표시
    # =====================================================

    station_base_layer = pdk.Layer(
        "ScatterplotLayer",

        data=station_df,

        get_position="[lon, lat]",

        get_radius=38,

        get_fill_color=[
            255,
            255,
            255,
            220,
        ],

        get_line_color=[
            100,
            100,
            100,
            180,
        ],

        stroked=True,

        line_width_min_pixels=2,

        pickable=True,

        auto_highlight=True,

        tooltip=SUBWAY_TOOLTIP,
    )

    layers.append(
        station_base_layer
    )

    # =====================================================
    # 2. 호선별 색상 점
    # =====================================================

    for line in sorted(
        subway["line"].unique()
    ):

        line_df = subway[
            subway["line"] == line
        ].copy()

        line_df = line_df[
            [
                "station",
                "lon",
                "lat",
                "color",
            ]
        ].drop_duplicates(
            subset=[
                "station"
            ]
        )

        if line_df.empty:
            continue

        color = (
            line_df[
                "color"
            ].iloc[0]
        )

        line_layer = pdk.Layer(
            "ScatterplotLayer",

            data=line_df,

            get_position="[lon, lat]",

            get_radius=28,

            get_fill_color=[
                color[0],
                color[1],
                color[2],
                255,
            ],

            get_line_color=[
                255,
                255,
                255,
                255,
            ],

            stroked=True,

            line_width_min_pixels=2,

            pickable=True,

            auto_highlight=True,

            tooltip=SUBWAY_TOOLTIP,
        )

        layers.append(
            line_layer
        )

    return layers


# =========================================================
# 거래 데이터 Tooltip
# =========================================================

TRANSACTION_TOOLTIP = {
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


# =========================================================
# 지하철역 Tooltip
# =========================================================

SUBWAY_TOOLTIP = {
    "html": (
        "<b>🚇 {station}</b><br/>"
        "호선: {lines}"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "12px",
        "padding": "8px",
    },
}


# =========================================================
# 자치구 Tooltip
# =========================================================

DISTRICT_TOOLTIP = {
    "html": (
        "<b>📍 {district_name}</b>"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "12px",
        "padding": "8px",
    },
}


# =========================================================
# 지도 렌더링
# =========================================================

def render_map(
    df,
    f,
    view_type,
    selected_place,
):

    st.markdown(
        "#### 🗺️ 거래 위치 지도"
    )

    # =====================================================
    # 서울시 GeoJSON
    # =====================================================

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
    # 지하철역 데이터
    # =====================================================

    subway = _load_subway_stations(
        str(
            SUBWAY_STATIONS_PATH
        ),
        str(
            GEOJSON_PATH
        ),
    )

    subway_layers = (
        _get_subway_station_layers(
            subway
        )
    )

    # =====================================================
    # 거래 데이터
    # =====================================================

    map_df = (
        f[
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
        ]
        .dropna(
            subset=[
                "위도",
                "경도",
            ]
        )
        .copy()
    )

    # =====================================================
    # 거래 데이터 최대 15,000건
    # =====================================================

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

        # -------------------------------------------------
        # 선택 자치구 GeoJSON
        # -------------------------------------------------

        selected_features = []

        for feature in seoul_geojson.get(
            "features",
            []
        ):

            properties = feature.get(
                "properties",
                {}
            )

            geo_name = (
                properties.get(
                    "SIG_KOR_NM"
                )
                or properties.get(
                    "name"
                )
                or properties.get(
                    "자치구명"
                )
            )

            if geo_name == selected_place:

                feature_copy = feature.copy()

                feature_copy[
                    "properties"
                ] = {
                    **feature.get(
                        "properties",
                        {}
                    ),
                    "district_name": geo_name,
                }

                selected_features.append(
                    feature_copy
                )

        selected_boundary = {
            "type": "FeatureCollection",
            "features": selected_features,
        }

        # -------------------------------------------------
        # 선택 자치구 거래만
        # -------------------------------------------------

        map_df = map_df[
            map_df["자치구명"]
            == selected_place
        ].copy()

        # -------------------------------------------------
        # 지도 중심
        # -------------------------------------------------

        if len(map_df) > 0:

            center_lat = (
                map_df["위도"].mean()
            )

            center_lon = (
                map_df["경도"].mean()
            )

        else:

            center_lat = 37.5172
            center_lon = 127.0473

        # -------------------------------------------------
        # 자치구 경계
        # -------------------------------------------------

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

            tooltip=DISTRICT_TOOLTIP,
        )

        # -------------------------------------------------
        # 거래 위치
        # -------------------------------------------------

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

            tooltip=TRANSACTION_TOOLTIP,
        )

        # -------------------------------------------------
        # 지도
        # -------------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12,
            pitch=0,
        )

        layers = [
            boundary_layer,
            *subway_layers,
            point_layer,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

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
            f"🚇 {selected_place}의 "
            "역세권 거래 위치를 표시합니다."
        )

        # -------------------------------------------------
        # 선택 노선 거래
        # -------------------------------------------------

        map_df = map_df[
            map_df[
                "최근접역_호선"
            ]
            .str.contains(
                selected_place,
                na=False,
            )
        ].copy()

        # -------------------------------------------------
        # 지도 중심
        # -------------------------------------------------

        if len(map_df) > 0:

            center_lat = (
                map_df["위도"].mean()
            )

            center_lon = (
                map_df["경도"].mean()
            )

        else:

            center_lat = 37.5665
            center_lon = 126.9780

        # -------------------------------------------------
        # 거래 위치
        # -------------------------------------------------

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

            tooltip=TRANSACTION_TOOLTIP,
        )

        # -------------------------------------------------
        # 지도
        # -------------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12.5,
            pitch=0,
        )

        layers = [
            *subway_layers,
            point_layer,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

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
            f"📍 {selected_place} 주변 "
            "거래 위치를 표시합니다."
        )

        # -------------------------------------------------
        # 선택 역 거래
        # -------------------------------------------------

        map_df = map_df[
            map_df["최근접역"]
            == selected_place
        ].copy()

        # -------------------------------------------------
        # 지도 중심
        # -------------------------------------------------

        if len(map_df) > 0:

            center_lat = (
                map_df["위도"].mean()
            )

            center_lon = (
                map_df["경도"].mean()
            )

        else:

            station_info = df[
                df["최근접역"]
                == selected_place
            ][
                [
                    "최근접역_위도",
                    "최근접역_경도",
                ]
            ].dropna()

            if len(station_info) > 0:

                center_lat = (
                    station_info[
                        "최근접역_위도"
                    ].iloc[0]
                )

                center_lon = (
                    station_info[
                        "최근접역_경도"
                    ].iloc[0]

                )

            else:

                center_lat = 37.5665
                center_lon = 126.9780

        # -------------------------------------------------
        # 거래 위치
        # -------------------------------------------------

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

            tooltip=TRANSACTION_TOOLTIP,
        )

        # -------------------------------------------------
        # 선택 역 강조
        # -------------------------------------------------

        station_info = (
            subway[
                subway["station"]
                == selected_place
            ][
                [
                    "station",
                    "line",
                    "lon",
                    "lat",
                ]
            ]
            .drop_duplicates(
                subset=[
                    "station",
                    "line",
                    "lon",
                    "lat",
                ]
            )
            .copy()
        )

        # -------------------------------------------------
        # 선택 역이 역사마스터에 없으면
        # 기존 전월세 데이터 좌표 사용
        # -------------------------------------------------

        if station_info.empty:

            station_info = (
                df[
                    df["최근접역"]
                    == selected_place
                ][
                    [
                        "최근접역_위도",
                        "최근접역_경도",
                    ]
                ]
                .dropna()
                .drop_duplicates(
                    subset=[
                        "최근접역_위도",
                        "최근접역_경도",
                    ]
                )
                .rename(
                    columns={
                        "최근접역_위도": "lat",
                        "최근접역_경도": "lon",
                    }
                )
            )

        # -------------------------------------------------
        # 선택 역 Layer
        # -------------------------------------------------

        station_layer = pdk.Layer(
            "ScatterplotLayer",

            data=station_info,

            get_position="[lon, lat]",

            get_radius=70,

            # 흰색 면 제거
            get_fill_color=[
                255,
                255,
                255,
                0,
            ],

            # 파란색 테두리
            get_line_color=[
                30,
                80,
                200,
                255,
            ],

            stroked=True,

            line_width_min_pixels=4,

            pickable=True,

            auto_highlight=True,

            tooltip=SUBWAY_TOOLTIP,
        )

        # -------------------------------------------------
        # 지도
        # -------------------------------------------------

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=14,
            pitch=0,
        )

        layers = [
            *subway_layers,
            point_layer,
            station_layer,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",
            ),

            use_container_width=True,
        )

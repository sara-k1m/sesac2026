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
# Tooltip
# =========================================================

# ---------------------------------------------------------
# 거래 데이터 Tooltip
# ---------------------------------------------------------

TRANSACTION_TOOLTIP = {
    "html": (
        "<div style='font-family: Arial, sans-serif;'>"
        "<b>🏠 거래 정보</b><br/>"
        "<hr style='margin:4px 0;'>"
        "자치구: {자치구명}<br/>"
        "최근접역: {최근접역}<br/>"
        "호선: {최근접역_호선}<br/>"
        "월세: {임대료(만원)}만원<br/>"
        "보증금: {보증금(만원)}만원<br/>"
        "면적: {임대면적}㎡<br/>"
        "역까지 거리: {최근접역_거리(m)}m"
        "</div>"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "13px",
        "padding": "10px",
        "borderRadius": "6px",
    },
}


# ---------------------------------------------------------
# 지하철역 Tooltip
# ---------------------------------------------------------

SUBWAY_TOOLTIP = {
    "html": (
        "<div style='font-family: Arial, sans-serif;'>"
        "<b>🚇 {station}</b><br/>"
        "호선: {lines}"
        "</div>"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "13px",
        "padding": "10px",
        "borderRadius": "6px",
    },
}


# ---------------------------------------------------------
# 자치구 Tooltip
# ---------------------------------------------------------

DISTRICT_TOOLTIP = {
    "html": (
        "<div style='font-family: Arial, sans-serif;'>"
        "<b>📍 자치구</b><br/>"
        "자치구: {district_name}"
        "</div>"
    ),
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "13px",
        "padding": "10px",
        "borderRadius": "6px",
    },
}


# =========================================================
# 지하철 노선 색상
# =========================================================

_OFFICIAL_LINE_COLORS = {

    "1호선": [0, 82, 164],
    "2호선": [0, 168, 77],
    "3호선": [239, 124, 28],
    "4호선": [0, 165, 222],
    "5호선": [153, 108, 172],
    "6호선": [205, 124, 47],
    "7호선": [116, 127, 0],
    "8호선": [230, 24, 108],
    "9호선": [189, 176, 146],

    "경의중앙선": [119, 196, 163],
    "수인분당선": [250, 190, 0],
    "신분당선": [212, 0, 59],
    "경춘선": [12, 142, 114],
    "경강선": [0, 61, 165],
    "서해선": [143, 195, 31],

    "공항철도": [0, 144, 210],
    "우이신설선": [176, 206, 24],
    "신림선": [103, 137, 202],
    "김포골드라인": [173, 134, 5],

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

    for line_group in line_groups:

        if line_group in _OFFICIAL_LINE_COLORS:

            color_map[line_group] = (
                _OFFICIAL_LINE_COLORS[line_group]
            )

        else:

            remaining.append(
                line_group
            )

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

@st.cache_data(show_spinner=False)
def _load_subway_stations(
    path_str,
    geojson_path_str,
):

    path = Path(path_str)

    geojson_path = Path(
        geojson_path_str
    )

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

    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    subway = pd.read_csv(
        path,
        encoding="utf-8-sig",
    )

    # -----------------------------------------------------
    # 컬럼명
    # -----------------------------------------------------

    subway = subway.rename(
        columns={
            "역명": "station",
            "호선": "line",
            "경도": "lon",
            "위도": "lat",
        }
    )

    required_columns = [
        "station",
        "line",
        "lon",
        "lat",
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in subway.columns
    ]

    if missing_columns:

        st.error(
            "지하철역 CSV에 다음 컬럼이 없습니다: "
            + ", ".join(missing_columns)
        )

        return pd.DataFrame(
            columns=[
                "station",
                "line",
                "lat",
                "lon",
                "color",
            ]
        )

    subway = subway[
        required_columns
    ].copy()

    # -----------------------------------------------------
    # 숫자 변환
    # -----------------------------------------------------

    subway["lon"] = pd.to_numeric(
        subway["lon"],
        errors="coerce",
    )

    subway["lat"] = pd.to_numeric(
        subway["lat"],
        errors="coerce",
    )

    subway = subway.dropna(
        subset=[
            "station",
            "line",
            "lon",
            "lat",
        ]
    ).copy()

    # -----------------------------------------------------
    # 문자열 정리
    # -----------------------------------------------------

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
    # 서울시 GeoJSON
    # =====================================================

    if not geojson_path.exists():

        st.warning(
            "서울시 GeoJSON 파일을 찾을 수 없어 "
            "지하철역의 서울시 내부 여부를 확인하지 않습니다."
        )

        subway["서울시_내부"] = True

    else:

        with open(
            geojson_path,
            "r",
            encoding="utf-8",
        ) as geojson_file:

            seoul_geojson = json.load(
                geojson_file
            )

        # =================================================
        # 서울시 Polygon
        # =================================================

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

        # =================================================
        # 서울시 내부 역만
        # =================================================

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
    # 호선 색상
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
# 특정 호선 필터
# =========================================================

def _filter_subway_by_line(
    subway,
    selected_line,
):

    if subway.empty:
        return subway.copy()

    if not selected_line:
        return subway.copy()

    selected_line = str(
        selected_line
    ).strip()

    # -----------------------------------------------------
    # 호선 컬럼의 값과 정확히 일치하는 경우
    # -----------------------------------------------------

    exact_match = subway[
        subway["line"]
        == selected_line
    ].copy()

    if not exact_match.empty:
        return exact_match

    # -----------------------------------------------------
    # 데이터에 "2호선 외선" 등 부가 문자열이 있을 경우
    # -----------------------------------------------------

    filtered = subway[
        subway["line"]
        .astype(str)
        .str.contains(
            selected_line,
            case=False,
            na=False,
            regex=False,
        )
    ].copy()

    return filtered


# =========================================================
# 역 표시용 데이터
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
                "color",
            ]
        )

    station_groups = []

    for station, group in subway.groupby(
        "station"
    ):

        lat = group["lat"].mean()
        lon = group["lon"].mean()

        lines = (
            group["line"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        # -------------------------------------------------
        # 대표 색상
        #
        # 한 역에 여러 호선이 있는 환승역은
        # 첫 번째 호선 색상을 대표 색상으로 사용합니다.
        #
        # 노선 필터가 적용된 경우에는 해당 노선만
        # 남기 때문에 자연스럽게 선택된 노선 색상이 됩니다.
        # -------------------------------------------------

        first_color = (
            group["color"].iloc[0]
            if len(group) > 0
            else [80, 80, 80]
        )

        station_groups.append(
            {
                "station": station,
                "lat": lat,
                "lon": lon,
                "lines": ", ".join(lines),
                "line_count": len(lines),
                "color": first_color,
            }
        )

    station_df = pd.DataFrame(
        station_groups
    )

    # -----------------------------------------------------
    # 색상 분리
    # -----------------------------------------------------

    if not station_df.empty:

        station_df[
            [
                "color_r",
                "color_g",
                "color_b",
            ]
        ] = pd.DataFrame(
            station_df["color"].tolist(),
            index=station_df.index,
        )

    return station_df


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

    if station_df.empty:
        return []

    layers = []

    # =====================================================
    # 1. 지하철역 원
    # =====================================================

    station_base_layer = pdk.Layer(
        "ScatterplotLayer",

        data=station_df,

        get_position="[lon, lat]",

        # 기존 30 → 55
        get_radius=55,

        # 호선 색상 + 완전 불투명
        get_fill_color=[
            "color_r",
            "color_g",
            "color_b",
            255,
        ],

        # 흰색 외곽선
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
        station_base_layer
    )

    # =====================================================
    # 2. 역 이름
    # =====================================================

    station_text_layer = pdk.Layer(
        "TextLayer",

        data=station_df,

        get_position="[lon, lat]",

        get_text="station",

        # 역 이름 크기
        get_size=14,

        get_color=[
            20,
            30,
            45,
            255,
        ],

        # 원 아래쪽에 이름 배치
        get_pixel_offset=[
            0,
            32,
        ],

        get_text_anchor="middle",

        get_alignment_baseline="top",

        billboard=True,

        pickable=False,

        font_family="Arial, sans-serif",

        font_weight=600,
    )

    layers.append(
        station_text_layer
    )

    return layers


# =========================================================
# 선택된 역 강조 Layer
# =========================================================

def _get_selected_station_layer(
    station_info
):

    if station_info.empty:
        return None

    # -----------------------------------------------------
    # 컬러가 있으면 대표 색상 사용
    # -----------------------------------------------------

    if "color" in station_info.columns:

        colors = station_info[
            "color"
        ].tolist()

        if colors:

            color = colors[0]

        else:

            color = [
                30,
                80,
                200,
            ]

    else:

        color = [
            30,
            80,
            200,
        ]

    station_info = station_info.copy()

    station_info["color_r"] = color[0]
    station_info["color_g"] = color[1]
    station_info["color_b"] = color[2]

    # =====================================================
    # 선택 역 원
    # =====================================================

    selected_station_circle = pdk.Layer(
        "ScatterplotLayer",

        data=station_info,

        get_position="[lon, lat]",

        get_radius=90,

        get_fill_color=[
            "color_r",
            "color_g",
            "color_b",
            255,
        ],

        get_line_color=[
            255,
            255,
            255,
            255,
        ],

        stroked=True,

        line_width_min_pixels=4,

        pickable=True,

        auto_highlight=True,

        tooltip=SUBWAY_TOOLTIP,
    )

    # =====================================================
    # 선택 역 이름
    # =====================================================

    selected_station_text = pdk.Layer(
        "TextLayer",

        data=station_info,

        get_position="[lon, lat]",

        get_text="station",

        get_size=16,

        get_color=[
            20,
            30,
            45,
            255,
        ],

        get_pixel_offset=[
            0,
            48,
        ],

        get_text_anchor="middle",

        get_alignment_baseline="top",

        billboard=True,

        pickable=False,

        font_family="Arial, sans-serif",

        font_weight=700,
    )

    return [
        selected_station_circle,
        selected_station_text,
    ]


# =========================================================
# 지도
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
    # GeoJSON
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
    # 지하철 데이터
    # =====================================================

    subway = _load_subway_stations(
        str(SUBWAY_STATIONS_PATH),
        str(GEOJSON_PATH),
    )

    # =====================================================
    # 거래 데이터
    # =====================================================

    transaction_columns = [
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

    available_transaction_columns = [
        col
        for col in transaction_columns
        if col in f.columns
    ]

    map_df = f[
        available_transaction_columns
    ].dropna(
        subset=[
            col
            for col in [
                "위도",
                "경도",
            ]
            if col in available_transaction_columns
        ]
    ).copy()

    # =====================================================
    # 최대 15,000건
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
        # 선택 자치구
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
        # 해당 자치구 거래
        # -------------------------------------------------

        if "자치구명" in map_df.columns:

            map_df = map_df[
                map_df["자치구명"]
                == selected_place
            ].copy()

        # -------------------------------------------------
        # 중심
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
        # 자치구 Layer
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
        # 거래 Layer
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
                190,
            ],

            get_line_color=[
                255,
                255,
                255,
                255,
            ],

            stroked=True,

            line_width_min_pixels=1,

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

        # -------------------------------------------------
        # Layer 순서
        #
        # 자치구 → 지하철역 → 거래점
        #
        # 거래점이 가장 위에 있으므로
        # 거래점 클릭/hover가 우선적으로 잡힙니다.
        # -------------------------------------------------

        layers = [
            boundary_layer,
            *_get_subway_station_layers(subway),
            point_layer,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",

                tooltip={
                    "style": {
                        "backgroundColor": "white",
                        "color": "#172033",
                    }
                },
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
            "역세권 거래 위치와 해당 호선의 지하철역을 표시합니다."
        )

        # =================================================
        # 해당 노선 거래
        # =================================================

        if "최근접역_호선" in map_df.columns:

            map_df = map_df[
                map_df[
                    "최근접역_호선"
                ]
                .astype(str)
                .str.contains(
                    str(selected_place),
                    na=False,
                    regex=False,
                )
            ].copy()

        # =================================================
        # 해당 노선 지하철역만 필터
        #
        # ★ 핵심 수정사항
        # =================================================

        subway_line = (
            _filter_subway_by_line(
                subway,
                selected_place,
            )
        )

        # =================================================
        # 중심
        # =================================================

        if len(map_df) > 0:

            center_lat = (
                map_df["위도"].mean()
            )

            center_lon = (
                map_df["경도"].mean()
            )

        elif not subway_line.empty:

            center_lat = (
                subway_line["lat"].mean()
            )

            center_lon = (
                subway_line["lon"].mean()
            )

        else:

            center_lat = 37.5665
            center_lon = 126.9780

        # =================================================
        # 거래 Layer
        # =================================================

        point_layer = pdk.Layer(
            "ScatterplotLayer",

            data=map_df,

            get_position="[경도, 위도]",

            get_radius=35,

            get_fill_color=[
                50,
                120,
                200,
                190,
            ],

            get_line_color=[
                255,
                255,
                255,
                255,
            ],

            stroked=True,

            line_width_min_pixels=1,

            pickable=True,

            auto_highlight=True,

            tooltip=TRANSACTION_TOOLTIP,
        )

        # =================================================
        # 지하철역 Layer
        #
        # ★ 선택된 호선의 역만 표시
        # =================================================

        subway_layers = (
            _get_subway_station_layers(
                subway_line
            )
        )

        # =================================================
        # 지도
        # =================================================

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

                tooltip={
                    "style": {
                        "backgroundColor": "white",
                        "color": "#172033",
                    }
                },
            ),

            use_container_width=True,

            height=750,
        )

    # =====================================================
    # 역
    # =====================================================

    else:

        st.caption(
            f"📍 {selected_place} 주변 "
            "거래 위치를 표시합니다."
        )

        # =================================================
        # 선택 역 거래
        # =================================================

        if "최근접역" in map_df.columns:

            map_df = map_df[
                map_df["최근접역"]
                == selected_place
            ].copy()

        # =================================================
        # 지도 중심
        # =================================================

        if len(map_df) > 0:

            center_lat = (
                map_df["위도"].mean()
            )

            center_lon = (
                map_df["경도"].mean()
            )

        else:

            station_info_from_df = df[
                df["최근접역"]
                == selected_place
            ][
                [
                    "최근접역_위도",
                    "최근접역_경도",
                ]
            ].dropna()

            if len(
                station_info_from_df
            ) > 0:

                center_lat = (
                    station_info_from_df[
                        "최근접역_위도"
                    ].iloc[0]
                )

                center_lon = (
                    station_info_from_df[
                        "최근접역_경도"
                    ].iloc[0]
                )

            else:

                center_lat = 37.5665
                center_lon = 126.9780

        # =================================================
        # 거래 위치 Layer
        # =================================================

        point_layer = pdk.Layer(
            "ScatterplotLayer",

            data=map_df,

            get_position="[경도, 위도]",

            get_radius=30,

            get_fill_color=[
                220,
                70,
                70,
                190,
            ],

            get_line_color=[
                255,
                255,
                255,
                255,
            ],

            stroked=True,

            line_width_min_pixels=1,

            pickable=True,

            auto_highlight=True,

            tooltip=TRANSACTION_TOOLTIP,
        )

        # =================================================
        # 선택된 역 정보
        # =================================================

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
                    "color",
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

        # =================================================
        # 선택 역의 Tooltip용 호선 정보
        # =================================================

        if not station_info.empty:

            station_lines = (
                station_info["line"]
                .drop_duplicates()
                .tolist()
            )

            station_info = (
                station_info
                .groupby(
                    [
                        "station",
                        "lon",
                        "lat",
                    ],
                    as_index=False,
                )
                .agg(
                    {
                        "color": "first",
                    }
                )
            )

            station_info["lines"] = (
                ", ".join(
                    station_lines
                )
            )

        # =================================================
        # 역사마스터에 없을 경우
        # 기존 거래 데이터 좌표 사용
        # =================================================

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

            # Tooltip용 컬럼 추가
            station_info["station"] = (
                selected_place
            )

            station_info["lines"] = ""

            station_info["color"] = [
                [
                    30,
                    80,
                    200,
                ]
            ] * len(station_info)

        # =================================================
        # 선택 역 강조
        # =================================================

        selected_station_layers = (
            _get_selected_station_layer(
                station_info
            )
        )

        if selected_station_layers is None:

            selected_station_layers = []

        # =================================================
        # 역 지도
        #
        # 선택 역 화면에서는 전체 역을 보여주지 않고
        # 선택된 역을 강조해서 보여줍니다.
        # =================================================

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=14,
            pitch=0,
        )

        layers = [
            point_layer,
            *selected_station_layers,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",

                tooltip={
                    "style": {
                        "backgroundColor": "white",
                        "color": "#172033",
                    }
                },
            ),

            use_container_width=True,

            height=750,
        )

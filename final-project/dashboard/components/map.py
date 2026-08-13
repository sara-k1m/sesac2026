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
# 전체 Tooltip
#
# HTML을 사용하지 않고 text 방식 사용
# =========================================================

DECK_TOOLTIP = {
    "text": "{tooltip_text}",
    "style": {
        "backgroundColor": "white",
        "color": "#172033",
        "fontSize": "13px",
        "padding": "10px",
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
# 표시용 값
# =========================================================

def _display_value(value):

    if value is None:
        return "-"

    try:

        if pd.isna(value):
            return "-"

    except Exception:
        pass

    return str(value)


# =========================================================
# 거래 Tooltip
# =========================================================

def _make_transaction_tooltip(row):

    district = _display_value(
        row.get("자치구명")
    )

    station = _display_value(
        row.get("최근접역")
    )

    line = _display_value(
        row.get("최근접역_호선")
    )

    rent = _display_value(
        row.get("임대료(만원)")
    )

    deposit = _display_value(
        row.get("보증금(만원)")
    )

    area = _display_value(
        row.get("임대면적")
    )

    distance = _display_value(
        row.get("최근접역_거리(m)")
    )

    return (
        "🏠 거래 정보\n"
        f"자치구: {district}\n"
        f"최근접역: {station}\n"
        f"호선: {line}\n"
        f"월세: {rent}만원\n"
        f"보증금: {deposit}만원\n"
        f"면적: {area}㎡\n"
        f"역까지 거리: {distance}m"
    )


# =========================================================
# 역 Tooltip
# =========================================================

def _make_station_tooltip(
    station,
    lines,
):

    station = _display_value(station)
    lines = _display_value(lines)

    return (
        f"🚇 {station}\n"
        f"호선: {lines}"
    )


# =========================================================
# 자치구 Tooltip
# =========================================================

def _make_district_tooltip(
    district_name,
):

    district_name = _display_value(
        district_name
    )

    return (
        "📍 자치구\n"
        f"자치구: {district_name}"
    )


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

    empty_columns = [
        "station",
        "line",
        "lat",
        "lon",
        "color",
    ]

    if not path.exists():

        return pd.DataFrame(
            columns=empty_columns
        )

    # =====================================================
    # CSV
    # =====================================================

    subway = pd.read_csv(
        path,
        encoding="utf-8-sig",
    )

    # =====================================================
    # 컬럼명
    # =====================================================

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
            + ", ".join(
                missing_columns
            )
        )

        return pd.DataFrame(
            columns=empty_columns
        )

    subway = subway[
        required_columns
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
    # 서울시 GeoJSON
    # =====================================================

    if geojson_path.exists():

        with open(
            geojson_path,
            "r",
            encoding="utf-8",
        ) as geojson_file:

            seoul_geojson = json.load(
                geojson_file
            )

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

        if seoul_polygons:

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
# 호선별 지하철역 필터
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

    # =====================================================
    # 정확히 일치
    # =====================================================

    exact = subway[
        subway["line"]
        == selected_line
    ].copy()

    if not exact.empty:

        return exact

    # =====================================================
    # 포함 검색
    # =====================================================

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
                "color_r",
                "color_g",
                "color_b",
                "tooltip_text",
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

        # =================================================
        # 대표 색상
        #
        # 여러 호선이 만나는 역의 경우
        # 첫 번째 호선 색상을 대표색으로 사용
        # =================================================

        if len(group) > 0:

            color = group[
                "color"
            ].iloc[0]

        else:

            color = [
                80,
                80,
                80,
            ]

        station_groups.append(
            {
                "station": station,
                "lat": lat,
                "lon": lon,
                "lines": ", ".join(lines),
                "line_count": len(lines),
                "color_r": color[0],
                "color_g": color[1],
                "color_b": color[2],
                "tooltip_text": (
                    _make_station_tooltip(
                        station,
                        ", ".join(lines),
                    )
                ),
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

    if station_df.empty:

        return []

    layers = []

    # =====================================================
    # 역 원
    # =====================================================

    station_layer = pdk.Layer(
        "ScatterplotLayer",

        data=station_df,

        get_position="[lon, lat]",

        # 역 원 크기
        get_radius=55,

        # 호선 고유 색상
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
    )

    layers.append(
        station_layer
    )

    # =====================================================
    # 역 이름
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

        # 역 원 아래쪽
        get_pixel_offset=[
            0,
            34,
        ],

        get_text_anchor="middle",

        get_alignment_baseline="top",

        billboard=True,

        # 텍스트는 hover 대상 아님
        pickable=False,

        font_family="Arial, sans-serif",

        font_weight=600,
    )

    layers.append(
        station_text_layer
    )

    return layers


# =========================================================
# 거래 데이터 Tooltip 준비
# =========================================================

def _prepare_transaction_data(
    map_df
):

    map_df = map_df.copy()

    if map_df.empty:

        map_df["tooltip_text"] = pd.Series(
            dtype="object"
        )

        return map_df

    map_df["tooltip_text"] = map_df.apply(
        _make_transaction_tooltip,
        axis=1,
    )

    return map_df


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
    # 거래 데이터 컬럼
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

    missing_transaction_columns = [
        col
        for col in transaction_columns
        if col not in f.columns
    ]

    if missing_transaction_columns:

        st.error(
            "거래 데이터에 다음 컬럼이 없습니다: "
            + ", ".join(
                missing_transaction_columns
            )
        )

        return

    map_df = f[
        transaction_columns
    ].dropna(
        subset=[
            "위도",
            "경도",
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

        # =================================================
        # 선택 자치구 GeoJSON
        # =================================================

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

                # -------------------------------------------------
                # ★ 중요
                # 자치구에는 자치구 Tooltip을 넣어야 함
                # -------------------------------------------------

                feature_copy[
                    "properties"
                ] = {
                    **feature.get(
                        "properties",
                        {}
                    ),
                    "district_name": geo_name,
                    "tooltip_text": (
                        _make_district_tooltip(
                            geo_name
                        )
                    ),
                }

                selected_features.append(
                    feature_copy
                )

        selected_boundary = {
            "type": "FeatureCollection",
            "features": selected_features,
        }

        # =================================================
        # 해당 자치구 거래
        # =================================================

        map_df = map_df[
            map_df["자치구명"]
            == selected_place
        ].copy()

        map_df = _prepare_transaction_data(
            map_df
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

        elif selected_features:

            # GeoJSON bounds를 이용한 중심 계산
            try:

                geometry_list = [
                    shape(
                        feature["geometry"]
                    )
                    for feature
                    in selected_features
                    if feature.get(
                        "geometry"
                    )
                ]

                if geometry_list:

                    merged_bounds = geometry_list[0]

                    for geom in geometry_list[1:]:

                        merged_bounds = (
                            merged_bounds.union(
                                geom
                            )
                        )

                    center = (
                        merged_bounds.centroid
                    )

                    center_lon = center.x
                    center_lat = center.y

                else:

                    center_lat = 37.5172
                    center_lon = 127.0473

            except Exception:

                center_lat = 37.5172
                center_lon = 127.0473

        else:

            center_lat = 37.5172
            center_lon = 127.0473

        # =================================================
        # 자치구 Layer
        # =================================================

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

        # =================================================
        # 거래 Layer
        # =================================================

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
        )

        # =================================================
        # 지도 중심
        # =================================================

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=12,
            pitch=0,
        )

        # =================================================
        # Layer 순서
        # =================================================

        layers = [
            # 자치구
            boundary_layer,

            # 전체 지하철역
            *_get_subway_station_layers(
                subway
            ),

            # 거래점
            point_layer,
        ]

        # =================================================
        # 지도
        # =================================================

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",

                tooltip=DECK_TOOLTIP,
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

        map_df = _prepare_transaction_data(
            map_df
        )

        # =================================================
        # 선택한 호선 역만 필터링
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
        )

        # =================================================
        # 선택 호선 역 Layer
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
            # 해당 호선 역만
            *subway_layers,

            # 거래점
            point_layer,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",

                tooltip=DECK_TOOLTIP,
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

        map_df = map_df[
            map_df["최근접역"]
            == selected_place
        ].copy()

        map_df = _prepare_transaction_data(
            map_df
        )

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
        )

        # =================================================
        # 선택 역 정보
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
        # 역사마스터에 있는 경우
        # =================================================

        if not station_info.empty:

            station_lines = (
                station_info["line"]
                .drop_duplicates()
                .tolist()
            )

            station_color = (
                station_info[
                    "color"
                ].iloc[0]
            )

            station_info = pd.DataFrame(
                [
                    {
                        "station": selected_place,

                        "lat": station_info[
                            "lat"
                        ].mean(),

                        "lon": station_info[
                            "lon"
                        ].mean(),

                        "lines": ", ".join(
                            station_lines
                        ),

                        "color_r": station_color[0],
                        "color_g": station_color[1],
                        "color_b": station_color[2],
                    }
                ]
            )

        # =================================================
        # 역사마스터에 없는 경우
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

            station_info["station"] = (
                selected_place
            )

            station_info["lines"] = ""

            station_info["color_r"] = 30
            station_info["color_g"] = 80
            station_info["color_b"] = 200

        # =================================================
        # 선택 역 Tooltip
        # =================================================

        if not station_info.empty:

            station_info["tooltip_text"] = (
                station_info.apply(
                    lambda row:
                    _make_station_tooltip(
                        row["station"],
                        row["lines"],
                    ),
                    axis=1,
                )
            )

        # =================================================
        # 선택 역 Layer
        # =================================================

        selected_station_layers = []

        if not station_info.empty:

            selected_station_layer = pdk.Layer(
                "ScatterplotLayer",

                data=station_info,

                get_position="[lon, lat]",

                # 크게 표시
                get_radius=90,

                # 호선 색상
                get_fill_color=[
                    "color_r",
                    "color_g",
                    "color_b",
                    255,
                ],

                # 흰색 테두리
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
            )

            selected_station_layers.append(
                selected_station_layer
            )

            # =================================================
            # 선택 역 이름
            # =================================================

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

                # 텍스트는 Tooltip을 가로채지 않음
                pickable=False,

                font_family="Arial, sans-serif",

                font_weight=700,
            )

            selected_station_layers.append(
                selected_station_text
            )

        # =================================================
        # 지도
        # =================================================

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=14,
            pitch=0,
        )

        layers = [
            # 거래점
            point_layer,

            # 선택 역
            *selected_station_layers,
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,

                initial_view_state=view_state,

                map_provider="carto",

                map_style="light",

                tooltip=DECK_TOOLTIP,
            ),

            use_container_width=True,

            height=750,
        )

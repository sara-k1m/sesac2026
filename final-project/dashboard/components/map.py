# -*- coding: utf-8 -*-

import colorsys
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

GEOJSON_PATH = BASE_DIR / "assets" / "seoul_gu.geojson"

# 지하철역_GEOM(역사마스터).csv 를 assets 폴더에 이 이름으로 넣어주세요.
# (파일명에 괄호가 있으면 경로 문제가 생길 수 있어 단순한 이름을 권장합니다)
SUBWAY_STATIONS_PATH = BASE_DIR / "assets" / "subway_stations_.csv"


# =========================================================
# 노선 색상
# =========================================================
# 주요 노선은 실제 공식 색상을 사용하고, 그 외(경부선/안산선 등 광역 노선)는
# 노선 개수에 맞춰 자동으로 서로 구분되는 색상을 생성합니다.

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
    "인천1호선": [124, 168, 213],
    "인천2호선": [237, 139, 0],
    "공항철도1호선": [0, 144, 210],
    "경의중앙선": [119, 196, 163],
    "분당선": [250, 190, 0],
    "신분당선": [212, 0, 59],
    "우이신설선": [176, 206, 24],
    "경춘선": [12, 142, 114],
    "수인선": [245, 162, 0],
    "서해선": [143, 195, 31],
    "경강선": [0, 61, 165],
    "김포골드라인": [173, 134, 5],
    "신림선": [103, 137, 202],
}


def _hsv_to_rgb255(h, s, v):

    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    return [int(r * 255), int(g * 255), int(b * 255)]


def _build_color_palette(line_groups):
    """공식 색상이 없는 노선에는 서로 구분되는 색상을 자동 배정한다."""

    color_map = {}
    remaining = []

    for line_group in line_groups:

        if line_group in _OFFICIAL_LINE_COLORS:
            color_map[line_group] = _OFFICIAL_LINE_COLORS[line_group]
        else:
            remaining.append(line_group)

    n = len(remaining)

    for idx, line_group in enumerate(remaining):

        hue = idx / max(n, 1)
        color_map[line_group] = _hsv_to_rgb255(hue, 0.55, 0.85)

    return color_map


def _haversine(lat1, lon1, lat2, lon2):

    r = 6371.0

    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = (
        np.sin(dphi / 2) ** 2
        + np.cos(p1) * np.cos(p2) * np.sin(dlambda / 2) ** 2
    )

    return 2 * r * np.arcsin(np.sqrt(a))


def _minimum_spanning_tree_edges(lats, lons):
    """
    Prim's algorithm 기반 최소 신장 트리(하버사인 거리 기준).

    역사마스터의 역번호만으로는 2호선(성수/신정 지선), 5호선(마천 지선)
    처럼 분기가 있는 노선의 실제 연결 순서를 알 수 없다. 좌표 기반 MST를
    쓰면 지리적으로 가장 가까운 역끼리 이어지므로, 순환선과 지선을 별도
    분기 규칙 없이도 합리적으로 근사할 수 있다.
    """

    n = len(lats)

    in_tree = np.zeros(n, dtype=bool)
    min_dist = np.full(n, np.inf)
    parent = np.full(n, -1, dtype=int)

    in_tree[0] = True

    for j in range(1, n):
        min_dist[j] = _haversine(lats[0], lons[0], lats[j], lons[j])
        parent[j] = 0

    edges = []

    for _ in range(n - 1):

        candidates = np.where(~in_tree)[0]
        u = candidates[np.argmin(min_dist[candidates])]

        in_tree[u] = True
        edges.append((int(parent[u]), int(u)))

        for v in np.where(~in_tree)[0]:

            d = _haversine(lats[u], lons[u], lats[v], lons[v])

            if d < min_dist[v]:
                min_dist[v] = d
                parent[v] = u

    return edges


@st.cache_data(show_spinner=False)
def _load_subway_network(path_str):
    """
    역사마스터 CSV를 읽어 노선별 연결선(간선) 좌표 목록을 계산한다.

    같은 물리적 선로의 연장 구간(예: '9호선(연장)', '신분당선(연장2)',
    '7호선(인천)')은 기본 노선명으로 합쳐 하나의 선으로 이어서 그린다.
    """

    path = Path(path_str)

    if not path.exists():
        return pd.DataFrame(
            columns=["lon1", "lat1", "lon2", "lat2", "line_group", "color"]
        )

    df = pd.read_csv(path, encoding="utf-8-sig")

    df = df.rename(
        columns={
            "역명": "station",
            "호선": "line_raw",
            "경도": "lon",
            "위도": "lat",
        }
    )

    df = df.dropna(subset=["lat", "lon", "line_raw"])

    df["line_group"] = (
        df["line_raw"]
        .str.replace(r"\(연장\d*\)", "", regex=True)
        .str.replace(r"\(인천\)", "", regex=True)
        .str.strip()
    )

    line_groups = sorted(df["line_group"].unique())
    color_map = _build_color_palette(line_groups)

    edge_rows = []

    for line_group in line_groups:

        sub = df[df["line_group"] == line_group].reset_index(drop=True)

        if len(sub) < 2:
            continue

        edges = _minimum_spanning_tree_edges(
            sub["lat"].to_numpy(),
            sub["lon"].to_numpy(),
        )

        color = color_map[line_group]

        for i, j in edges:

            edge_rows.append(
                {
                    "lon1": sub.loc[i, "lon"],
                    "lat1": sub.loc[i, "lat"],
                    "lon2": sub.loc[j, "lon"],
                    "lat2": sub.loc[j, "lat"],
                    "line_group": line_group,
                    "color": color,
                }
            )

    return pd.DataFrame(edge_rows)


def _get_subway_line_layer():

    edges_df = _load_subway_network(str(SUBWAY_STATIONS_PATH))

    if edges_df.empty:
        return None

    return pdk.Layer(
        "LineLayer",
        data=edges_df,
        get_source_position="[lon1, lat1]",
        get_target_position="[lon2, lat2]",
        get_color="color",
        get_width=2,
        width_min_pixels=1.3,
        pickable=False,
    )


def render_map(
    df,
    f,
    view_type,
    selected_place,
):

    st.markdown("#### 🗺️ 거래 위치 지도")

    try:

        with open(GEOJSON_PATH, "r", encoding="utf-8") as geojson_file:
            seoul_geojson = json.load(geojson_file)

    except FileNotFoundError:

        st.error("seoul_gu.geojson 파일을 찾을 수 없습니다.")
        return

    subway_layer = _get_subway_line_layer()

    if subway_layer is None:
        st.caption(
            "ℹ️ 지하철 노선도를 표시하려면 assets/subway_stations.csv "
            "파일이 필요합니다."
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
        .dropna(subset=["위도", "경도"])
        .copy()
    )

    if len(map_df) > 15000:
        map_df = map_df.sample(15000, random_state=42)

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

            properties = feature.get("properties", {})

            geo_name = (
                properties.get("SIG_KOR_NM")
                or properties.get("name")
                or properties.get("자치구명")
            )

            if geo_name == selected_place:
                selected_features.append(feature)

        selected_boundary = {
            "type": "FeatureCollection",
            "features": selected_features,
        }

        map_df = map_df[map_df["자치구명"] == selected_place].copy()

        if len(map_df) > 0:
            center_lat = map_df["위도"].mean()
            center_lon = map_df["경도"].mean()
        else:
            center_lat = 37.5172
            center_lon = 127.0473

        boundary_layer = pdk.Layer(
            "GeoJsonLayer",
            data=selected_boundary,
            get_fill_color=[70, 130, 180, 70],
            get_line_color=[30, 80, 130, 220],
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
            get_fill_color=[220, 70, 70, 180],
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

        layers = [
            layer
            for layer in [subway_layer, boundary_layer, point_layer]
            if layer is not None
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
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

        st.caption(f"🚇 {selected_place}의 역세권 거래 위치를 표시합니다.")

        map_df = map_df[
            map_df["최근접역_호선"].str.contains(selected_place, na=False)
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
            get_fill_color=[50, 120, 200, 180],
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

        layers = [
            layer for layer in [subway_layer, point_layer] if layer is not None
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
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

        st.caption(f"📍 {selected_place} 주변 거래 위치를 표시합니다.")

        map_df = map_df[map_df["최근접역"] == selected_place].copy()

        if len(map_df) > 0:
            center_lat = map_df["위도"].mean()
            center_lon = map_df["경도"].mean()
        else:

            station_info = df[df["최근접역"] == selected_place][
                ["최근접역_위도", "최근접역_경도"]
            ].dropna()

            if len(station_info) > 0:
                center_lat = station_info["최근접역_위도"].iloc[0]
                center_lon = station_info["최근접역_경도"].iloc[0]
            else:
                center_lat = 37.5665
                center_lon = 126.9780

        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[경도, 위도]",
            get_radius=30,
            get_fill_color=[220, 70, 70, 180],
            pickable=True,
            auto_highlight=True,
        )

        station_info = (
            df[df["최근접역"] == selected_place][
                ["최근접역_위도", "최근접역_경도"]
            ]
            .dropna()
            .drop_duplicates()
        )

        station_layer = pdk.Layer(
            "ScatterplotLayer",
            data=station_info,
            get_position="[최근접역_경도, 최근접역_위도]",
            get_radius=100,
            get_fill_color=[30, 80, 200, 255],
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

        layers = [
            layer
            for layer in [subway_layer, point_layer, station_layer]
            if layer is not None
        ]

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip,
                map_provider="carto",
                map_style="light",
            ),
            use_container_width=True,
        )

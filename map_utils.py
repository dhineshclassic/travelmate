"""
TravelMate - Map Utilities
Folium map creation, route drawing, markers, and tile management.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import folium
from folium import plugins
from streamlit_folium import st_folium

from config import (
    DEFAULT_LOCATION,
    DEFAULT_MAP_STYLE,
    DEFAULT_ZOOM,
    MAP_TILES,
    ROUTE_TYPES,
)
from route_engine import MultiRouteResponse, RouteResult


def create_base_map(
    center: Tuple[float, float] = DEFAULT_LOCATION,
    zoom: int = DEFAULT_ZOOM,
    map_style: str = DEFAULT_MAP_STYLE,
) -> folium.Map:
    """Create a clean Folium map with the selected tile layer and useful plugins."""
    tile_cfg = MAP_TILES.get(map_style, MAP_TILES["OpenStreetMap"])

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )

    folium.TileLayer(
        tiles=tile_cfg["tiles"],
        attr=tile_cfg["attr"],
        name=tile_cfg["name"],
        overlay=False,
        control=True,
    ).add_to(m)

    for name, cfg in MAP_TILES.items():
        if name == map_style:
            continue
        folium.TileLayer(
            tiles=cfg["tiles"],
            attr=cfg["attr"],
            name=cfg["name"],
            overlay=False,
            control=True,
        ).add_to(m)

    plugins.Fullscreen(
        position="topright",
        title="Fullscreen",
        title_cancel="Exit Fullscreen",
        force_separate_button=True,
    ).add_to(m)

    plugins.LocateControl(auto_start=False).add_to(m)
    plugins.MousePosition().add_to(m)
    plugins.MeasureControl(position="bottomleft", primary_length_unit="kilometers").add_to(m)

    folium.LayerControl(position="topright", collapsed=True).add_to(m)

    return m


def add_route_to_map(
    m: folium.Map,
    route: RouteResult,
    highlighted: bool = False,
) -> None:
    """Draw a single route polyline on the map."""
    if not route.coordinates or len(route.coordinates) < 2:
        return

    weight = ROUTE_TYPES[route.route_type]["weight"]
    opacity = ROUTE_TYPES[route.route_type]["opacity"]

    if highlighted:
        weight += 3
        opacity = min(opacity + 0.15, 1.0)

    folium.PolyLine(
        locations=route.coordinates,
        color=route.color,
        weight=weight,
        opacity=opacity,
        tooltip=f"{route.label} • {route.distance_km:.2f} km • {int(route.duration_min)} min",
        popup=folium.Popup(
            f"""
            <div style="font-family: system-ui; min-width: 180px;">
                <strong style="color:{route.color};">{route.label} Route</strong><br>
                Distance: {route.distance_km:.2f} km<br>
                Time: {int(route.duration_min)} min<br>
                Speed: {route.average_speed_kmh:.0f} km/h<br>
                Turns: {route.num_turns}<br>
                Difficulty: {route.difficulty}
            </div>
            """,
            max_width=260,
        ),
    ).add_to(m)


def add_markers(
    m: folium.Map,
    start: Optional[Tuple[float, float]],
    end: Optional[Tuple[float, float]],
    start_name: str = "Start",
    end_name: str = "Destination",
) -> None:
    """Add elegant start and end markers."""
    if start:
        folium.Marker(
            location=start,
            tooltip=f"Start: {start_name}",
            popup=folium.Popup(f"<b>Start</b><br>{start_name}", max_width=250),
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(m)

    if end:
        folium.Marker(
            location=end,
            tooltip=f"Destination: {end_name}",
            popup=folium.Popup(f"<b>Destination</b><br>{end_name}", max_width=250),
            icon=folium.Icon(color="red", icon="flag", prefix="fa"),
        ).add_to(m)


def fit_map_to_routes(
    m: folium.Map,
    routes: Dict[str, RouteResult],
    start: Optional[Tuple[float, float]] = None,
    end: Optional[Tuple[float, float]] = None,
    padding: int = 40,
) -> None:
    """Automatically zoom and pan the map so that all routes + markers are visible."""
    points: List[Tuple[float, float]] = []
    if start:
        points.append(start)
    if end:
        points.append(end)
    for route in routes.values():
        points.extend(route.coordinates)

    if len(points) >= 2:
        m.fit_bounds(points, padding=(padding, padding))
    elif len(points) == 1:
        m.location = points[0]
        m.zoom_start = 14


def build_route_map(
    response: MultiRouteResponse,
    selected_route: str = "fastest",
    map_style: str = DEFAULT_MAP_STYLE,
    zoom: int = DEFAULT_ZOOM,
) -> folium.Map:
    """High-level helper: create a complete map with all routes, markers, and correct view."""
    if response.start_coord and response.end_coord:
        center = (
            (response.start_coord[0] + response.end_coord[0]) / 2,
            (response.start_coord[1] + response.end_coord[1]) / 2,
        )
    elif response.start_coord:
        center = response.start_coord
    else:
        center = DEFAULT_LOCATION

    m = create_base_map(center=center, zoom=zoom, map_style=map_style)

    for key, route in response.routes.items():
        if key != selected_route:
            add_route_to_map(m, route, highlighted=False)

    if selected_route in response.routes:
        add_route_to_map(m, response.routes[selected_route], highlighted=True)

    add_markers(
        m,
        start=response.start_coord,
        end=response.end_coord,
        start_name=response.start_name or "Start",
        end_name=response.end_name or "Destination",
    )

    fit_map_to_routes(
        m,
        routes=response.routes,
        start=response.start_coord,
        end=response.end_coord,
    )

    return m


def render_map(
    m: folium.Map,
    height: int = 620,
    key: str = "travelmate_map",
) -> Dict:
    """Render the Folium map inside Streamlit and return the interaction data."""
    return st_folium(
        m,
        height=height,
        width=None,
        returned_objects=["last_object_clicked", "bounds", "zoom"],
        key=key,
    )

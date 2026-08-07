"""
TravelMate - Route Engine
Reliable multi-route calculation using OSRM public API.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st

from config import CACHE_TTL_SECONDS, ROUTE_TYPES, TRANSPORT_MODES
from utils import (
    count_turns,
    estimate_calories,
    estimate_travel_time_minutes,
    format_distance,
    format_duration,
    haversine_km,
    infer_difficulty,
    infer_road_type,
)

warnings.filterwarnings("ignore")

OSRM_BASE = "https://router.project-osrm.org"


@dataclass
class RouteResult:
    route_type: str
    label: str
    color: str
    coordinates: List[Tuple[float, float]]
    distance_km: float
    duration_min: float
    average_speed_kmh: float
    num_turns: int
    road_type: str
    difficulty: str
    calories: int
    geometry_length_m: float = 0.0
    success: bool = True
    message: str = ""

    def to_dict(self) -> Dict:
        return {
            "route_type": self.route_type,
            "label": self.label,
            "color": self.color,
            "coordinates": self.coordinates,
            "distance_km": self.distance_km,
            "duration_min": self.duration_min,
            "average_speed_kmh": self.average_speed_kmh,
            "num_turns": self.num_turns,
            "road_type": self.road_type,
            "difficulty": self.difficulty,
            "calories": self.calories,
            "formatted_distance": format_distance(self.distance_km),
            "formatted_duration": format_duration(self.duration_min),
        }


@dataclass
class MultiRouteResponse:
    success: bool
    message: str
    start_coord: Optional[Tuple[float, float]] = None
    end_coord: Optional[Tuple[float, float]] = None
    start_name: str = ""
    end_name: str = ""
    mode: str = "Car"
    routes: Dict[str, RouteResult] = field(default_factory=dict)


def _osrm_profile(mode: str) -> str:
    """Map transport modes to OSRM profiles."""
    mapping = {
        "Walking": "foot",
        "Motorcycle": "driving",
        "Car": "driving",
        "Bus": "driving",
    }
    return mapping.get(mode, "driving")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Calculating routes…")
def _fetch_osrm_route(
    start_lon: float,
    start_lat: float,
    end_lon: float,
    end_lat: float,
    profile: str = "driving",
    alternatives: bool = True,
) -> Optional[dict]:
    """Call OSRM public API."""
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = (
        f"{OSRM_BASE}/route/v1/{profile}/{coords}"
        f"?overview=full&geometries=geojson&steps=true&alternatives={str(alternatives).lower()}"
    )
    try:
        resp = requests.get(url, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                return data
    except Exception:
        pass
    return None


def _geojson_to_latlon(geometry: dict) -> List[Tuple[float, float]]:
    coords = geometry.get("coordinates", [])
    return [(lat, lon) for lon, lat in coords]


def _build_route_from_osrm(osrm_route: dict, route_type: str, mode: str) -> RouteResult:
    """Convert one OSRM route into RouteResult with mode-specific timing."""
    coords = _geojson_to_latlon(osrm_route.get("geometry", {}))
    distance_m = osrm_route.get("distance", 0)
    duration_s = osrm_route.get("duration", 0)

    distance_km = distance_m / 1000.0

    # Mode-specific duration handling
    if mode == "Walking":
        # Always use our walking speed (5 km/h) – never trust driving profile for walk
        duration_min = estimate_travel_time_minutes(distance_km, "Walking")
    elif mode == "Motorcycle":
        # OSRM driving duration is a good base; scale slightly faster than car
        duration_min = (duration_s / 60.0) * 0.85
        if duration_min < 0.5:
            duration_min = estimate_travel_time_minutes(distance_km, "Motorcycle")
    elif mode == "Bus":
        # Buses are slower (stops, traffic)
        duration_min = (duration_s / 60.0) * 1.40
        if duration_min < 0.5:
            duration_min = estimate_travel_time_minutes(distance_km, "Bus")
    else:  # Car
        duration_min = duration_s / 60.0
        if duration_min < 0.5:
            duration_min = estimate_travel_time_minutes(distance_km, "Car")

    avg_speed = distance_km / (duration_min / 60.0) if duration_min > 0 else 0.0
    turns = count_turns(coords)
    road = infer_road_type(distance_km, turns)
    diff = infer_difficulty(mode, distance_km, turns)
    cals = estimate_calories(distance_km, mode)

    meta = ROUTE_TYPES.get(route_type, ROUTE_TYPES["fastest"])

    return RouteResult(
        route_type=route_type,
        label=meta["label"],
        color=meta["color"],
        coordinates=coords,
        distance_km=round(distance_km, 3),
        duration_min=round(duration_min, 1),
        average_speed_kmh=round(avg_speed, 1),
        num_turns=turns,
        road_type=road,
        difficulty=diff,
        calories=cals,
        geometry_length_m=distance_m,
    )


def calculate_routes(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    mode: str = "Car",
    start_name: str = "",
    end_name: str = "",
) -> MultiRouteResponse:
    """
    Calculate routes using OSRM.
    Returns only real alternatives – never duplicates the same geometry.
    """
    mode = mode if mode in TRANSPORT_MODES else "Car"
    profile = _osrm_profile(mode)

    straight_km = haversine_km(start_lat, start_lon, end_lat, end_lon)
    if straight_km > 3000:
        return MultiRouteResponse(
            success=False,
            message="too_far",
            start_coord=(start_lat, start_lon),
            end_coord=(end_lat, end_lon),
            start_name=start_name,
            end_name=end_name,
            mode=mode,
        )

    data = _fetch_osrm_route(
        start_lon, start_lat, end_lon, end_lat,
        profile=profile,
        alternatives=True,
    )

    if not data or not data.get("routes"):
        return MultiRouteResponse(
            success=False,
            message="no_route",
            start_coord=(start_lat, start_lon),
            end_coord=(end_lat, end_lon),
            start_name=start_name,
            end_name=end_name,
            mode=mode,
        )

    osrm_routes = data["routes"]
    routes: Dict[str, RouteResult] = {}

    # Always take the first as fastest
    routes["fastest"] = _build_route_from_osrm(osrm_routes[0], "fastest", mode)

    # Only add truly different alternatives
    if len(osrm_routes) >= 2:
        # Sort by distance for shortest
        by_distance = sorted(osrm_routes, key=lambda r: r.get("distance", 0))
        shortest_candidate = by_distance[0]

        # Check if shortest is meaningfully different from fastest
        if abs(shortest_candidate.get("distance", 0) - osrm_routes[0].get("distance", 0)) > 50:
            routes["shortest"] = _build_route_from_osrm(shortest_candidate, "shortest", mode)
        else:
            # Use second route if available and different
            if len(osrm_routes) >= 2:
                routes["shortest"] = _build_route_from_osrm(osrm_routes[1], "shortest", mode)

        # Alternate = third distinct route if available
        used_distances = {r.get("distance", 0) for r in osrm_routes[:2]}
        for r in osrm_routes[2:]:
            if r.get("distance", 0) not in used_distances:
                routes["alternate"] = _build_route_from_osrm(r, "alternate", mode)
                break
        if "alternate" not in routes and len(osrm_routes) >= 3:
            routes["alternate"] = _build_route_from_osrm(osrm_routes[2], "alternate", mode)

    # If we only got one real route, do NOT invent duplicates
    # Just return the single route under "fastest"
    if len(routes) == 1 and "shortest" not in routes:
        # Optionally still show shortest as the same only when truly no alternative
        pass

    return MultiRouteResponse(
        success=True,
        message="ok",
        start_coord=(start_lat, start_lon),
        end_coord=(end_lat, end_lon),
        start_name=start_name,
        end_name=end_name,
        mode=mode,
        routes=routes,
    )

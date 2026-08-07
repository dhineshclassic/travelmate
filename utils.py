"""
TravelMate - Utility Functions
Correct worldwide geocoding, formatting, calculations, and validation.
"""

from __future__ import annotations

import math
import re
from typing import List, Optional, Tuple

import streamlit as st
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from config import CACHE_TTL_SECONDS, ERROR_MESSAGES, TRANSPORT_MODES


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def geocode_location(query: str, user_agent: str = "TravelMate/2.1") -> Optional[Tuple[float, float, str]]:
    """
    Correct worldwide geocoding.
    Tries the exact query first, then sensible expansions.
    Never forces an Indian city context on non-Indian queries.
    """
    if not query or not query.strip():
        return None

    cleaned = query.strip()
    geolocator = Nominatim(user_agent=user_agent, timeout=15)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)

    candidates = _build_query_candidates(cleaned)

    for q in candidates:
        try:
            location = geocode(
                q,
                exactly_one=True,
                addressdetails=True,
                language="en",
            )
            if location is not None:
                # Basic sanity: reject results that are extremely far from expected
                # when the user typed a well-known city name
                return (location.latitude, location.longitude, location.address)
        except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable, Exception):
            continue

    return None


def _build_query_candidates(query: str) -> List[str]:
    """
    Build search candidates carefully.
    - Exact query always first
    - Only add country/city context when it makes sense
    - Do NOT force "Bangalore, India" on every short name
    """
    q = query.strip()
    q_lower = q.lower().replace(" ", "")

    candidates = [q]

    # Normalize common misspellings / compact forms
    aliases = {
        # USA / International
        "newyork": "New York, USA",
        "newyorkcity": "New York, USA",
        "nyc": "New York, USA",
        "manhattan": "Manhattan, New York, USA",
        "losangeles": "Los Angeles, California, USA",
        "sanfrancisco": "San Francisco, California, USA",
        "london": "London, United Kingdom",
        "paris": "Paris, France",
        "tokyo": "Tokyo, Japan",
        "dubai": "Dubai, UAE",
        "singapore": "Singapore",
        "sydney": "Sydney, Australia",
        # Major Indian cities
        "chennai": "Chennai, Tamil Nadu, India",
        "madras": "Chennai, Tamil Nadu, India",
        "coimbatore": "Coimbatore, Tamil Nadu, India",
        "kovai": "Coimbatore, Tamil Nadu, India",
        "bangalore": "Bangalore, Karnataka, India",
        "bengaluru": "Bengaluru, Karnataka, India",
        "mysore": "Mysore, Karnataka, India",
        "mysuru": "Mysuru, Karnataka, India",
        "mumbai": "Mumbai, Maharashtra, India",
        "bombay": "Mumbai, Maharashtra, India",
        "pune": "Pune, Maharashtra, India",
        "delhi": "New Delhi, India",
        "newdelhi": "New Delhi, India",
        "jaipur": "Jaipur, Rajasthan, India",
        "hyderabad": "Hyderabad, Telangana, India",
        "vijayawada": "Vijayawada, Andhra Pradesh, India",
        "madurai": "Madurai, Tamil Nadu, India",
        "trichy": "Tiruchirappalli, Tamil Nadu, India",
        "tiruchirappalli": "Tiruchirappalli, Tamil Nadu, India",
        "kochi": "Kochi, Kerala, India",
        "cochin": "Kochi, Kerala, India",
        "trivandrum": "Thiruvananthapuram, Kerala, India",
        "thiruvananthapuram": "Thiruvananthapuram, Kerala, India",
        "kolkata": "Kolkata, West Bengal, India",
        "calcutta": "Kolkata, West Bengal, India",
        "ahmedabad": "Ahmedabad, Gujarat, India",
        "chandigarh": "Chandigarh, India",
        # Bangalore areas
        "madiwala": "Madiwala, Bangalore, India",
        "btmlayout": "BTM Layout, Bangalore, India",
        "koramangala": "Koramangala, Bangalore, India",
        "indiranagar": "Indiranagar, Bangalore, India",
        "whitefield": "Whitefield, Bangalore, India",
        "electroniccity": "Electronic City, Bangalore, India",
        "jayanagar": "Jayanagar, Bangalore, India",
        "malleshwaram": "Malleshwaram, Bangalore, India",
    }

    if q_lower in aliases:
        candidates.insert(0, aliases[q_lower])
        candidates.append(aliases[q_lower])

    # If user already wrote a comma or country-like word, keep it simple
    if "," in q or any(w in q.lower() for w in ["usa", "india", "uk", "uae", "japan", "france", "australia"]):
        return _unique(candidates)

    # Generic expansions (order matters – most specific first)
    expansions = [
        f"{q}, India",
        f"{q}, USA",
        f"{q}, United States",
        f"{q}, United Kingdom",
        f"{q}, city",
    ]

    # Only for very short local-sounding names, try Bangalore context
    if len(q.split()) <= 2 and q_lower not in aliases:
        # Local Indian area names are common for this app
        expansions = [
            f"{q}, Bangalore, India",
            f"{q}, Bengaluru, India",
            f"{q}, Tamil Nadu, India",
            f"{q}, India",
            f"{q}, USA",
        ] + expansions

    candidates.extend(expansions)
    return _unique(candidates)[:7]


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        key = x.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(x)
    return out


def reverse_geocode(lat: float, lon: float, user_agent: str = "TravelMate/2.1") -> str:
    geolocator = Nominatim(user_agent=user_agent, timeout=10)
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True, language="en")
        return location.address if location else f"{lat:.5f}, {lon:.5f}"
    except Exception:
        return f"{lat:.5f}, {lon:.5f}"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def format_distance(km: float) -> str:
    if km < 1.0:
        return f"{int(km * 1000)} m"
    if km < 10:
        return f"{km:.2f} km"
    return f"{km:.1f} km"


def format_duration(minutes: float) -> str:
    if minutes < 1:
        return "< 1 min"
    total = int(round(minutes))
    hours, mins = divmod(total, 60)
    if hours == 0:
        return f"{mins} min"
    if mins == 0:
        return f"{hours} h"
    return f"{hours} h {mins} min"


def estimate_travel_time_minutes(distance_km: float, mode: str) -> float:
    speed = TRANSPORT_MODES.get(mode, TRANSPORT_MODES["Car"])["speed_kmh"]
    if speed <= 0:
        return 0.0
    return (distance_km / speed) * 60.0


def estimate_calories(distance_km: float, mode: str) -> int:
    cal_per_km = TRANSPORT_MODES.get(mode, {}).get("calories_per_km", 0.0)
    return int(round(distance_km * cal_per_km))


def count_turns(coordinates: List[Tuple[float, float]], angle_threshold: float = 35.0) -> int:
    if len(coordinates) < 3:
        return 0
    turns = 0
    for i in range(1, len(coordinates) - 1):
        lat1, lon1 = coordinates[i - 1]
        lat2, lon2 = coordinates[i]
        lat3, lon3 = coordinates[i + 1]
        b1 = _bearing(lat1, lon1, lat2, lon2)
        b2 = _bearing(lat2, lon2, lat3, lon3)
        diff = abs(b2 - b1)
        if diff > 180:
            diff = 360 - diff
        if diff > angle_threshold:
            turns += 1
    return turns


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def infer_road_type(distance_km: float, num_turns: int) -> str:
    if distance_km < 2 and num_turns > 8:
        return "Urban / Local streets"
    if distance_km < 8:
        return "City roads"
    if num_turns < 4:
        return "Highway / Major road"
    return "Mixed roads"


def infer_difficulty(mode: str, distance_km: float, num_turns: int) -> str:
    if mode == "Walking":
        if distance_km > 8 or num_turns > 15:
            return "Hard"
        if distance_km > 4:
            return "Moderate"
        return "Easy"
    if mode == "Motorcycle":
        if distance_km > 40:
            return "Long trip"
        return "Easy"
    if distance_km > 50:
        return "Long trip"
    return "Easy"


def sanitize_location_input(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r"[^\w\s,.\-/#&'()]", "", cleaned)
    return cleaned[:200]


def validate_inputs(start: str, end: str) -> Optional[str]:
    if not start or not start.strip():
        return "empty_start"
    if not end or not end.strip():
        return "empty_end"
    return None


def get_friendly_error(key: str) -> str:
    return ERROR_MESSAGES.get(key, "An unexpected error occurred. Please try again.")

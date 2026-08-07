"""
TravelMate - Configuration Module
Centralized settings, constants, colors, and map tile definitions.
"""

from typing import Dict, Tuple

APP_NAME: str = "TravelMate"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = "Professional desktop routing & navigation experience"
APP_ICON: str = "🗺️"

COLORS: Dict[str, str] = {
    "primary": "#1A73E8",
    "primary_dark": "#0D47A1",
    "primary_light": "#E8F0FE",
    "accent": "#00BFA5",
    "accent_dark": "#00897B",
    "route_fastest": "#1A73E8",
    "route_shortest": "#34A853",
    "route_alternate": "#FB8C00",
    "route_highlight": "#EA4335",
    "background_light": "#F8F9FA",
    "background_dark": "#121212",
    "card_light": "#FFFFFF",
    "card_dark": "#1E1E1E",
    "sidebar_light": "#FFFFFF",
    "sidebar_dark": "#1A1A1A",
    "text_primary_light": "#202124",
    "text_primary_dark": "#E8EAED",
    "text_secondary_light": "#5F6368",
    "text_secondary_dark": "#9AA0A6",
    "border_light": "#E0E0E0",
    "border_dark": "#333333",
    "success": "#34A853",
    "warning": "#FBBC04",
    "error": "#EA4335",
    "info": "#1A73E8",
}

# Updated transport modes (no Train, added Motorcycle, removed fuel)
TRANSPORT_MODES: Dict[str, Dict] = {
    "Walking": {
        "speed_kmh": 5.0,
        "icon": "🚶",
        "color": "#34A853",
        "calories_per_km": 55.0,
    },
    "Motorcycle": {
        "speed_kmh": 35.0,
        "icon": "🏍️",
        "color": "#FB8C00",
        "calories_per_km": 0.0,
    },
    "Car": {
        "speed_kmh": 45.0,
        "icon": "🚗",
        "color": "#1A73E8",
        "calories_per_km": 0.0,
    },
    "Bus": {
        "speed_kmh": 28.0,
        "icon": "🚌",
        "color": "#7B1FA2",
        "calories_per_km": 0.0,
    },
}

DEFAULT_TRANSPORT_MODE: str = "Car"

ROUTE_TYPES: Dict[str, Dict] = {
    "fastest": {
        "label": "Fastest",
        "color": COLORS["route_fastest"],
        "weight": 6,
        "opacity": 0.85,
    },
    "shortest": {
        "label": "Shortest",
        "color": COLORS["route_shortest"],
        "weight": 5,
        "opacity": 0.80,
    },
    "alternate": {
        "label": "Alternate",
        "color": COLORS["route_alternate"],
        "weight": 4,
        "opacity": 0.75,
    },
}

MAP_TILES: Dict[str, Dict] = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors",
        "name": "OpenStreetMap",
    },
    "Satellite": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles © Esri",
        "name": "Satellite",
    },
    "Terrain": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles © Esri",
        "name": "Terrain",
    },
    "Dark": {
        "tiles": "CartoDB dark_matter",
        "attr": "© CartoDB",
        "name": "Dark Mode",
    },
    "Light": {
        "tiles": "CartoDB positron",
        "attr": "© CartoDB",
        "name": "Light Mode",
    },
}

DEFAULT_MAP_STYLE: str = "OpenStreetMap"
DEFAULT_ZOOM: int = 13
DEFAULT_LOCATION: Tuple[float, float] = (12.9716, 77.5946)  # Bangalore

CACHE_TTL_SECONDS: int = 3600

ERROR_MESSAGES: Dict[str, str] = {
    "empty_start": "Please enter a starting location.",
    "empty_end": "Please enter a destination.",
    "invalid_location": "Could not find that location. Try a more specific name, landmark, or postal code.",
    "no_route": "No route could be calculated between these points. Try different locations or transport mode.",
    "network_error": "Network issue while fetching map data. Please check your connection and try again.",
    "too_far": "These locations are too far apart for the free routing service (max ~3000 km). Try locations on the same continent.",
    "geocoding_failed": "Unable to locate one or both addresses. Please check spelling.",
}

ABOUT_TEXT: str = """
**TravelMate** is a professional desktop routing application built with Python & Streamlit.

It provides multi-route planning (Fastest / Shortest / Alternate), realistic travel-time estimates, and a clean modern interface.

**Features**
- Multi-modal routing (Walk, Motorcycle, Car, Bus)
- Three simultaneous route alternatives with distinct colors
- Detailed statistics: distance, ETA, calories, turns, difficulty
- Multiple map styles (OSM, Satellite, Terrain, Dark, Light)

Built for desktop / laptop users.
"""

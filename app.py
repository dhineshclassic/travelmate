"""
TravelMate – Main Application
"""

from __future__ import annotations

import streamlit as st

from config import APP_NAME, APP_ICON, DEFAULT_MAP_STYLE, DEFAULT_LOCATION, DEFAULT_ZOOM
from map_utils import build_route_map, render_map, create_base_map
from route_engine import calculate_routes, MultiRouteResponse
from ui import (
    inject_custom_css,
    render_top_nav,
    render_sidebar,
    render_route_selector,
    render_metrics,
    render_about_modal,
    render_empty_state,
    render_error,
)
from utils import (
    geocode_location,
    sanitize_location_input,
    validate_inputs,
    get_friendly_error,
    haversine_km,
)


st.set_page_config(
    page_title=f"{APP_NAME} – Smart Routing",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "TravelMate – Professional multi-route navigation."},
)


def init_session_state() -> None:
    defaults = {
        "dark_mode": False,
        "show_about": False,
        "route_response": None,
        "selected_route": "fastest",
        "last_start": "",
        "last_end": "",
        "last_mode": "Car",
        "debug_info": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    init_session_state()

    inject_custom_css(dark_mode=st.session_state.dark_mode)
    render_top_nav(dark_mode=st.session_state.dark_mode)
    render_about_modal()

    sidebar = render_sidebar()
    map_style = sidebar["map_style"]

    if sidebar["clear"]:
        st.session_state.route_response = None
        st.session_state.selected_route = "fastest"
        st.session_state.debug_info = None
        st.rerun()

    if sidebar["generate"]:
        start_raw = sanitize_location_input(sidebar["start"])
        end_raw = sanitize_location_input(sidebar["end"])
        mode = sidebar["mode"]

        error_key = validate_inputs(start_raw, end_raw)
        if error_key:
            st.session_state.route_response = MultiRouteResponse(success=False, message=error_key)
            st.session_state.debug_info = None
        else:
            with st.spinner("Resolving locations & calculating routes…"):
                start_geo = geocode_location(start_raw)
                end_geo = geocode_location(end_raw)

                # Debug info always stored
                debug = {
                    "start_input": start_raw,
                    "end_input": end_raw,
                    "start_resolved": start_geo[2] if start_geo else None,
                    "end_resolved": end_geo[2] if end_geo else None,
                    "start_coords": (start_geo[0], start_geo[1]) if start_geo else None,
                    "end_coords": (end_geo[0], end_geo[1]) if end_geo else None,
                    "mode": mode,
                }
                st.session_state.debug_info = debug

                if start_geo is None or end_geo is None:
                    st.session_state.route_response = MultiRouteResponse(
                        success=False,
                        message="invalid_location",
                    )
                else:
                    start_lat, start_lon, start_name = start_geo
                    end_lat, end_lon, end_name = end_geo

                    # Safety: reject absurdly long routes for free OSRM demo
                    dist = haversine_km(start_lat, start_lon, end_lat, end_lon)
                    if dist > 3000:
                        st.session_state.route_response = MultiRouteResponse(
                            success=False,
                            message="too_far",
                            start_coord=(start_lat, start_lon),
                            end_coord=(end_lat, end_lon),
                            start_name=start_name,
                            end_name=end_name,
                            mode=mode,
                        )
                    else:
                        response = calculate_routes(
                            start_lat=start_lat,
                            start_lon=start_lon,
                            end_lat=end_lat,
                            end_lon=end_lon,
                            mode=mode,
                            start_name=start_name,
                            end_name=end_name,
                        )
                        st.session_state.route_response = response
                        st.session_state.selected_route = "fastest"
                        st.session_state.last_start = start_raw
                        st.session_state.last_end = end_raw
                        st.session_state.last_mode = mode

        st.rerun()

    # Show resolved locations (debug / transparency)
    if st.session_state.debug_info:
        d = st.session_state.debug_info
        with st.expander("📍 Resolved Locations", expanded=False):
            if d["start_resolved"]:
                st.markdown(f"**Start:** {d['start_resolved']}")
                st.caption(f"Coordinates: {d['start_coords'][0]:.5f}, {d['start_coords'][1]:.5f}")
            else:
                st.error(f"Start not found: “{d['start_input']}”")
            if d["end_resolved"]:
                st.markdown(f"**Destination:** {d['end_resolved']}")
                st.caption(f"Coordinates: {d['end_coords'][0]:.5f}, {d['end_coords'][1]:.5f}")
            else:
                st.error(f"Destination not found: “{d['end_input']}”")

    response: MultiRouteResponse | None = st.session_state.route_response

    if response is None:
        render_empty_state()
        m = create_base_map(center=DEFAULT_LOCATION, zoom=DEFAULT_ZOOM, map_style=map_style)
        render_map(m, height=580, key="empty_map")
        return

    if not response.success:
        render_error(get_friendly_error(response.message))
        m = create_base_map(center=DEFAULT_LOCATION, zoom=DEFAULT_ZOOM, map_style=map_style)
        render_map(m, height=520, key="error_map")
        return

    # Successful response
    new_selected = render_route_selector(response, st.session_state.selected_route)
    if new_selected != st.session_state.selected_route:
        st.session_state.selected_route = new_selected
        st.rerun()

    selected_key = st.session_state.selected_route
    selected_route = response.routes.get(selected_key)

    m = build_route_map(
        response=response,
        selected_route=selected_key,
        map_style=map_style,
    )
    render_map(m, height=600, key="main_route_map")

    if selected_route:
        render_metrics(selected_route, response.mode)

    st.caption(
        f"Start: {response.start_name}  →  End: {response.end_name}  |  "
        f"Mode: {response.mode}  |  "
        f"Routes: {len(response.routes)}"
    )


if __name__ == "__main__":
    main()

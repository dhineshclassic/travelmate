"""
TravelMate - UI Components
Light Mode fully readable; Dark Mode preserved.
"""

from __future__ import annotations

from typing import Dict

import streamlit as st

from config import ABOUT_TEXT, TRANSPORT_MODES
from route_engine import MultiRouteResponse, RouteResult
from utils import format_distance, format_duration


def inject_custom_css(dark_mode: bool = False) -> None:
    """Theme CSS. Light Mode uses dark text; Dark Mode unchanged."""
    if dark_mode:
        bg = "#0F0F0F"
        card = "#1A1A1A"
        card_hover = "#222222"
        text = "#F0F0F0"
        text_sec = "#A0A0A0"
        border = "#2A2A2A"
        sidebar_bg = "#141414"
        input_bg = "#1F1F1F"
        primary = "#4C8BF5"
        danger = "#EA4335"
        radio_bg = "#1F1F1F"
        select_bg = "#1F1F1F"
    else:
        # Light Mode – everything must be readable
        bg = "#F5F7FA"
        card = "#FFFFFF"
        card_hover = "#FAFBFC"
        text = "#1A1A1A"
        text_sec = "#5F6368"
        border = "#DADCE0"
        sidebar_bg = "#FFFFFF"
        input_bg = "#FFFFFF"
        primary = "#1A73E8"
        danger = "#EA4335"
        radio_bg = "#FFFFFF"
        select_bg = "#FFFFFF"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {text} !important;
    }}

    .stApp {{
        background-color: {bg};
        color: {text} !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    /* ===== SIDEBAR TOGGLE ALWAYS VISIBLE ===== */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"],
    [data-testid="baseButton-headerNoPadding"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border};
        padding: 1.25rem 1rem;
    }}
    [data-testid="stSidebar"] * {{
        color: {text} !important;
    }}
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {{
        color: {text} !important;
    }}
    [data-testid="stSidebar"] h3 {{
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: {text_sec} !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.6rem !important;
    }}

    /* ===== RADIO BUTTONS (Transport Mode) ===== */
    .stRadio > div {{
        background: transparent !important;
    }}
    .stRadio label {{
        color: {text} !important;
        background: {radio_bg} !important;
        border-radius: 10px !important;
        padding: 0.35rem 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }}
    .stRadio [data-testid="stMarkdownContainer"] p {{
        color: {text} !important;
    }}
    /* Selected radio indicator */
    .stRadio div[role="radiogroup"] label[data-checked="true"] {{
        border-left: 3px solid {primary} !important;
    }}

    /* ===== SELECTBOX (Map Style) ===== */
    .stSelectbox > div > div {{
        background-color: {select_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        color: {text} !important;
    }}
    .stSelectbox label {{
        color: {text} !important;
    }}
    .stSelectbox [data-baseweb="select"] > div {{
        background-color: {select_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}
    .stSelectbox [data-baseweb="select"] span {{
        color: {text} !important;
    }}
    /* Dropdown menu */
    [data-baseweb="menu"],
    [data-baseweb="popover"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}
    [data-baseweb="menu"] li {{
        color: {text} !important;
        background-color: {card} !important;
    }}
    [data-baseweb="menu"] li:hover {{
        background-color: {card_hover} !important;
    }}

    /* Cards */
    .tm-card {{
        background: {card};
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        border: 1px solid {border};
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 0.85rem;
        transition: all 0.2s ease;
        color: {text} !important;
    }}
    .tm-card:hover {{
        background: {card_hover};
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }}

    .tm-metric-value {{
        font-size: 1.65rem;
        font-weight: 700;
        color: {text} !important;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}
    .tm-metric-label {{
        font-size: 0.78rem;
        color: {text_sec} !important;
        font-weight: 500;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}

    .tm-logo {{
        font-size: 1.55rem;
        font-weight: 700;
        color: {primary} !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        letter-spacing: -0.03em;
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.25rem !important;
        transition: all 0.18s ease !important;
        border: none !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    }}
    .stButton > button[kind="primary"] {{
        background: {primary} !important;
        color: #FFFFFF !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: {card} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
    }}

    /* Text inputs */
    .stTextInput > div > div > input {{
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        border: 1px solid {border} !important;
        background: {input_bg} !important;
        color: {text} !important;
        font-size: 0.95rem !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {primary} !important;
        box-shadow: 0 0 0 3px rgba(26,115,232,0.15) !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: {text_sec} !important;
        opacity: 0.8 !important;
    }}
    .stTextInput label {{
        color: {text} !important;
    }}

    .tm-section-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {text} !important;
        margin: 1.4rem 0 0.9rem 0;
        letter-spacing: -0.01em;
    }}

    .tm-empty {{
        text-align: center;
        padding: 3.5rem 2rem;
        background: {card};
        border-radius: 20px;
        border: 1px solid {border};
        color: {text} !important;
    }}

    .tm-error {{
        background: {card};
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        border-left: 4px solid {danger};
        margin-bottom: 1rem;
        color: {text} !important;
    }}

    .streamlit-expanderHeader {{
        color: {text} !important;
    }}

    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 3px; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_top_nav(dark_mode: bool) -> None:
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown('<div class="tm-logo">🗺️ TravelMate</div>', unsafe_allow_html=True)
    with col2:
        label = "☀️ Light" if dark_mode else "🌙 Dark"
        if st.button(label, use_container_width=True, key="theme_toggle"):
            st.session_state.dark_mode = not dark_mode
            st.rerun()
    with col3:
        if st.button("ℹ️ About", use_container_width=True, key="about_btn"):
            st.session_state.show_about = True


def render_sidebar() -> Dict:
    st.sidebar.markdown("### 📍 Locations")

    start = st.sidebar.text_input(
        "Starting Point",
        placeholder="Example: New York, USA  or  Chennai",
        key="input_start",
        help="Enter a city, address, landmark, or coordinates (e.g. 40.7128, -74.0060)",
    )
    end = st.sidebar.text_input(
        "Destination",
        placeholder="Example: Coimbatore  or  Statue of Liberty",
        key="input_end",
        help="Enter your destination city, address, or landmark",
    )

    st.sidebar.markdown("### 🚀 Transport Mode")
    mode_icons = {k: f"{v['icon']}  {k}" for k, v in TRANSPORT_MODES.items()}
    mode = st.sidebar.radio(
        "Select mode",
        options=list(TRANSPORT_MODES.keys()),
        format_func=lambda x: mode_icons[x],
        index=2,
        key="transport_mode",
        label_visibility="collapsed",
    )

    st.sidebar.markdown("### 🗺️ Map Style")
    map_style = st.sidebar.selectbox(
        "Map style",
        options=["OpenStreetMap", "Satellite", "Terrain", "Dark", "Light"],
        index=0,
        key="map_style",
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        generate = st.button("🧭 Find Routes", type="primary", use_container_width=True)
    with col_b:
        clear = st.button("🗑️ Clear", use_container_width=True)

    return {
        "start": start,
        "end": end,
        "mode": mode,
        "map_style": map_style,
        "generate": generate,
        "clear": clear,
    }


def render_route_selector(response: MultiRouteResponse, selected: str) -> str:
    if not response.success or not response.routes:
        return selected

    st.markdown('<div class="tm-section-title">Available Routes</div>', unsafe_allow_html=True)

    cols = st.columns(len(response.routes))
    new_selected = selected

    for idx, (key, route) in enumerate(response.routes.items()):
        with cols[idx]:
            is_selected = key == selected
            label = route.label
            sub = f"{format_distance(route.distance_km)} · {format_duration(route.duration_min)}"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                f"{label}\n{sub}",
                key=f"route_btn_{key}",
                use_container_width=True,
                type=btn_type,
            ):
                new_selected = key

    return new_selected


def render_metrics(route: RouteResult, mode: str) -> None:
    st.markdown('<div class="tm-section-title">Route Details</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{format_distance(route.distance_km)}</div>
                <div class="tm-metric-label">Distance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{format_duration(route.duration_min)}</div>
                <div class="tm-metric-label">Duration</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{route.average_speed_kmh:.0f} km/h</div>
                <div class="tm-metric-label">Avg Speed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{TRANSPORT_MODES[mode]['icon']} {mode}</div>
                <div class="tm-metric-label">Transport</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c5, c6, c7 = st.columns(3)
    with c5:
        cal_text = f"{route.calories} kcal" if route.calories > 0 else "—"
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{cal_text}</div>
                <div class="tm-metric-label">Calories</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{route.num_turns}</div>
                <div class="tm-metric-label">Turns</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c7:
        st.markdown(
            f"""
            <div class="tm-card">
                <div class="tm-metric-value">{route.difficulty}</div>
                <div class="tm-metric-label">Difficulty</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="tm-card" style="margin-top:0.4rem;">
            <span style="opacity:0.75;">Road Type:</span> <strong>{route.road_type}</strong>
            &nbsp;&nbsp;•&nbsp;&nbsp;
            <span style="opacity:0.75;">Route:</span> <strong>{route.label}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_about_modal() -> None:
    if st.session_state.get("show_about", False):
        with st.expander("About TravelMate", expanded=True):
            st.markdown(ABOUT_TEXT)
            if st.button("Close"):
                st.session_state.show_about = False
                st.rerun()


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="tm-empty">
            <div style="font-size:3.2rem; margin-bottom:1rem;">🗺️</div>
            <h3 style="margin-bottom:0.6rem; font-weight:600;">Plan your next journey</h3>
            <p style="opacity:0.65; max-width:400px; margin:0 auto; line-height:1.5;">
                Enter a starting point and destination, choose your transport mode,
                then click <strong>Find Routes</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str) -> None:
    st.markdown(
        f"""
        <div class="tm-error">
            <strong style="color:#EA4335;">Unable to calculate route</strong><br>
            <span style="opacity:0.85;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

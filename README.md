# 🗺️ TravelMate

**Professional desktop routing & navigation experience built with Python & Streamlit.**

TravelMate is a modern, multi-route mapping application inspired by Google Maps, Uber, and Apple Maps — redesigned specifically for desktop and laptop users. It provides Fastest, Shortest, and Alternate routes with rich statistics, multiple map styles, and a clean premium interface.

![TravelMate](assets/logo.png)

---

## ✨ Features

- **Multi-route planning** – Fastest (blue), Shortest (green), and Alternate (orange) routes displayed simultaneously
- **Multiple transport modes** – Walking, Bike, Car, Bus, Train with realistic speed & cost models
- **Rich route statistics** – Distance, duration, average speed, fuel cost, calories, number of turns, road type, difficulty
- **Interactive map** – Fullscreen, measure tool, locate control, mouse position, multiple tile layers
- **Map styles** – OpenStreetMap, Satellite, Terrain, Dark Mode, Light Mode
- **Smart search** – Supports city, street, landmark, postal code, and country
- **Modern UI** – Rounded cards, soft shadows, dark/light theme toggle, professional typography
- **Production-ready** – Modular codebase, caching, error handling, Streamlit Cloud compatible

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/TravelMate.git
cd TravelMate
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app** → select your repository.
4. Set the main file path to `app.py`.
5. Click **Deploy**.

Streamlit Cloud will automatically install the packages listed in `requirements.txt`.

> **Note**: The first route calculation may take longer because OSMnx downloads the street network. Subsequent requests for the same area are cached.

---

## 📁 Project Structure

```
TravelMate/
├── app.py                 # Main Streamlit entry point
├── requirements.txt       # Python dependencies
├── config.py              # Colors, speeds, constants, map tiles
├── utils.py               # Geocoding, formatting, calculations
├── route_engine.py        # OSMnx + NetworkX multi-route engine
├── ui.py                  # Custom CSS, cards, sidebar, metrics
├── map_utils.py           # Folium map construction & rendering
├── assets/
│   ├── logo.png           # Application logo
│   └── styles.css         # Extra design-system CSS
└── README.md              # This file
```

---

## 🛠️ Tech Stack

| Library                    | Purpose                              |
|----------------------------|--------------------------------------|
| Streamlit                  | Web application framework            |
| Folium + streamlit-folium  | Interactive maps                     |
| OSMnx                      | OpenStreetMap network download       |
| NetworkX                   | Graph algorithms (shortest paths)    |
| Geopy                      | Geocoding (Nominatim)                |
| Pandas / NumPy             | Data handling & calculations         |
| Pillow                     | Image support                        |

---

## 🎨 Design Inspiration

The interface is a complete desktop redesign inspired by modern mapping products:

- Google Maps
- Uber
- Apple Maps
- Notion
- Airbnb

Key design principles: generous spacing, soft shadows, rounded cards, clear visual hierarchy, and a calm professional color palette.

---

## ⚙️ Configuration

All tunable values live in `config.py`:

- Average speeds per transport mode
- Route colors and weights
- Map tile providers
- Error messages
- UI constants

You can change branding, speeds, or colors without touching the rest of the code.

---

## ⚠️ Known Limitations

- **Train routing** is simplified (uses the drive network). Real train routing would require GTFS data.
- Very long distances (> 50 km) are blocked for performance reasons.
- First request in a new area downloads the OpenStreetMap graph (can take 10–30 seconds).
- Nominatim has usage policies; the app uses rate limiting and caching to stay respectful.

---

## 📄 License

MIT License – feel free to use, modify, and deploy.

---

## 🙏 Credits

Built with ❤️ using open-source tools from the OpenStreetMap community, OSMnx, NetworkX, and Streamlit.

**TravelMate** – Plan better journeys.

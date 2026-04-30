import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from profile import (
    init_profile, get_profile, set_profile, profile_banner,
    STATIONS, POLLEN_PARAMS, THRESHOLDS, LEVEL_ORDER,
    sensitivity_mult, get_level, level_color, level_emoji,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BlessYou · Swiss Pollen Forecast",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_profile()
p = get_profile()

# ── Auto Location Detection ────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def detect_city() -> str:
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        data = r.json()
        detected = data.get("city", "Zürich")
        for city in STATIONS.keys():
            if city.lower() in detected.lower() or detected.lower() in city.lower():
                return city
        return "Zürich"
    except Exception:
        return "Zürich"

# ── Data fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_pollen(lat, lon, pollen_vars):
    variables = ",".join(set(pollen_vars))
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={variables}&forecast_days=5&timezone=Europe%2FZurich"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("hourly", None)
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&timezone=Europe%2FZurich"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("current", None)
    except Exception:
        return None

@st.cache_data(ttl=86400)
def fetch_places_osm(lat, lon, amenity):
    url = "https://overpass-api.de/api/interpreter"
    query = f"[out:json][timeout:25];(node[amenity={amenity}](around:5000,{lat},{lon});way[amenity={amenity}](around:5000,{lat},{lon}););out body center;"
    try:
        r = requests.get(url, params={"data": query}, timeout=25, headers={"User-Agent": "BlessYou-App/1.0"})
        r.raise_for_status()
        elements = r.json().get("elements", [])
        places = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name", "Unknown")
            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            address = f"{street} {housenumber}".strip() or "Address not available"
            if el["type"] == "node":
                place_lat, place_lon = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                place_lat, place_lon = center.get("lat"), center.get("lon")
            if place_lat and place_lon:
                places.append({"name": name, "address": address, "lat": place_lat, "lon": place_lon})
        return places[:8]
    except Exception as e:
        st.warning(f"Could not load places: {e}")
        return []

def is_in_season(pollen):
    month = datetime.now().month
    seasons = {
        "Birch":   [3, 4, 5],
        "Grass":   [5, 6, 7, 8],
        "Mugwort": [7, 8, 9],
        "Hazel":   [1, 2, 3],
        "Alder":   [2, 3, 4],
    }
    return month in seasons.get(pollen, [])

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌿 BlessYou")
    st.caption("Swiss Pollen Forecast")
    st.divider()

    # Pre-fill from profile if setup done
    selected_pollens = st.multiselect(
        "Your pollen allergies",
        options=list(POLLEN_PARAMS.keys()),
        default=p["pollens"] if p["pollens"] else ["Birch", "Grass"],
    )
    st.markdown("**🎚️ Your sensitivity per pollen:**")
    sensitivities = {}
    for pollen in selected_pollens:
        sensitivities[pollen] = st.select_slider(
            f"{pollen}",
            options=["Low", "Medium", "High"],
            value=p["sensitivities"].get(pollen, "Medium"),
            key=f"sens_{pollen}"
        )

    detected_city = detect_city()
    city_list = list(STATIONS.keys())
    saved_city = p["city"] if p["setup_done"] else detected_city
    default_index = city_list.index(saved_city) if saved_city in city_list else 0

    selected_city = st.selectbox(
        "📍 Your location",
        options=city_list,
        index=default_index,
    )

    # Sync sidebar choices back to profile
    set_profile({
        "city": selected_city,
        "pollens": selected_pollens,
        "sensitivities": sensitivities,
    })

    st.divider()
    if st.button("↻ Refresh Data", use_container_width=True):
        st.cache_data.clear()
    st.caption("Data: Open-Meteo Air Quality API")

# ── Header ─────────────────────────────────────────────────────────────────────
col_title, col_meta = st.columns([3, 1])
with col_title:
    st.title("🌿 BlessYou — Swiss Pollen Monitor")
    st.caption(f"Real-time pollen forecast · {datetime.now().strftime('%A, %d %B %Y')}")
with col_meta:
    city_info = STATIONS.get(selected_city, {})
    st.metric(label="📍 Location", value=selected_city, delta=f"Canton {city_info.get('canton', '')}")

# ── Profile banner ─────────────────────────────────────────────────────────────
st.divider()
profile_banner()
st.divider()

if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()

# ── Fetch data ─────────────────────────────────────────────────────────────────
home = STATIONS[selected_city]
api_vars = list({POLLEN_PARAMS[p_]["api"] for p_ in selected_pollens})

with st.spinner(f"Loading pollen forecast for {selected_city}…"):
    hourly = fetch_pollen(home["lat"], home["lon"], api_vars)

if not hourly:
    st.error("❌ Could not load pollen data from Open-Meteo. Check your connection.")
    st.stop()

df = pd.DataFrame(hourly)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)
today = datetime.now().date()
today_df = df[df["time"].dt.date == today]

today_vals = {}
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    if api_key in today_df.columns:
        vals = pd.to_numeric(today_df[api_key], errors="coerce").dropna()
        today_vals[pollen] = float(vals.max()) if len(vals) > 0 else np.nan
    else:
        today_vals[pollen] = np.nan

with st.spinner("Loading weather data..."):
    weather = fetch_weather(home["lat"], home["lon"])

with st.spinner("Loading pharmacies and doctors..."):
    pharmacies = fetch_places_osm(home["lat"], home["lon"], "pharmacy")
    doctors = fetch_places_osm(home["lat"], home["lon"], "doctors")

# ── Section 1: Today's Pollen Levels ──────────────────────────────────────────
st.subheader("🌿 Today's Pollen Levels")

# If risk score is set, show link to risk page
if get_profile()["risk_score"] is not None:
    score = get_profile()["risk_score"]
    badge = get_profile()["risk_badge"]
    st.success(
        f"🎯 Your personal risk score today is **{score}/10** — **{badge}**. "
        f"Go to the **🎯 Risk Score** page for your full personalised breakdown!"
    )

cols = st.columns(len(selected_pollens))
for i, pollen in enumerate(selected_pollens):
    val = today_vals.get(pollen, np.nan)
    pollen_mult = sensitivity_mult(sensitivities.get(pollen, "Medium"))
    level = get_level(val, THRESHOLDS[pollen], pollen_mult)
    display_val = f"{val:.0f} gr/m³" if not np.isnan(val) else "N/A"
    in_season = is_in_season(pollen)
    season_label = "🟢 In season" if in_season else "⚪ Out of season"
    with cols[i]:
        st.metric(
            label=f"{pollen}  ·  {season_label}",
            value=display_val,
            delta=level.upper(),
            delta_color="off",
        )
        st.caption(f"{level_emoji(level)} {level.upper()}")

st.divider()

# ── Section 2: Live Weather Conditions ────────────────────────────────────────
st.subheader("🌤️ Live Weather Conditions")

if weather:
    temp     = weather.get("temperature_2m", "N/A")
    humidity = weather.get("relative_humidity_2m", "N/A")
    rain     = weather.get("precipitation", "N/A")
    wind     = weather.get("wind_speed_10m", "N/A")

    wcol1, wcol2, wcol3, wcol4 = st.columns(4)
    wcol1.metric("🌡️ Temperature", f"{temp}°C")
    wcol2.metric("💧 Humidity",    f"{humidity}%")
    wcol3.metric("🌧️ Rain",        f"{rain} mm")
    wcol4.metric("🌬️ Wind Speed",  f"{wind} km/h")

    if isinstance(wind, (int, float)) and wind > 20:
        st.warning(f"🌬️ High wind today ({wind} km/h) — pollen is spreading more than usual!")
    elif isinstance(rain, (int, float)) and rain > 0:
        st.success(f"🌧️ Rain today ({rain}mm) — rain washes pollen out of the air. Good day to go outside!")
    elif isinstance(humidity, (int, float)) and humidity < 40:
        st.warning(f"☀️ Low humidity today ({humidity}%) — dry air means pollen stays airborne longer.")
    elif isinstance(humidity, (int, float)) and humidity > 70:
        st.info(f"💧 High humidity today ({humidity}%) — pollen tends to clump and fall. Slightly better conditions!")
    else:
        st.info("🌤️ Normal weather conditions today — no special weather impact on pollen levels.")
else:
    st.warning("Could not load weather data.")

st.divider()

# ── Section 3: Switzerland Pollen Map ─────────────────────────────────────────
st.subheader("🗺️ Switzerland Pollen Map")

@st.cache_data(ttl=3600)
def fetch_all_stations(pollen_vars: tuple) -> dict:
    results = {}
    for city, info in STATIONS.items():
        data = fetch_pollen(info["lat"], info["lon"], list(pollen_vars))
        if data:
            tdf = pd.DataFrame(data)
            tdf["time"] = pd.to_datetime(tdf["time"])
            today_data = tdf[tdf["time"].dt.date == datetime.now().date()]
            city_vals = {}
            for var in pollen_vars:
                if var in today_data.columns:
                    peak = pd.to_numeric(today_data[var], errors="coerce").max()
                    city_vals[var] = float(peak) if not np.isnan(peak) else 0.0
                else:
                    city_vals[var] = 0.0
            results[city] = city_vals
    return results

with st.spinner("Fetching map data for all Swiss cities…"):
    all_data = fetch_all_stations(tuple(api_vars))

def build_map(weather=None, pharmacies=[], doctors=[]):
    m = folium.Map(
        location=[46.8, 8.2], zoom_start=8,
        tiles="CartoDB positron", control_scale=True,
        min_zoom=7, max_zoom=13, max_bounds=True,
    )
    m.fit_bounds([[45.8, 5.9], [47.9, 10.5]])
    m.options['minZoom'] = 7
    heat_pts = []
    for city, info in STATIONS.items():
        city_vals = all_data.get(city, {})
        total = 0.0
        worst = "none"
        for pollen in selected_pollens:
            api_key = POLLEN_PARAMS[pollen]["api"]
            val = city_vals.get(api_key, 0.0)
            total += val
            pollen_mult = sensitivity_mult(sensitivities.get(pollen, "Medium"))
            lv = get_level(val, THRESHOLDS[pollen], pollen_mult)
            if LEVEL_ORDER.index(lv) > LEVEL_ORDER.index(worst):
                worst = lv
        heat_pts.append([info["lat"], info["lon"], min(total, 400)])
        clr = level_color(worst)
        popup_html = (
            f"<b>{city}</b> ({info['canton']})<br>"
            f"<b style='color:{clr}'>{worst.upper()}</b><br>"
            f"Combined: {total:.0f} gr/m³"
        )
        folium.CircleMarker(
            location=[info["lat"], info["lon"]], radius=13,
            color="white", weight=2, fill=True,
            fill_color=clr, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {worst}",
        ).add_to(m)

    HeatMap(
        heat_pts, radius=55, blur=40, min_opacity=0.3,
        gradient={"0.0": "#2d6a4f", "0.35": "#B8935A", "0.65": "#C4532A", "1.0": "#5b21b6"},
    ).add_to(m)

    weather_popup = f"<b>📍 {selected_city}</b><br>"
    if weather:
        temp     = weather.get("temperature_2m", "N/A")
        humidity = weather.get("relative_humidity_2m", "N/A")
        wind     = weather.get("wind_speed_10m", "N/A")
        rain     = weather.get("precipitation", "N/A")
        weather_popup += f"🌡️ {temp}°C &nbsp; 💧 {humidity}%<br>🌬️ {wind} km/h &nbsp; 🌧️ {rain}mm"

    folium.Marker(
        [home["lat"], home["lon"]],
        tooltip=f"📍 {selected_city} — click for weather",
        popup=folium.Popup(weather_popup, max_width=250),
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)

    for p_ in pharmacies:
        folium.Marker(
            [p_["lat"], p_["lon"]],
            tooltip=p_["name"],
            popup=folium.Popup(f"<b>💊 {p_['name']}</b><br>📍 {p_['address']}", max_width=200),
            icon=folium.Icon(color="red", icon="plus", prefix="fa"),
        ).add_to(m)

    for d in doctors:
        folium.Marker(
            [d["lat"], d["lon"]],
            tooltip=d["name"],
            popup=folium.Popup(f"<b>🩺 {d['name']}</b><br>📍 {d['address']}", max_width=200),
            icon=folium.Icon(color="blue", icon="user-md", prefix="fa"),
        ).add_to(m)

    return m

col_tog1, col_tog2 = st.columns(2)
with col_tog1:
    show_pharmacies = st.toggle("💊 Show pharmacies on map", value=False)
with col_tog2:
    show_doctors = st.toggle("🩺 Show doctors on map", value=False)

st_folium(
    build_map(
        weather=weather,
        pharmacies=pharmacies if show_pharmacies else [],
        doctors=doctors if show_doctors else [],
    ),
    height=460,
    use_container_width=True
)

st.divider()

# ── Section 4: 5-Day Pollen Forecast ──────────────────────────────────────────
st.subheader("📈 5-Day Pollen Forecast")

fig = go.Figure()
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    if api_key not in df.columns:
        continue
    vals = pd.to_numeric(df[api_key], errors="coerce").clip(lower=0)
    clr = POLLEN_PARAMS[pollen]["color"]
    r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
    fig.add_trace(go.Scatter(
        x=df["time"], y=vals, name=pollen,
        line=dict(color=clr, width=2.5),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.10)",
        mode="lines",
    ))

fig.add_vline(
    x=datetime.now().timestamp() * 1000,
    line_dash="dash", line_color="#adb5bd",
    annotation_text="Now", annotation_position="top right",
)

t = THRESHOLDS[selected_pollens[0]]
fig.add_hrect(y0=0,    y1=t[0], fillcolor="green",  opacity=0.03, line_width=0)
fig.add_hrect(y0=t[0], y1=t[1], fillcolor="green",  opacity=0.05, line_width=0)
fig.add_hrect(y0=t[1], y1=t[2], fillcolor="orange", opacity=0.05, line_width=0)
fig.add_hrect(y0=t[2], y1=t[3], fillcolor="red",    opacity=0.05, line_width=0)

fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(title="", gridcolor="#f0f0f0"),
    yaxis=dict(title="Pollen (grains/m³)", gridcolor="#f0f0f0"),
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=10, r=10, t=40, b=10),
    height=360,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Section 5: Nearby Pharmacies & Doctors ────────────────────────────────────
st.subheader("💊 Nearby Pharmacies & Doctors")
st.caption(f"Live data from OpenStreetMap · within 5km of {selected_city}")

show_list = st.toggle("📋 Show list of pharmacies & doctors", value=False)
if show_list:
    col_pharm, col_doc = st.columns(2)
    with col_pharm:
        st.markdown("**💊 Pharmacies nearby**")
        if pharmacies:
            for ph in pharmacies:
                st.markdown(f"🏥 **{ph['name']}**  \n📍 {ph['address']}")
        else:
            st.info("No pharmacies found nearby.")
    with col_doc:
        st.markdown("**🩺 Doctors nearby**")
        if doctors:
            for d in doctors:
                st.markdown(f"👨‍⚕️ **{d['name']}**  \n📍 {d['address']}")
        else:
            st.info("No doctors found nearby.")

st.divider()
st.caption("🌿 BlessYou · Pollen data: Open-Meteo Air Quality API · Weather: Open-Meteo · Places: OpenStreetMap")
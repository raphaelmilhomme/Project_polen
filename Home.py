import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime
from user_profile import (
    init_profile, get_profile, set_profile, profile_banner,
    STATIONS, POLLEN_PARAMS, THRESHOLDS, LEVEL_ORDER,
    sensitivity_mult, get_level, level_color, level_emoji,
)

st.set_page_config(
    page_title="BlessYou · Swiss Pollen Forecast",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_profile()
p = get_profile()

LEVEL_SCORES = {"none": 0, "low": 2, "moderate": 5, "high": 7, "very high": 10}

# ── Data fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def detect_city():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        detected = r.json().get("city", "Zürich")
        for city in STATIONS:
            if city.lower() in detected.lower() or detected.lower() in city.lower():
                return city
        return "Zürich"
    except:
        return "Zürich"

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
    except:
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
    except:
        return None

@st.cache_data(ttl=86400)
def fetch_places_osm(lat, lon, amenity):
    url   = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:30];
    (
      node[amenity={amenity}](around:5000,{lat},{lon});
      way[amenity={amenity}](around:5000,{lat},{lon});
    );
    out body center;
    """
    try:
        r = requests.post(
            url,
            data={"data": query},
            timeout=30,
            headers={"User-Agent": "BlessYou-App/1.0"},
        )
        r.raise_for_status()
        places = []
        for el in r.json().get("elements", []):
            tags   = el.get("tags", {})
            name   = tags.get("name", "Unknown")
            street = tags.get("addr:street", "")
            number = tags.get("addr:housenumber", "")
            addr   = f"{street} {number}".strip() or "Address not available"
            if el["type"] == "node":
                la, lo = el.get("lat"), el.get("lon")
            else:
                c = el.get("center", {})
                la, lo = c.get("lat"), c.get("lon")
            if la and lo:
                places.append({"name": name, "address": addr, "lat": la, "lon": lo})
        return places[:8]
    except Exception as e:
        return []

def is_in_season(pollen):
    month   = datetime.now().month
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

    city_list   = list(STATIONS.keys())
    saved_city  = p["city"] if p["city"] in city_list else detect_city()
    default_idx = city_list.index(saved_city)

    selected_city = st.selectbox("📍 Your location", options=city_list, index=default_idx)

    st.divider()
    st.markdown("**👤 Your profile**")

    age_group = st.radio(
        "🎂 Age group",
        ["Under 12", "12–65", "Over 65"],
        index=["Under 12", "12–65", "Over 65"].index(p["age_group"]) if p["age_group"] in ["Under 12", "12–65", "Over 65"] else 1,
        horizontal=True,
    )
    has_asthma = st.radio(
        "🫁 Asthma?",
        ["No", "Yes"],
        index=["No", "Yes"].index(p["asthma"]),
        horizontal=True,
    )
    med_options = [
        "No medication",
        "Antihistamines (e.g. Cetirizine)",
        "Nasal spray",
        "Both antihistamines + nasal spray",
    ]
    medication = st.selectbox(
        "💊 Medication",
        med_options,
        index=med_options.index(p["medication"]) if p["medication"] in med_options else 0,
    )
    hours_outside = st.slider("🚶 Hours outside today", 0, 12, p["hours_outside"])

    # Save everything including city to shared profile
    set_profile({
        "city":          selected_city,
        "pollens":       selected_pollens,
        "sensitivities": sensitivities,
        "age_group":     age_group,
        "asthma":        has_asthma,
        "medication":    medication,
        "hours_outside": hours_outside,
        "setup_done":    True,
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

st.divider()
profile_banner()
st.divider()

if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()

# ── Fetch data ─────────────────────────────────────────────────────────────────
home     = STATIONS[selected_city]
api_vars = list({POLLEN_PARAMS[p_]["api"] for p_ in selected_pollens})

with st.spinner(f"Loading pollen forecast for {selected_city}…"):
    hourly = fetch_pollen(home["lat"], home["lon"], api_vars)

if not hourly:
    st.error("❌ Could not load pollen data. Check your connection.")
    st.stop()

df         = pd.DataFrame(hourly)
df["time"] = pd.to_datetime(df["time"])
df         = df.sort_values("time").reset_index(drop=True)
today      = datetime.now().date()
today_df   = df[df["time"].dt.date == today]

today_vals = {}
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    if api_key in today_df.columns:
        vals = pd.to_numeric(today_df[api_key], errors="coerce").dropna()
        today_vals[pollen] = float(vals.max()) if len(vals) > 0 else np.nan
    else:
        today_vals[pollen] = np.nan

with st.spinner("Loading weather..."):
    weather = fetch_weather(home["lat"], home["lon"])

with st.spinner("Loading pharmacies and doctors..."):
    pharmacies = fetch_places_osm(home["lat"], home["lon"], "pharmacy")
    doctors    = fetch_places_osm(home["lat"], home["lon"], "doctors")

# ── Section 1: Today's Pollen Levels ──────────────────────────────────────────
st.subheader("🌿 Today's Pollen Levels")

cols = st.columns(len(selected_pollens))
pollen_levels = {}
for i, pollen in enumerate(selected_pollens):
    val          = today_vals.get(pollen, np.nan)
    mult         = sensitivity_mult(sensitivities.get(pollen, "Medium"))
    level        = get_level(val, THRESHOLDS[pollen], mult)
    pollen_levels[pollen] = level
    display_val  = f"{val:.0f} gr/m³" if not np.isnan(val) else "N/A"
    season_label = "🟢 In season" if is_in_season(pollen) else "⚪ Out of season"
    with cols[i]:
        st.metric(
            label=f"{pollen}  ·  {season_label}",
            value=display_val,
            delta=level.upper(),
            delta_color="off",
        )
        st.caption(f"{level_emoji(level)} {level.upper()}")

st.divider()

# ── Section 2: Weather + Personal Risk Score ───────────────────────────────────
st.subheader("🌤️ Weather & Your Personal Risk Score")

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
        st.warning(f"☀️ Low humidity ({humidity}%) — dry air means pollen stays airborne longer.")
    elif isinstance(humidity, (int, float)) and humidity > 70:
        st.info(f"💧 High humidity ({humidity}%) — pollen tends to clump and fall. Slightly better!")
    else:
        st.info("🌤️ Normal weather conditions today.")

    st.divider()
    st.markdown("#### 🎯 Your Personal Risk Score")

    raw_scores   = [LEVEL_SCORES[pollen_levels[p_]] for p_ in selected_pollens]
    worst_raw    = max(raw_scores)
    other_scores = sorted(raw_scores, reverse=True)[1:]
    additional   = sum(s * 0.2 for s in other_scores)
    avg_raw      = min(worst_raw + additional, 10.0)

    age_factor        = 1.2 if age_group in ["Under 12", "Over 65"] else 1.0
    asthma_factor     = 1.3 if has_asthma == "Yes" else 1.0
    medication_factor = {
        "No medication": 1.0,
        "Antihistamines (e.g. Cetirizine)": 0.7,
        "Nasal spray": 0.8,
        "Both antihistamines + nasal spray": 0.5,
    }[medication]
    exposure_factor = 1 + (hours_outside * 0.05)

    weather_factor = 1.0
    if isinstance(wind,     (int, float)) and wind     > 20: weather_factor += 0.2
    if isinstance(rain,     (int, float)) and rain     > 0:  weather_factor -= 0.2
    if isinstance(humidity, (int, float)) and humidity < 40: weather_factor += 0.1

    final_score = min(round(
        avg_raw * age_factor * asthma_factor * medication_factor
        * exposure_factor * weather_factor, 1
    ), 10.0)

    if final_score <= 2:   badge, badge_color = "🟢 Safe Day",        "success"
    elif final_score <= 4: badge, badge_color = "🟡 Low Risk Day",    "success"
    elif final_score <= 6: badge, badge_color = "🟠 Caution Day",     "warning"
    elif final_score <= 8: badge, badge_color = "🔴 High Risk Day",   "error"
    else:                  badge, badge_color = "🟣 Stay Inside Day", "error"

    set_profile({"risk_score": final_score, "risk_badge": badge})

    col_score, col_badge, col_explain = st.columns([1, 1, 2])
    with col_score:
        st.metric(label="Personal Risk Score", value=f"{final_score} / 10")
        st.progress(int(final_score * 10))
    with col_badge:
        st.markdown(f"### {badge}")
        st.caption("Live pollen + weather + your profile")
    with col_explain:
        st.info(
            f"**How this is calculated:**\n\n"
            f"- Pollen: {', '.join([f'{p_} ({pollen_levels[p_]})' for p_ in selected_pollens])}\n"
            f"- Sensitivity: **{list(sensitivities.values())[0] if sensitivities else 'Medium'}**\n"
            f"- Asthma: **{has_asthma}**\n"
            f"- Medication: **{medication}**\n"
            f"- Hours outside: **{hours_outside}h**\n"
            f"- Weather: **{'↑ worse' if weather_factor > 1 else '↓ better' if weather_factor < 1 else 'neutral'}**\n"
            f"- Age factor: **{'Yes' if age_group in ['Under 12', 'Over 65'] else 'No'}**"
        )

    st.divider()
    st.markdown("#### 💊 Medication Reminder")
    if medication == "No medication":
        if final_score >= 5:
            st.warning("⚠️ Your risk score is high. Consider speaking to a doctor about antihistamines like Cetirizine or Loratadine.")
        else:
            st.success("✅ No medication needed today based on your risk level.")
    elif "Antihistamines" in medication:
        st.success("💊 Take your antihistamine **2 hours before** going outside. Since pollen peaks at 6–10am, aim for **7am** today.")
    elif medication == "Nasal spray":
        st.success("🌿 Use your nasal spray **30 minutes** before going outside, every morning.")
    elif medication == "Both antihistamines + nasal spray":
        st.success("💊🌿 Antihistamine by **7am**, nasal spray by **8:30am**. Combined treatment reduces your risk by ~50%!")

else:
    st.warning("Could not load weather data.")

st.divider()

# ── Section 3: Best Day This Week ─────────────────────────────────────────────
st.subheader("📅 Best Day to Go Outside This Week")

df["date"]   = df["time"].dt.date
daily_scores = []
mult_avg     = sum(sensitivity_mult(sensitivities.get(p_, "Medium")) for p_ in selected_pollens) / len(selected_pollens)

for d in sorted(df["date"].unique()):
    day_data = df[df["date"] == d]
    day_vals = {}
    for pollen in selected_pollens:
        api_key = POLLEN_PARAMS[pollen]["api"]
        if api_key in day_data.columns:
            peak = pd.to_numeric(day_data[api_key], errors="coerce").max()
            day_vals[pollen] = float(peak) if not np.isnan(peak) else 0.0
        else:
            day_vals[pollen] = 0.0
    day_levels = {p_: get_level(day_vals[p_], THRESHOLDS[p_], mult_avg) for p_ in selected_pollens}
    day_raw    = sum([LEVEL_SCORES[day_levels[p_]] for p_ in selected_pollens]) / len(selected_pollens)
    daily_scores.append({
        "date":  d,
        "label": pd.Timestamp(d).strftime("%A %d %b"),
        "score": round(day_raw, 1),
    })

best_day  = min(daily_scores, key=lambda x: x["score"])
worst_day = max(daily_scores, key=lambda x: x["score"])

col_best, col_worst = st.columns(2)
with col_best:
    st.success(f"**✅ Best day: {best_day['label']}**\n\nPollen score: {best_day['score']}/10\n\nGreat day for outdoor activities!")
with col_worst:
    st.error(f"**⚠️ Worst day: {worst_day['label']}**\n\nPollen score: {worst_day['score']}/10\n\nTry to stay indoors if possible.")

st.divider()

# ── Section 4: Switzerland Pollen Map ─────────────────────────────────────────
st.subheader("🗺️ Switzerland Pollen Map")

@st.cache_data(ttl=3600)
def fetch_all_stations(pollen_vars):
    results = {}
    for city, info in STATIONS.items():
        data = fetch_pollen(info["lat"], info["lon"], list(pollen_vars))
        if data:
            tdf         = pd.DataFrame(data)
            tdf["time"] = pd.to_datetime(tdf["time"])
            today_data  = tdf[tdf["time"].dt.date == datetime.now().date()]
            city_vals   = {}
            for var in pollen_vars:
                if var in today_data.columns:
                    peak = pd.to_numeric(today_data[var], errors="coerce").max()
                    city_vals[var] = float(peak) if not np.isnan(peak) else 0.0
                else:
                    city_vals[var] = 0.0
            results[city] = city_vals
    return results

with st.spinner("Fetching map data…"):
    all_data = fetch_all_stations(tuple(api_vars))

def build_map(weather=None, pharmacies=[], doctors=[]):
    m = folium.Map(
        location=[46.8, 8.2],
        zoom_start=8,
        tiles="CartoDB positron",
        control_scale=True,
        min_zoom=7,
        max_zoom=13,
        max_bounds=True,
    )
    m.fit_bounds([[45.8, 5.9], [47.9, 10.5]])
    m.options['minZoom'] = 7
    m.options['maxBounds'] = [[45.5, 5.5], [48.2, 10.8]]
    m.options['maxBoundsViscosity'] = 1.0

    heat_pts = []
    for city, info in STATIONS.items():
        city_vals    = all_data.get(city, {})
        total, worst = 0.0, "none"
        for pollen in selected_pollens:
            api_key = POLLEN_PARAMS[pollen]["api"]
            val     = city_vals.get(api_key, 0.0)
            total  += val
            mult    = sensitivity_mult(sensitivities.get(pollen, "Medium"))
            lv      = get_level(val, THRESHOLDS[pollen], mult)
            if LEVEL_ORDER.index(lv) > LEVEL_ORDER.index(worst):
                worst = lv
        heat_pts.append([info["lat"], info["lon"], min(total, 400)])
        clr        = level_color(worst)
        popup_html = f"<b>{city}</b> ({info['canton']})<br><b style='color:{clr}'>{worst.upper()}</b><br>Combined: {total:.0f} gr/m³"
        folium.CircleMarker(
            location=[info["lat"], info["lon"]], radius=13,
            color="white", weight=2, fill=True, fill_color=clr, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {worst}",
        ).add_to(m)

    HeatMap(heat_pts, radius=55, blur=40, min_opacity=0.3,
            gradient={"0.0": "#2d6a4f", "0.35": "#B8935A", "0.65": "#C4532A", "1.0": "#5b21b6"}).add_to(m)

    weather_popup = f"<b>📍 {selected_city}</b><br>"
    if weather:
        weather_popup += (
            f"🌡️ {weather.get('temperature_2m','N/A')}°C &nbsp; "
            f"💧 {weather.get('relative_humidity_2m','N/A')}%<br>"
            f"🌬️ {weather.get('wind_speed_10m','N/A')} km/h &nbsp; "
            f"🌧️ {weather.get('precipitation','N/A')}mm"
        )
    folium.Marker(
        [home["lat"], home["lon"]],
        tooltip=f"📍 {selected_city}",
        popup=folium.Popup(weather_popup, max_width=250),
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)

    for ph in pharmacies:
        folium.Marker(
            [ph["lat"], ph["lon"]], tooltip=ph["name"],
            popup=folium.Popup(f"<b>💊 {ph['name']}</b><br>📍 {ph['address']}", max_width=200),
            icon=folium.Icon(color="red", icon="plus", prefix="fa"),
        ).add_to(m)
    for d in doctors:
        folium.Marker(
            [d["lat"], d["lon"]], tooltip=d["name"],
            popup=folium.Popup(f"<b>🩺 {d['name']}</b><br>📍 {d['address']}", max_width=200),
            icon=folium.Icon(color="blue", icon="user-md", prefix="fa"),
        ).add_to(m)
    return m

col_tog1, col_tog2 = st.columns(2)
with col_tog1:
    show_pharmacies = st.toggle("💊 Show pharmacies", value=False)
with col_tog2:
    show_doctors = st.toggle("🩺 Show doctors", value=False)

st_folium(
    build_map(
        weather=weather,
        pharmacies=pharmacies if show_pharmacies else [],
        doctors=doctors if show_doctors else [],
    ),
    height=460, use_container_width=True
)

st.divider()

# ── Section 5: 5-Day Forecast ──────────────────────────────────────────────────
st.subheader("📈 5-Day Pollen Forecast")

fig = go.Figure()
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    if api_key not in df.columns:
        continue
    vals = pd.to_numeric(df[api_key], errors="coerce").clip(lower=0)
    clr  = POLLEN_PARAMS[pollen]["color"]
    r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
    fig.add_trace(go.Scatter(
        x=df["time"], y=vals, name=pollen,
        line=dict(color=clr, width=2.5),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.10)",
        mode="lines",
    ))

fig.add_vline(x=datetime.now().timestamp() * 1000, line_dash="dash", line_color="#adb5bd",
              annotation_text="Now", annotation_position="top right")

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
    margin=dict(l=10, r=10, t=40, b=10), height=360,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Section 6: Nearby Pharmacies & Doctors ────────────────────────────────────
st.subheader("💊 Nearby Pharmacies & Doctors")
st.caption(f"Live data from OpenStreetMap · within 5km of {selected_city}")

show_list = st.toggle("📋 Show list", value=False)
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
st.caption("🌿 BlessYou · Pollen: Open-Meteo · Weather: Open-Meteo · Places: OpenStreetMap")
import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BlessYou · Swiss Pollen Forecast",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Constants ──────────────────────────────────────────────────────────────────
STATIONS = {
    "Zürich":     {"canton": "ZH", "lat": 47.376, "lon": 8.538},
    "Bern":       {"canton": "BE", "lat": 46.948, "lon": 7.447},
    "Basel":      {"canton": "BS", "lat": 47.560, "lon": 7.589},
    "Geneva":     {"canton": "GE", "lat": 46.204, "lon": 6.143},
    "Lausanne":   {"canton": "VD", "lat": 46.519, "lon": 6.633},
    "Luzern":     {"canton": "LU", "lat": 47.050, "lon": 8.309},
    "St. Gallen": {"canton": "SG", "lat": 47.422, "lon": 9.369},
    "Lugano":     {"canton": "TI", "lat": 46.004, "lon": 8.960},
    "Sion":       {"canton": "VS", "lat": 46.233, "lon": 7.360},
    "Davos":      {"canton": "GR", "lat": 46.813, "lon": 9.844},
    "Neuchâtel":  {"canton": "NE", "lat": 47.000, "lon": 6.944},
    "Aarau":      {"canton": "AG", "lat": 47.392, "lon": 8.044},
    "Chur":       {"canton": "GR", "lat": 46.852, "lon": 9.533},
    "Frauenfeld": {"canton": "TG", "lat": 47.556, "lon": 8.898},
    "Bellinzona": {"canton": "TI", "lat": 46.193, "lon": 9.023},
}
 
POLLEN_PARAMS = {
    "Birch":   {"api": "birch_pollen",   "color": "#C4532A", "season": "Mar–May"},
    "Grass":   {"api": "grass_pollen",   "color": "#2d6a4f", "season": "May–Aug"},
    "Mugwort": {"api": "mugwort_pollen", "color": "#7B6FA0", "season": "Jul–Sep"},
    "Hazel":   {"api": "alder_pollen",   "color": "#B8935A", "season": "Jan–Mar"},
    "Alder":   {"api": "alder_pollen",   "color": "#6B8F6C", "season": "Feb–Apr"},
}
 
THRESHOLDS = {
    "Birch":   [1, 10,  50, 200],
    "Grass":   [1, 10,  50, 200],
    "Mugwort": [1,  5,  20,  80],
    "Hazel":   [1, 10,  50, 150],
    "Alder":   [1, 10,  50, 150],
}
 
LEVEL_ORDER = ["none", "low", "moderate", "high", "very high"]
 
# ── Data fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_pollen(lat: float, lon: float, pollen_vars: list) -> dict | None:
    variables = ",".join(set(pollen_vars))
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={variables}"
        f"&forecast_days=5"
        f"&timezone=Europe%2FZurich"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("hourly", None)
    except Exception:
        return None
 
# ── Helpers ────────────────────────────────────────────────────────────────────
def sensitivity_mult(sensitivity):
    return {"Low": 0.5, "Medium": 1.0, "High": 1.5}[sensitivity]
 
def get_level(value, thresholds, mult=1.0):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "none"
    v = float(value) * mult
    if v < thresholds[0]:   return "none"
    elif v < thresholds[1]: return "low"
    elif v < thresholds[2]: return "moderate"
    elif v < thresholds[3]: return "high"
    else:                   return "very high"
 
def level_color(level):
    return {
        "none":      "#9e9e9e",
        "low":       "#2d6a4f",
        "moderate":  "#B8935A",
        "high":      "#C4532A",
        "very high": "#5b21b6",
    }.get(level, "#9e9e9e")
 
def level_emoji(level):
    return {
        "none":      "⚪",
        "low":       "🟢",
        "moderate":  "🟡",
        "high":      "🔴",
        "very high": "🟣",
    }.get(level, "⚪")
 
def level_label(level):
    return f"{level_emoji(level)} {level.upper()}"
 
def advice_text(level, pollen_name):
    return {
        "none":      f"✅ No significant {pollen_name} detected. Safe to go outside.",
        "low":       f"🟢 Low {pollen_name}. Fine for most people. Consider antihistamines if sensitive.",
        "moderate":  f"🟡 Moderate {pollen_name}. Keep windows closed 6–10am. Pre-medicate before going out.",
        "high":      f"🔴 High {pollen_name}! Limit outdoor time, especially mornings. Shower after being outside.",
        "very high": f"🟣 Very high {pollen_name}! Stay indoors if possible. Use air purifiers and take medication.",
    }.get(level, "")
 
def personalized_advice(pollen_levels: dict, sensitivity: str) -> tuple[str, str]:
    worst_level = "none"
    worst_pollens = []
    for pollen, level in pollen_levels.items():
        if LEVEL_ORDER.index(level) > LEVEL_ORDER.index(worst_level):
            worst_level = level
            worst_pollens = [pollen]
        elif level == worst_level and level != "none":
            worst_pollens.append(pollen)
 
    risky = [p for p, l in pollen_levels.items() if LEVEL_ORDER.index(l) >= LEVEL_ORDER.index("moderate")]
    all_clear = all(l in ("none", "low") for l in pollen_levels.values())
 
    if all_clear:
        if sensitivity == "High":
            go_out = "🟢 Levels are low for your allergies. You can go outside — take your antihistamines as a precaution."
        else:
            go_out = "✅ All clear for your selected allergies. Enjoy the outdoors!"
    elif worst_level == "moderate":
        pollen_list = ", ".join(risky)
        if sensitivity == "High":
            go_out = f"⚠️ Moderate {pollen_list} detected. Given your high sensitivity, limit time outside and pre-medicate."
        elif sensitivity == "Medium":
            go_out = f"🟡 Moderate {pollen_list}. It's manageable — take antihistamines before heading out."
        else:
            go_out = f"🟡 Moderate {pollen_list}, but your low sensitivity means it should be fine with precautions."
    elif worst_level == "high":
        pollen_list = ", ".join(worst_pollens)
        if sensitivity == "High":
            go_out = f"🔴 High {pollen_list} — strongly advise staying indoors. Your sensitivity makes this a real risk."
        elif sensitivity == "Medium":
            go_out = f"🔴 High {pollen_list}. Limit outdoor activity, especially in the morning. Shower after going out."
        else:
            go_out = f"🔴 High {pollen_list}. Keep outdoor time short and avoid peak hours."
    elif worst_level == "very high":
        pollen_list = ", ".join(worst_pollens)
        if sensitivity == "High":
            go_out = f"🟣 Very high {pollen_list} — stay indoors. This is a severe risk for someone with your sensitivity."
        else:
            go_out = f"🟣 Very high {pollen_list}. Strongly recommend staying indoors and using air purifiers."
    else:
        go_out = "✅ No significant pollen detected for your allergies today."
 
    if all_clear:
        avoid = "💡 Any time of day is fine. Afternoon tends to be slightly better as pollen disperses."
    elif worst_level in ("moderate", "high", "very high"):
        if sensitivity == "High":
            avoid = "⛔ Avoid 6–10am entirely — peak dispersal time. After rain or post-7pm is safest for you."
        else:
            avoid = "⚠️ Avoid mornings (6–10am). Best window: afternoon (2–6pm) or right after rainfall."
    else:
        avoid = "💡 Afternoons are your best bet. Morning pollen counts are slightly elevated but manageable."
 
    return go_out, avoid
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌿 BlessYou")
    st.caption("Swiss Pollen Forecast")
    st.divider()
 
    selected_pollens = st.multiselect(
        "Your pollen allergies",
        options=list(POLLEN_PARAMS.keys()),
        default=["Birch", "Grass"],
    )
    sensitivity = st.select_slider(
        "Sensitivity level",
        options=["Low", "Medium", "High"],
        value="Medium",
    )
    selected_city = st.selectbox(
        "Your location",
        options=list(STATIONS.keys()),
        index=0,
    )
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
 
if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()
 
# ── Fetch data ─────────────────────────────────────────────────────────────────
home = STATIONS[selected_city]
mult = sensitivity_mult(sensitivity)
api_vars = list({POLLEN_PARAMS[p]["api"] for p in selected_pollens})
 
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
 
# ── Today's overview ───────────────────────────────────────────────────────────
st.subheader("Today's Pollen Levels")
 
cols = st.columns(len(selected_pollens))
for i, pollen in enumerate(selected_pollens):
    val = today_vals.get(pollen, np.nan)
    level = get_level(val, THRESHOLDS[pollen], mult)
    display_val = f"{val:.0f} gr/m³" if not np.isnan(val) else "N/A"
    with cols[i]:
        st.metric(
            label=f"{pollen}  ·  {POLLEN_PARAMS[pollen]['season']}",
            value=display_val,
            delta=level_label(level),
        )
 
st.divider()
 
# ── Personalized advice ────────────────────────────────────────────────────────
st.subheader("Personalized Advice")
 
pollen_levels = {
    pollen: get_level(today_vals.get(pollen, np.nan), THRESHOLDS[pollen], mult)
    for pollen in selected_pollens
}
 
go_out, avoid = personalized_advice(pollen_levels, sensitivity)
 
worst_level = max(pollen_levels.values(), key=lambda l: LEVEL_ORDER.index(l))
col_go, col_avoid = st.columns(2)
with col_go:
    if worst_level in ("none", "low"):
        st.success(f"**Should you go outside?**\n\n{go_out}")
    elif worst_level == "moderate":
        st.warning(f"**Should you go outside?**\n\n{go_out}")
    else:
        st.error(f"**Should you go outside?**\n\n{go_out}")
with col_avoid:
    st.info(f"**Best & worst times today**\n\n{avoid}")
 
for pollen in selected_pollens:
    level = pollen_levels[pollen]
    msg = advice_text(level, pollen)
    if level in ("none", "low"):
        st.success(msg)
    elif level == "moderate":
        st.warning(msg)
    else:
        st.error(msg)
 
st.divider()
 
# ── Forecast chart ─────────────────────────────────────────────────────────────
st.subheader("5-Day Pollen Forecast")
 
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
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=10, r=10, t=40, b=10),
    height=360,
)
st.plotly_chart(fig, use_container_width=True)
 
# ── 5-day daily summary ────────────────────────────────────────────────────────
st.subheader("Daily Peak Forecast")
df["date"] = df["time"].dt.date
daily_rows = []
for d in sorted(df["date"].unique()):
    day_data = df[df["date"] == d]
    row = {"Date": pd.Timestamp(d).strftime("%a %d %b")}
    for pollen in selected_pollens:
        api_key = POLLEN_PARAMS[pollen]["api"]
        if api_key in day_data.columns:
            peak = pd.to_numeric(day_data[api_key], errors="coerce").max()
            lv = get_level(peak, THRESHOLDS[pollen], mult)
            row[pollen] = f"{level_emoji(lv)} {peak:.0f} gr/m³" if not np.isnan(peak) else "N/A"
        else:
            row[pollen] = "N/A"
    daily_rows.append(row)
 
st.dataframe(pd.DataFrame(daily_rows).set_index("Date"), use_container_width=True)
 
st.divider()
 
# ── Switzerland map ────────────────────────────────────────────────────────────
st.subheader("Switzerland Pollen Map")
 
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
 
def build_map():
    m = folium.Map(
        location=[46.8, 8.2], zoom_start=8,
        tiles="CartoDB positron", control_scale=True,
    )
    heat_pts = []
    for city, info in STATIONS.items():
        city_vals = all_data.get(city, {})
        total = 0.0
        worst = "none"
        for pollen in selected_pollens:
            api_key = POLLEN_PARAMS[pollen]["api"]
            val = city_vals.get(api_key, 0.0)
            total += val
            lv = get_level(val, THRESHOLDS[pollen], mult)
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
        gradient={"0.0": "#2d6a4f", "0.35": "#B8935A",
                  "0.65": "#C4532A", "1.0": "#5b21b6"},
    ).add_to(m)
 
    folium.Marker(
        [home["lat"], home["lon"]],
        tooltip=f"📍 {selected_city}",
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)
    return m
 
st_folium(build_map(), height=460, use_container_width=True)
 
st.divider()
 
# ── Nearby pharmacies & doctors ───────────────────────────────────────────────
st.subheader("Nearby Pharmacies & Doctors")
st.caption(f"Showing results near {selected_city} — data from OpenStreetMap")
 
@st.cache_data(ttl=86400)
def fetch_nearby(lat: float, lon: float, radius_m: int = 2000) -> list:
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
      node["amenity"="doctors"](around:{radius_m},{lat},{lon});
      node["amenity"="clinic"](around:{radius_m},{lat},{lon});
    );
    out body;
    """
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data=query, timeout=25
        )
        r.raise_for_status()
        return r.json().get("elements", [])
    except Exception:
        return []
 
with st.spinner("Finding nearby pharmacies and doctors…"):
    nearby = fetch_nearby(home["lat"], home["lon"])
 
if not nearby:
    st.info("No pharmacies or doctors found nearby. Try a different city.")
else:
    icons = {
        "pharmacy": ("green", "plus"),
        "doctors":  ("blue",  "user-md"),
        "clinic":   ("blue",  "user-md"),
    }
 
    m2 = folium.Map(
        location=[home["lat"], home["lon"]], zoom_start=14,
        tiles="CartoDB positron", control_scale=True,
    )
 
    # Home marker
    folium.Marker(
        [home["lat"], home["lon"]],
        tooltip=f"📍 {selected_city}",
        icon=folium.Icon(color="red", icon="home", prefix="fa"),
    ).add_to(m2)
 
    for place in nearby:
        amenity = place.get("tags", {}).get("amenity", "pharmacy")
        name = place.get("tags", {}).get("name", amenity.capitalize())
        address = place.get("tags", {}).get("addr:street", "")
        phone = place.get("tags", {}).get("phone", "")
        popup_text = f"<b>{name}</b><br>{amenity.capitalize()}"
        if address:
            popup_text += f"<br>{address}"
        if phone:
            popup_text += f"<br>📞 {phone}"
        color, icon = icons.get(amenity, ("green", "plus"))
        folium.Marker(
            location=[place["lat"], place["lon"]],
            tooltip=name,
            popup=folium.Popup(popup_text, max_width=200),
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(m2)
 
    st_folium(m2, height=420, use_container_width=True)
 
    # Summary counts
    n_pharmacy = sum(1 for p in nearby if p.get("tags", {}).get("amenity") == "pharmacy")
    n_doctors  = sum(1 for p in nearby if p.get("tags", {}).get("amenity") in ("doctors", "clinic"))
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("💊 Pharmacies nearby", n_pharmacy)
    with col_b:
        st.metric("🩺 Doctors / Clinics nearby", n_doctors)
 
st.divider()
 
# ── City comparison ────────────────────────────────────────────────────────────
st.subheader("All Cities — Today's Peak")
 
cities = list(all_data.keys())
fig2 = go.Figure()
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    vals = [all_data.get(city, {}).get(api_key, 0.0) for city in cities]
    fig2.add_trace(go.Bar(
        name=pollen, x=cities, y=vals,
        marker_color=POLLEN_PARAMS[pollen]["color"], opacity=0.85,
    ))
 
fig2.update_layout(
    barmode="group",
    xaxis=dict(tickangle=-35, gridcolor="#f0f0f0"),
    yaxis=dict(title="Pollen peak (gr/m³)", gridcolor="#f0f0f0"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=10, r=10, t=30, b=90),
    height=380,
)
st.plotly_chart(fig2, use_container_width=True)
 
# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🌿 BlessYou · Pollen data: Open-Meteo Air Quality API · "
)
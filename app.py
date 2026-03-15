import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime, timedelta
 
# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PollenCH · Switzerland Pollen Alert",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f2eb; color: #1a1a1a; }
[data-testid="stSidebar"] { background: #1c2b1c !important; }
[data-testid="stSidebar"] * { color: #d4e8d4 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #a8cca8 !important; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 0.08em;
}
.app-header {
    background: #1c2b1c; padding: 2.5rem 2rem 2rem;
    border-radius: 0 0 2rem 2rem; margin: -1rem -1rem 2rem -1rem; text-align: center;
}
.app-title { font-family:'Syne',sans-serif; font-size:3rem; font-weight:800;
    color:#e8f5e8; letter-spacing:-0.02em; margin:0; line-height:1; }
.app-title span { color:#6dbf6d; }
.app-subtitle { font-size:0.9rem; color:#7aaa7a; margin-top:0.4rem;
    letter-spacing:0.05em; text-transform:uppercase; }
.stat-card { background:white; border-radius:1rem; padding:1.2rem; text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.06); border:1px solid #e8e8e8; margin-bottom:0.5rem; }
.stat-card .value { font-family:'Syne',sans-serif; font-size:2rem; font-weight:700; line-height:1; }
.stat-card .label { font-size:0.75rem; text-transform:uppercase;
    letter-spacing:0.08em; color:#777; margin-top:0.3rem; }
.section-title { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700;
    color:#1c2b1c; margin:1.5rem 0 0.8rem; padding-bottom:0.4rem;
    border-bottom:2px solid #c5dfc5; }
.alert-card { border-radius:1rem; padding:1.2rem 1.5rem; margin-bottom:0.8rem;
    font-size:0.95rem; font-weight:500; border-left:5px solid; }
.alert-none     { background:#f5f5f5; border-color:#9e9e9e; color:#424242; }
.alert-low      { background:#e8f5e8; border-color:#4caf50; color:#1b5e20; }
.alert-moderate { background:#fff8e1; border-color:#ff9800; color:#e65100; }
.alert-high     { background:#fce4ec; border-color:#e53935; color:#b71c1c; }
.alert-vhigh    { background:#f3e5f5; border-color:#8e24aa; color:#4a148c; }
.advice-block { background:white; border-radius:1rem; padding:1.5rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.06); border:1px solid #e8e8e8; }
.advice-block h4 { font-family:'Syne',sans-serif; color:#1c2b1c; margin:0 0 0.8rem; }
.stButton > button { background:#2e5c2e !important; color:white !important;
    border:none !important; border-radius:0.6rem !important;
    font-family:'Syne',sans-serif !important; font-weight:600 !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
# ── Constants ──────────────────────────────────────────────────────────────────
STATIONS = {
    "Zürich":       {"canton":"ZH","lat":47.376,"lon":8.538},
    "Bern":         {"canton":"BE","lat":46.948,"lon":7.447},
    "Basel":        {"canton":"BS","lat":47.560,"lon":7.589},
    "Geneva":       {"canton":"GE","lat":46.204,"lon":6.143},
    "Lausanne":     {"canton":"VD","lat":46.519,"lon":6.633},
    "Luzern":       {"canton":"LU","lat":47.050,"lon":8.309},
    "St. Gallen":   {"canton":"SG","lat":47.422,"lon":9.369},
    "Lugano":       {"canton":"TI","lat":46.004,"lon":8.960},
    "Sion":         {"canton":"VS","lat":46.233,"lon":7.360},
    "Davos":        {"canton":"GR","lat":46.813,"lon":9.844},
    "Neuchâtel":    {"canton":"NE","lat":47.000,"lon":6.944},
    "Aarau":        {"canton":"AG","lat":47.392,"lon":8.044},
    "Chur":         {"canton":"GR","lat":46.852,"lon":9.533},
    "Frauenfeld":   {"canton":"TG","lat":47.556,"lon":8.898},
    "Bellinzona":   {"canton":"TI","lat":46.193,"lon":9.023},
}
 
# Open-Meteo Air Quality API variable names
POLLEN_PARAMS = {
    "Birch (Birke)":     {"api":"birch_pollen",   "color":"#e74c3c","season":"Mar–May"},
    "Grass (Gräser)":    {"api":"grass_pollen",   "color":"#27ae60","season":"May–Aug"},
    "Mugwort (Beifuss)": {"api":"mugwort_pollen", "color":"#8e44ad","season":"Jul–Sep"},
    "Hazel (Hasel)":     {"api":"alder_pollen",   "color":"#f39c12","season":"Jan–Mar"},
    "Alder (Erle)":      {"api":"alder_pollen",   "color":"#2980b9","season":"Feb–Apr"},
}
 
# Thresholds in grains/m³
THRESHOLDS = {
    "Birch (Birke)":     [1, 10,  50, 200],
    "Grass (Gräser)":    [1, 10,  50, 200],
    "Mugwort (Beifuss)": [1,  5,  20,  80],
    "Hazel (Hasel)":     [1, 10,  50, 150],
    "Alder (Erle)":      [1, 10,  50, 150],
}
 
LEVEL_ORDER = ["none","low","moderate","high","very high"]
 
# ── Data fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_pollen(lat: float, lon: float, pollen_vars: list) -> dict | None:
    """
    Fetch hourly pollen forecast from Open-Meteo Air Quality API.
    Returns dict with 'time' and one key per pollen variable.
    Free, no API key needed, works globally.
    """
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
        data = r.json()
        return data.get("hourly", None)
    except Exception as e:
        return None
 
# ── Helpers ────────────────────────────────────────────────────────────────────
def sensitivity_mult(sensitivity):
    return {"Low (mild symptoms)":0.5,
            "Medium (moderate symptoms)":1.0,
            "High (severe symptoms)":1.5}[sensitivity]
 
def get_level(value, thresholds, mult=1.0):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "none"
    v = float(value) * mult
    if v < thresholds[0]: return "none"
    elif v < thresholds[1]: return "low"
    elif v < thresholds[2]: return "moderate"
    elif v < thresholds[3]: return "high"
    else: return "very high"
 
def level_color(level):
    return {"none":"#9e9e9e","low":"#4caf50","moderate":"#ff9800",
            "high":"#e53935","very high":"#8e24aa"}.get(level,"#9e9e9e")
 
def level_emoji(level):
    return {"none":"⚪","low":"🟢","moderate":"🟡",
            "high":"🔴","very high":"🟣"}.get(level,"⚪")
 
def advice_text(level, pollen_name):
    return {
        "none":     f"✅ No significant {pollen_name} detected. Safe to go outside.",
        "low":      f"🟢 Low {pollen_name}. Fine for most people. Consider antihistamines if sensitive.",
        "moderate": f"🟡 Moderate {pollen_name}. Keep windows closed 06–10h. Pre-medicate before going out.",
        "high":     f"🔴 High {pollen_name}! Limit outdoor time, especially mornings. Shower after being outside.",
        "very high":f"🟣 Very high {pollen_name}! Stay indoors if possible. Use air purifiers and take medication.",
    }.get(level,"")
 
def best_time_advice(level):
    if level in ("none","low"):
        return "✅ Any time of day is fine.", "💡 Afternoon is slightly better — pollen disperses more after midday."
    elif level == "moderate":
        return "🕒 Best: afternoon (14–18h) or after rain.", "⚠️ Avoid mornings (06–10h) — peak dispersal time."
    elif level == "high":
        return "🌧️ Best: during or right after rain.", "⛔ Avoid mornings entirely. Evenings (after 19h) are safer."
    else:
        return "🏠 Recommend staying indoors today.", "⛔ All outdoor activities carry high risk."
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 PollenCH Settings")
    st.markdown("---")
    selected_pollens = st.multiselect(
        "Your pollen allergies",
        options=list(POLLEN_PARAMS.keys()),
        default=["Birch (Birke)", "Grass (Gräser)"],
    )
    sensitivity = st.select_slider(
        "Your sensitivity level",
        options=["Low (mild symptoms)","Medium (moderate symptoms)","High (severe symptoms)"],
        value="Medium (moderate symptoms)",
    )
    selected_city = st.selectbox(
        "Your location",
        options=list(STATIONS.keys()),
        index=0,
    )
    st.markdown("---")
    load_btn = st.button("🔄 Refresh Data", use_container_width=True)
    st.markdown("**Data:** Open-Meteo Air Quality API  \n**Source:** CAMS European forecast  \n**Update:** Every 24h · 5-day forecast  \n**No API key needed** ✅")
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">Pollen<span>CH</span></div>
  <div class="app-subtitle">Switzerland · Real-time pollen forecast</div>
</div>
""", unsafe_allow_html=True)
 
if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()
 
if load_btn:
    st.cache_data.clear()
 
# ── Fetch home city data ───────────────────────────────────────────────────────
home = STATIONS[selected_city]
mult = sensitivity_mult(sensitivity)
api_vars = list({POLLEN_PARAMS[p]["api"] for p in selected_pollens})
 
with st.spinner(f"Loading pollen forecast for {selected_city}…"):
    hourly = fetch_pollen(home["lat"], home["lon"], api_vars)
 
if not hourly:
    st.error("❌ Could not load pollen data from Open-Meteo. Check your internet connection.")
    st.stop()
 
# Parse into DataFrame
df = pd.DataFrame(hourly)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)
 
# Get today's max value per pollen
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
st.markdown(f"<div class='section-title'>📍 Today in {selected_city} — {today.strftime('%A %d %B %Y')}</div>", unsafe_allow_html=True)
 
cols = st.columns(len(selected_pollens))
for i, pollen in enumerate(selected_pollens):
    val = today_vals.get(pollen, np.nan)
    level = get_level(val, THRESHOLDS[pollen], mult)
    color = level_color(level)
    display_val = f"{val:.0f}" if not np.isnan(val) else "N/A"
    unit = " gr/m³" if not np.isnan(val) else ""
    with cols[i]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="value" style="color:{color}">{level_emoji(level)} {display_val}{unit}</div>
            <div class="label">{pollen}</div>
            <div style="font-size:0.8rem;color:{color};font-weight:600;margin-top:0.3rem">{level.upper()}</div>
            <div style="font-size:0.7rem;color:#999;margin-top:0.2rem">Season: {POLLEN_PARAMS[pollen]['season']}</div>
        </div>
        """, unsafe_allow_html=True)
 
# ── Daily advice ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>💡 Your Daily Advice</div>", unsafe_allow_html=True)
 
worst_level = "none"
for pollen in selected_pollens:
    lv = get_level(today_vals.get(pollen, np.nan), THRESHOLDS[pollen], mult)
    if LEVEL_ORDER.index(lv) > LEVEL_ORDER.index(worst_level):
        worst_level = lv
 
go_out, avoid = best_time_advice(worst_level)
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="advice-block"><h4>🚪 Should you go outside?</h4><p style="margin:0">{go_out}</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="advice-block"><h4>⏰ Best/Worst times today</h4><p style="margin:0">{avoid}</p></div>', unsafe_allow_html=True)
 
st.markdown("")
for pollen in selected_pollens:
    level = get_level(today_vals.get(pollen, np.nan), THRESHOLDS[pollen], mult)
    cls = {"none":"alert-none","low":"alert-low","moderate":"alert-moderate",
           "high":"alert-high","very high":"alert-vhigh"}.get(level,"alert-none")
    st.markdown(f'<div class="alert-card {cls}">{advice_text(level, pollen)}</div>', unsafe_allow_html=True)
 
# ── Forecast chart ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>📈 5-Day Pollen Forecast</div>", unsafe_allow_html=True)
 
fig = go.Figure()
for pollen in selected_pollens:
    api_key = POLLEN_PARAMS[pollen]["api"]
    if api_key not in df.columns:
        continue
    vals = pd.to_numeric(df[api_key], errors="coerce").clip(lower=0)
    clr = POLLEN_PARAMS[pollen]["color"]
    r,g,b = int(clr[1:3],16),int(clr[3:5],16),int(clr[5:7],16)
    fig.add_trace(go.Scatter(
        x=df["time"], y=vals, name=pollen,
        line=dict(color=clr, width=2.5),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.1)",
        mode="lines",
    ))
 
# Add today marker
now = datetime.now()
fig.add_vline(x=now.timestamp()*1000, line_dash="dash", line_color="#666", annotation_text="Now",
              annotation_position="top right")
 
# Risk bands
t = THRESHOLDS[selected_pollens[0]]
fig.add_hrect(y0=0,    y1=t[0], fillcolor="#4caf50", opacity=0.04, line_width=0)
fig.add_hrect(y0=t[0], y1=t[1], fillcolor="#ffeb3b", opacity=0.05, line_width=0)
fig.add_hrect(y0=t[1], y1=t[2], fillcolor="#ff9800", opacity=0.05, line_width=0)
fig.add_hrect(y0=t[2], y1=t[3], fillcolor="#e53935", opacity=0.05, line_width=0)
 
fig.update_layout(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Inter", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(title="", gridcolor="#f0f0f0"),
    yaxis=dict(title="Pollen (grains/m³)", gridcolor="#f0f0f0"),
    margin=dict(l=10,r=10,t=40,b=10), height=360,
)
st.plotly_chart(fig, use_container_width=True)
 
# ── 5-day daily summary table ──────────────────────────────────────────────────
st.markdown("**Daily peak forecast**")
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
 
# ── Switzerland map ────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🗺️ Switzerland Pollen Map</div>", unsafe_allow_html=True)
st.info("💡 Loading data for all 15 Swiss cities — this takes a few seconds.", icon="ℹ️")
 
@st.cache_data(ttl=3600)
def fetch_all_stations(pollen_vars: tuple) -> dict:
    """Fetch today's peak pollen for all Swiss stations."""
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
 
# Build map
tab1, tab2 = st.tabs(["🌡️ Heatmap", "📍 Risk Dots"])
 
def build_map(mode="heat"):
    m = folium.Map(location=[46.8,8.2], zoom_start=8,
                   tiles="CartoDB positron", control_scale=True)
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
        popup_html = (f"<div style='font-family:sans-serif'>"
                      f"<b>{city}</b> ({info['canton']})<br>"
                      f"<b style='color:{clr}'>{worst.upper()}</b><br>"
                      f"Combined: {total:.0f} gr/m³</div>")
        folium.CircleMarker(
            location=[info["lat"], info["lon"]], radius=13,
            color="white", weight=2, fill=True,
            fill_color=clr, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {worst}",
        ).add_to(m)
 
    if mode == "heat":
        HeatMap(heat_pts, radius=55, blur=40, min_opacity=0.3,
                gradient={"0.0":"#4caf50","0.35":"#ffeb3b",
                          "0.65":"#ff9800","1.0":"#e53935"}).add_to(m)
 
    # Home marker
    folium.Marker(
        [home["lat"], home["lon"]], tooltip=f"📍 {selected_city}",
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)
    return m
 
with tab1:
    st_folium(build_map("heat"), height=460, use_container_width=True)
with tab2:
    st_folium(build_map("dots"), height=460, use_container_width=True)
 
# ── All cities comparison bar chart ───────────────────────────────────────────
st.markdown("<div class='section-title'>🏔️ All Cities Comparison — Today's Peak</div>", unsafe_allow_html=True)
 
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
    barmode="group", paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Inter", size=11),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(tickangle=-35, gridcolor="#f0f0f0"),
    yaxis=dict(title="Pollen peak (gr/m³)", gridcolor="#f0f0f0"),
    margin=dict(l=10,r=10,t=30,b=90), height=380,
)
st.plotly_chart(fig2, use_container_width=True)
 
# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.78rem;padding:0.5rem'>"
    "Pollen data: <a href='https://open-meteo.com' style='color:#4caf50'>Open-Meteo Air Quality API</a> · "
    "Source: CAMS European Air Quality Forecast · "
    "Free, no API key · Not a substitute for medical advice"
    "</div>", unsafe_allow_html=True,
)
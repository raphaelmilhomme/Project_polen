import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
 
# ── Page config ───────────────────────────────────────────────────────────────
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
 
.stApp {
    background: #f5f2eb;
    color: #1a1a1a;
}
 
[data-testid="stSidebar"] {
    background: #1c2b1c !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #d4e8d4 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label { color: #a8cca8 !important; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; }
 
.app-header {
    background: #1c2b1c;
    padding: 2.5rem 2rem 2rem;
    border-radius: 0 0 2rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
}
.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #e8f5e8;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1;
}
.app-title span { color: #6dbf6d; }
.app-subtitle {
    font-size: 0.9rem;
    color: #7aaa7a;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
 
.alert-card {
    border-radius: 1rem;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    border-left: 5px solid;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.alert-low    { background:#e8f5e8; border-color:#4caf50; color:#1b5e20; }
.alert-moderate { background:#fff8e1; border-color:#ff9800; color:#e65100; }
.alert-high   { background:#fce4ec; border-color:#e53935; color:#b71c1c; }
.alert-vhigh  { background:#f3e5f5; border-color:#8e24aa; color:#4a148c; }
.alert-none   { background:#f5f5f5; border-color:#9e9e9e; color:#424242; }
 
.stat-card {
    background: white;
    border-radius: 1rem;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8e8e8;
}
.stat-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}
.stat-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #777;
    margin-top: 0.3rem;
}
 
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #1c2b1c;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #c5dfc5;
}
 
.advice-block {
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8e8e8;
}
.advice-block h4 {
    font-family: 'Syne', sans-serif;
    color: #1c2b1c;
    margin: 0 0 0.8rem;
    font-size: 1rem;
}
 
.stButton > button {
    background: #2e5c2e !important;
    color: white !important;
    border: none !important;
    border-radius: 0.6rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover { background: #3a7a3a !important; }
 
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
# ── Constants ─────────────────────────────────────────────────────────────────
STATIONS = {
    "BAS": {"name": "Basel",          "canton": "BS", "lat": 47.541, "lon": 7.588},
    "BER": {"name": "Bern/Zollikofen","canton": "BE", "lat": 46.991, "lon": 7.467},
    "BUE": {"name": "Buchs/Aarau",    "canton": "AG", "lat": 47.387, "lon": 8.073},
    "DAV": {"name": "Davos",          "canton": "GR", "lat": 46.813, "lon": 9.844},
    "GEN": {"name": "Genève/Cointrin","canton": "GE", "lat": 46.238, "lon": 6.108},
    "LAE": {"name": "Laegern",        "canton": "AG", "lat": 47.482, "lon": 8.398},
    "LAU": {"name": "Lausanne",       "canton": "VD", "lat": 46.537, "lon": 6.613},
    "LUG": {"name": "Lugano",         "canton": "TI", "lat": 46.004, "lon": 8.960},
    "LUZ": {"name": "Luzern",         "canton": "LU", "lat": 47.036, "lon": 8.301},
    "NEU": {"name": "Neuchâtel",      "canton": "NE", "lat": 46.998, "lon": 6.957},
    "PAY": {"name": "Payerne",        "canton": "VD", "lat": 46.812, "lon": 6.944},
    "PBS": {"name": "Pully/Lausanne", "canton": "VD", "lat": 46.509, "lon": 6.659},
    "SIO": {"name": "Sion",           "canton": "VS", "lat": 46.217, "lon": 7.340},
    "STG": {"name": "St. Gallen",     "canton": "SG", "lat": 47.430, "lon": 9.400},
    "VIT": {"name": "Visp",           "canton": "VS", "lat": 46.295, "lon": 7.883},
    "ZUE": {"name": "Zürich",         "canton": "ZH", "lat": 47.376, "lon": 8.538},
}
 
# Pollen parameter codes in MeteoSwiss CSV
POLLEN_PARAMS = {
    "Birch (Birke)":    {"code": "BETU", "color": "#e74c3c", "season": "Mar–May"},
    "Grass (Gräser)":   {"code": "POAC", "color": "#27ae60", "season": "May–Aug"},
    "Mugwort (Beifuss)":{"code": "ARTV", "color": "#8e44ad", "season": "Jul–Sep"},
    "Hazel (Hasel)":    {"code": "CORY", "color": "#f39c12", "season": "Jan–Mar"},
    "Alder (Erle)":     {"code": "ALNU", "color": "#2980b9", "season": "Feb–Apr"},
}
 
# Risk thresholds (grains/m³)
THRESHOLDS = {
    "Birch (Birke)":    [1, 10,  50,  200],
    "Grass (Gräser)":   [1, 10,  50,  200],
    "Mugwort (Beifuss)":[1,  5,  20,   80],
    "Hazel (Hasel)":    [1, 10,  50,  150],
    "Alder (Erle)":     [1, 10,  50,  150],
}
 
BASE_URL = "https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen"
 
# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_station_data(station_id: str) -> pd.DataFrame | None:
    """Fetch recent daily pollen data for a station.
    
    MeteoSwiss URL pattern:
    https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/{sid}/ogd-pollen_{sid}_d_recent.csv
    """
    sid = station_id.lower()
    url = f"{BASE_URL}/{sid}/ogd-pollen_{sid}_d_recent.csv"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            # Try uppercase station subfolder as fallback
            url2 = f"{BASE_URL}/{station_id}/ogd-pollen_{sid}_d_recent.csv"
            r = requests.get(url2, timeout=15)
            if r.status_code != 200:
                return None
        # MeteoSwiss CSVs: semicolon separated, may have metadata header rows
        # Try reading with different skiprow values
        raw = r.text
        lines = raw.splitlines()
        # Find the header row (contains 'reference_timestamp' or 'station_abbr' or date-like)
        header_idx = 0
        for i, line in enumerate(lines[:10]):
            if "timestamp" in line.lower() or "station" in line.lower() or "date" in line.lower():
                header_idx = i
                break
        df = pd.read_csv(io.StringIO(raw), sep=";", skiprows=header_idx, on_bad_lines="skip")
        if df.empty:
            return None
        # Detect date column
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
        df = df.dropna(subset=[date_col])
        df = df.rename(columns={date_col: "date"})
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception:
        return None
 
def get_level(value, thresholds):
    if pd.isna(value) or value < 0:
        return "none"
    if value < thresholds[0]:
        return "none"
    elif value < thresholds[1]:
        return "low"
    elif value < thresholds[2]:
        return "moderate"
    elif value < thresholds[3]:
        return "high"
    else:
        return "very high"
 
def level_color(level):
    return {"none":"#9e9e9e","low":"#4caf50","moderate":"#ff9800",
            "high":"#e53935","very high":"#8e24aa"}.get(level,"#9e9e9e")
 
def level_emoji(level):
    return {"none":"⚪","low":"🟢","moderate":"🟡",
            "high":"🔴","very high":"🟣"}.get(level,"⚪")
 
def sensitivity_multiplier(sensitivity):
    return {"Low (mild symptoms)": 0.5,
            "Medium (moderate symptoms)": 1.0,
            "High (severe symptoms)": 1.5}[sensitivity]
 
def get_user_level(value, thresholds, sensitivity):
    if pd.isna(value) or value < 0:
        return "none"
    adjusted = value * sensitivity_multiplier(sensitivity)
    if adjusted < thresholds[0]:
        return "none"
    elif adjusted < thresholds[1]:
        return "low"
    elif adjusted < thresholds[2]:
        return "moderate"
    elif adjusted < thresholds[3]:
        return "high"
    else:
        return "very high"
 
def advice_text(level, pollen_name, sensitivity):
    if level == "none":
        return "✅ No significant pollen detected. Safe to go outside."
    elif level == "low":
        return f"🟢 Low {pollen_name} levels. Outdoor activities generally fine. Consider taking antihistamines if you're sensitive."
    elif level == "moderate":
        return f"🟡 Moderate {pollen_name} pollen. Keep windows closed in the morning (peak dispersal 06:00–10:00). Pre-medicate before going out."
    elif level == "high":
        return f"🔴 High {pollen_name} pollen. Limit time outdoors especially in the morning. Wear sunglasses. Shower after being outside."
    else:
        return f"🟣 Very high {pollen_name} pollen! Stay indoors if possible. Use air purifiers. Take prescribed medication."
 
def best_time_advice(level):
    if level in ("none", "low"):
        return "Any time of day is fine.", "Afternoon (14:00–18:00) is typically best — pollen levels slightly lower after midday dispersal."
    elif level == "moderate":
        return "🕒 Best time: afternoon (14:00–18:00) or after rain.", "☀️ Avoid mornings (06:00–10:00) when pollen counts peak."
    elif level == "high":
        return "🌧️ Best time: during or right after rain (pollen washed from air).", "⛔ Avoid mornings entirely. If you must go out, evenings (after 19:00) are safer."
    else:
        return "🏠 Recommend staying indoors all day.", "⛔ All outdoor activities carry high risk today."
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
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
        options=["Low (mild symptoms)", "Medium (moderate symptoms)", "High (severe symptoms)"],
        value="Medium (moderate symptoms)",
    )
 
    selected_station = st.selectbox(
        "Your location (nearest station)",
        options=list(STATIONS.keys()),
        format_func=lambda x: f"{STATIONS[x]['name']} ({STATIONS[x]['canton']})",
        index=list(STATIONS.keys()).index("ZUE"),
    )
 
    st.markdown("---")
    st.markdown("**Data source:** MeteoSwiss OGD  \n**Update:** Hourly (daily aggregated)  \n**Coverage:** 16 stations CH")
    st.markdown("---")
    load_btn = st.button("🔄 Refresh Data", use_container_width=True)
 
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">Pollen<span>CH</span></div>
  <div class="app-subtitle">Switzerland · Real-time pollen monitoring</div>
</div>
""", unsafe_allow_html=True)
 
if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()
 
# ── Load data ─────────────────────────────────────────────────────────────────
if load_btn:
    st.cache_data.clear()
 
with st.spinner("Loading MeteoSwiss pollen data…"):
    station_dfs = {}
    for sid in STATIONS:
        df = fetch_station_data(sid)
        if df is not None:
            station_dfs[sid] = df
 
if not station_dfs:
    st.error("Could not load MeteoSwiss data. Please try again later.")
    test_sid = list(STATIONS.keys())[0].lower()
    st.code(f"URL tried: https://data.geo.admin.ch/ch.meteoschweiz.ogd-pollen/{test_sid}/ogd-pollen_{test_sid}_d_recent.csv")
    st.info("Paste that URL in your browser. If it downloads a CSV, the issue is your network/firewall blocking Streamlit outbound requests.")
    st.stop()
 
with st.expander("🔧 Debug info (expand if something looks wrong)"):
    st.write(f"Loaded **{len(station_dfs)}/16** stations successfully.")
    for sid, df in list(station_dfs.items())[:3]:
        st.write(f"**{sid}** — {len(df)} rows | columns: {list(df.columns[:8])}")
 
home_df = station_dfs.get(selected_station)
home_info = STATIONS[selected_station]
 
# ── Today's overview for home station ────────────────────────────────────────
st.markdown(f"<div class='section-title'>📍 Today at {home_info['name']}</div>", unsafe_allow_html=True)
 
today_vals = {}
if home_df is not None:
    latest = home_df.iloc[-1]
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        # find matching column (case insensitive)
        col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
        if col:
            today_vals[pollen] = latest[col]
        else:
            today_vals[pollen] = np.nan
 
cols = st.columns(max(len(selected_pollens), 1))
for i, pollen in enumerate(selected_pollens):
    val = today_vals.get(pollen, np.nan)
    thresh = THRESHOLDS[pollen]
    level = get_user_level(val, thresh, sensitivity)
    color = level_color(level)
    emoji = level_emoji(level)
    with cols[i]:
        display_val = f"{val:.0f}" if not pd.isna(val) else "N/A"
        unit = " gr/m³" if not pd.isna(val) else ""
        st.markdown(f"""
        <div class="stat-card">
            <div class="value" style="color:{color}">{emoji} {display_val}{unit}</div>
            <div class="label">{pollen}</div>
            <div style="font-size:0.8rem;color:{color};font-weight:600;margin-top:0.3rem">{level.upper()}</div>
            <div style="font-size:0.7rem;color:#999;margin-top:0.2rem">Season: {POLLEN_PARAMS[pollen]['season']}</div>
        </div>
        """, unsafe_allow_html=True)
 
# ── Personal advice block ─────────────────────────────────────────────────────
st.markdown("<div class='section-title'>💡 Your Daily Advice</div>", unsafe_allow_html=True)
 
worst_level_order = ["none","low","moderate","high","very high"]
worst_pollen = None
worst_level = "none"
for pollen in selected_pollens:
    val = today_vals.get(pollen, np.nan)
    level = get_user_level(val, THRESHOLDS[pollen], sensitivity)
    if worst_level_order.index(level) > worst_level_order.index(worst_level):
        worst_level = level
        worst_pollen = pollen
 
go_out, avoid = best_time_advice(worst_level)
 
adv_col1, adv_col2 = st.columns(2)
with adv_col1:
    st.markdown(f"""
    <div class="advice-block">
        <h4>🚪 Should you go outside?</h4>
        <p style="margin:0;font-size:0.95rem;">{go_out}</p>
    </div>
    """, unsafe_allow_html=True)
with adv_col2:
    st.markdown(f"""
    <div class="advice-block">
        <h4>⏰ Best/Worst times today</h4>
        <p style="margin:0;font-size:0.95rem;">{avoid}</p>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown("")
for pollen in selected_pollens:
    val = today_vals.get(pollen, np.nan)
    level = get_user_level(val, THRESHOLDS[pollen], sensitivity)
    cls_map = {"none":"alert-none","low":"alert-low","moderate":"alert-moderate",
               "high":"alert-high","very high":"alert-high"}
    cls = cls_map.get(level, "alert-none")
    adv = advice_text(level, pollen, sensitivity)
    st.markdown(f'<div class="alert-card {cls}">{adv}</div>', unsafe_allow_html=True)
 
# ── Map ────────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🗺️ Switzerland Pollen Map</div>", unsafe_allow_html=True)
 
map_tab1, map_tab2 = st.tabs(["🌡️ Heatmap", "🏔️ Cantons (Station dots)"])
 
# Collect latest values for all stations
map_data = []
for sid, sinfo in STATIONS.items():
    df = station_dfs.get(sid)
    if df is None:
        continue
    latest = df.iloc[-1]
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        col = next((c for c in df.columns if code.upper() in c.upper()), None)
        val = float(latest[col]) if col and not pd.isna(latest[col]) else 0.0
        level = get_user_level(val, THRESHOLDS[pollen], sensitivity)
        map_data.append({
            "station": sid,
            "name": sinfo["name"],
            "canton": sinfo["canton"],
            "lat": sinfo["lat"],
            "lon": sinfo["lon"],
            "pollen": pollen,
            "value": max(val, 0),
            "level": level,
            "color": level_color(level),
        })
 
map_df = pd.DataFrame(map_data)
 
def build_map(mode="heat"):
    m = folium.Map(
        location=[46.8, 8.2],
        zoom_start=8,
        tiles="CartoDB positron",
        control_scale=True,
    )
    if map_df.empty:
        return m
 
    # Aggregate across selected pollens (worst level per station)
    agg = map_df.groupby(["station","name","canton","lat","lon"]).agg(
        total_value=("value","sum"),
        worst_level=("level", lambda x: sorted(x, key=lambda l: worst_level_order.index(l))[-1])
    ).reset_index()
 
    if mode == "heat":
        heat_data = [[r.lat, r.lon, min(r.total_value, 500)] for r in agg.itertuples()]
        HeatMap(
            heat_data,
            radius=60, blur=40, min_opacity=0.3,
            gradient={"0.0":"#4caf50","0.3":"#ffeb3b","0.6":"#ff9800","1.0":"#e53935"},
        ).add_to(m)
 
    for r in agg.itertuples():
        clr = level_color(r.worst_level)
        popup_html = f"""
        <div style='font-family:sans-serif;min-width:160px'>
          <b style='font-size:1rem'>{r.name}</b><br>
          <span style='color:#777;font-size:0.8rem'>Canton {r.canton}</span><br><hr style='margin:4px 0'>
          <b style='color:{clr}'>{r.worst_level.upper()}</b> overall<br>
          <span style='font-size:0.8rem'>Combined: {r.total_value:.0f} gr/m³</span>
        </div>"""
        folium.CircleMarker(
            location=[r.lat, r.lon],
            radius=14,
            color="white",
            weight=2,
            fill=True,
            fill_color=clr,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{r.name}: {r.worst_level}",
        ).add_to(m)
 
    # Home station marker
    home = STATIONS[selected_station]
    folium.Marker(
        location=[home["lat"], home["lon"]],
        tooltip="📍 Your location",
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)
 
    return m
 
with map_tab1:
    st_folium(build_map("heat"), height=460, use_container_width=True)
with map_tab2:
    st_folium(build_map("dots"), height=460, use_container_width=True)
 
# ── Forecast chart (last 7 days as proxy, since no forecast API) ───────────────
st.markdown("<div class='section-title'>📈 Recent Trend & 5-Day Outlook (Historical Average)</div>", unsafe_allow_html=True)
 
if home_df is not None:
    fig = go.Figure()
    recent = home_df.tail(30)
 
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
        if not col:
            continue
        vals = pd.to_numeric(recent[col], errors="coerce").clip(lower=0)
        color = POLLEN_PARAMS[pollen]["color"]
 
        fig.add_trace(go.Scatter(
            x=recent["date"],
            y=vals,
            name=pollen,
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=color.replace(")", ",0.08)").replace("rgb","rgba") if "rgb" in color else color + "18",
            mode="lines+markers",
            marker=dict(size=5),
        ))
 
    # Add risk threshold bands
    first_thresh = THRESHOLDS[selected_pollens[0]] if selected_pollens else [1,10,50,200]
    fig.add_hrect(y0=0,          y1=first_thresh[0], fillcolor="#4caf50", opacity=0.04, line_width=0)
    fig.add_hrect(y0=first_thresh[0], y1=first_thresh[1], fillcolor="#ffeb3b", opacity=0.06, line_width=0)
    fig.add_hrect(y0=first_thresh[1], y1=first_thresh[2], fillcolor="#ff9800", opacity=0.06, line_width=0)
    fig.add_hrect(y0=first_thresh[2], y1=first_thresh[3], fillcolor="#e53935", opacity=0.06, line_width=0)
 
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Date", gridcolor="#f0f0f0", showgrid=True),
        yaxis=dict(title="Pollen concentration (grains/m³)", gridcolor="#f0f0f0", showgrid=True),
        margin=dict(l=10, r=10, t=40, b=10),
        height=360,
    )
    fig.add_annotation(
        text="Background bands: 🟢 Low  🟡 Moderate  🟠 High  🔴 Very high",
        xref="paper", yref="paper", x=0, y=-0.15,
        showarrow=False, font=dict(size=11, color="#777"),
    )
    st.plotly_chart(fig, use_container_width=True)
 
    # 5-day outlook table using same-week historical average
    st.markdown("**5-day outlook** — based on historical average for this time of year at " + home_info["name"])
    forecast_rows = []
    today = datetime.today()
    doy = today.timetuple().tm_yday
 
    for day_offset in range(1, 6):
        future_date = today + timedelta(days=day_offset)
        row = {"Date": future_date.strftime("%a %d %b")}
        for pollen in selected_pollens:
            code = POLLEN_PARAMS[pollen]["code"]
            col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
            if col:
                # average of same ±7 days in historical data
                home_df["doy"] = home_df["date"].dt.dayofyear
                target_doy = (doy + day_offset) % 365
                window = home_df[abs(home_df["doy"] - target_doy) <= 7]
                avg_val = pd.to_numeric(window[col], errors="coerce").clip(lower=0).mean()
                level = get_user_level(avg_val, THRESHOLDS[pollen], sensitivity)
                emoji = level_emoji(level)
                row[pollen] = f"{emoji} {avg_val:.0f} gr/m³" if not pd.isna(avg_val) else "N/A"
            else:
                row[pollen] = "N/A"
        forecast_rows.append(row)
 
    forecast_df = pd.DataFrame(forecast_rows).set_index("Date")
    st.dataframe(forecast_df, use_container_width=True)
 
# ── All-stations comparison ────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🏔️ All Stations Comparison</div>", unsafe_allow_html=True)
 
if not map_df.empty and selected_pollens:
    pivot = map_df[map_df["pollen"].isin(selected_pollens)].pivot_table(
        index=["name","canton"], columns="pollen", values="value", aggfunc="sum"
    ).reset_index()
 
    fig2 = go.Figure()
    for pollen in selected_pollens:
        if pollen not in pivot.columns:
            continue
        fig2.add_trace(go.Bar(
            name=pollen,
            x=pivot["name"],
            y=pivot[pollen].clip(lower=0),
            marker_color=POLLEN_PARAMS[pollen]["color"],
            opacity=0.85,
        ))
 
    fig2.update_layout(
        barmode="group",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(tickangle=-35, gridcolor="#f0f0f0"),
        yaxis=dict(title="Pollen (gr/m³)", gridcolor="#f0f0f0"),
        margin=dict(l=10, r=10, t=30, b=80),
        height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)
 
# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.78rem;padding:0.5rem'>"
    "Data: <a href='https://www.meteoswiss.admin.ch' style='color:#4caf50'>MeteoSwiss Open Government Data</a> · "
    "16 automatic stations · Licence CC-BY · "
    "Not a substitute for medical advice"
    "</div>",
    unsafe_allow_html=True,
)
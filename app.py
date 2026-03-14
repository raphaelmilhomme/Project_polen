import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import json
 
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
[data-testid="stSidebar"] { background: #1c2b1c !important; border-right: none; }
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
.alert-card { border-radius:1rem; padding:1.2rem 1.5rem; margin-bottom:1rem;
    font-size:1rem; font-weight:500; border-left:5px solid;
    display:flex; align-items:center; gap:0.8rem; }
.alert-low    { background:#e8f5e8; border-color:#4caf50; color:#1b5e20; }
.alert-moderate{ background:#fff8e1; border-color:#ff9800; color:#e65100; }
.alert-high   { background:#fce4ec; border-color:#e53935; color:#b71c1c; }
.alert-vhigh  { background:#f3e5f5; border-color:#8e24aa; color:#4a148c; }
.alert-none   { background:#f5f5f5; border-color:#9e9e9e; color:#424242; }
.stat-card { background:white; border-radius:1rem; padding:1.2rem; text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.06); border:1px solid #e8e8e8; }
.stat-card .value { font-family:'Syne',sans-serif; font-size:2rem; font-weight:700; line-height:1; }
.stat-card .label { font-size:0.75rem; text-transform:uppercase;
    letter-spacing:0.08em; color:#777; margin-top:0.3rem; }
.section-title { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700;
    color:#1c2b1c; margin:1.5rem 0 0.8rem; padding-bottom:0.4rem;
    border-bottom:2px solid #c5dfc5; }
.advice-block { background:white; border-radius:1rem; padding:1.5rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.06); border:1px solid #e8e8e8; }
.advice-block h4 { font-family:'Syne',sans-serif; color:#1c2b1c; margin:0 0 0.8rem; font-size:1rem; }
.stButton > button { background:#2e5c2e !important; color:white !important;
    border:none !important; border-radius:0.6rem !important;
    font-family:'Syne',sans-serif !important; font-weight:600 !important;
    letter-spacing:0.03em !important; padding:0.5rem 1.5rem !important; }
.stButton > button:hover { background:#3a7a3a !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
# ── Constants ──────────────────────────────────────────────────────────────────
STATIONS = {
    "BAS": {"name": "Basel",           "canton": "BS", "lat": 47.541, "lon": 7.588},
    "BER": {"name": "Bern/Zollikofen", "canton": "BE", "lat": 46.991, "lon": 7.467},
    "BUE": {"name": "Buchs/Aarau",     "canton": "AG", "lat": 47.387, "lon": 8.073},
    "DAV": {"name": "Davos",           "canton": "GR", "lat": 46.813, "lon": 9.844},
    "GEN": {"name": "Genève",          "canton": "GE", "lat": 46.238, "lon": 6.108},
    "LAE": {"name": "Laegern",         "canton": "AG", "lat": 47.482, "lon": 8.398},
    "LUG": {"name": "Lugano",          "canton": "TI", "lat": 46.004, "lon": 8.960},
    "LUZ": {"name": "Luzern",          "canton": "LU", "lat": 47.036, "lon": 8.301},
    "NEU": {"name": "Neuchâtel",       "canton": "NE", "lat": 46.998, "lon": 6.957},
    "PAY": {"name": "Payerne",         "canton": "VD", "lat": 46.812, "lon": 6.944},
    "PLS": {"name": "Lausanne",        "canton": "VD", "lat": 46.537, "lon": 6.613},
    "SIO": {"name": "Sion",            "canton": "VS", "lat": 46.217, "lon": 7.340},
    "STG": {"name": "St. Gallen",      "canton": "SG", "lat": 47.430, "lon": 9.400},
    "VIT": {"name": "Visp",            "canton": "VS", "lat": 46.295, "lon": 7.883},
    "ZUE": {"name": "Zürich",          "canton": "ZH", "lat": 47.376, "lon": 8.538},
}
 
POLLEN_PARAMS = {
    "Birch (Birke)":     {"code": "BETU", "color": "#e74c3c", "season": "Mar–May"},
    "Grass (Gräser)":    {"code": "POAC", "color": "#27ae60", "season": "May–Aug"},
    "Mugwort (Beifuss)": {"code": "ARTV", "color": "#8e44ad", "season": "Jul–Sep"},
    "Hazel (Hasel)":     {"code": "CORY", "color": "#f39c12", "season": "Jan–Mar"},
    "Alder (Erle)":      {"code": "ALNU", "color": "#2980b9", "season": "Feb–Apr"},
}
 
THRESHOLDS = {
    "Birch (Birke)":     [1, 10,  50, 200],
    "Grass (Gräser)":    [1, 10,  50, 200],
    "Mugwort (Beifuss)": [1,  5,  20,  80],
    "Hazel (Hasel)":     [1, 10,  50, 150],
    "Alder (Erle)":      [1, 10,  50, 150],
}
 
STAC_COLLECTION = "ch.meteoschweiz.ogd-pollen"
STAC_BASE = "https://data.geo.admin.ch/api/stac/v1"
 
# ── Data fetching via STAC API ─────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_asset_urls() -> dict:
    """
    Query the STAC API to get actual download URLs for each station's
    daily recent CSV file. Returns dict: {station_id_lower: url}
    """
    url = f"{STAC_BASE}/collections/{STAC_COLLECTION}/items?limit=200"
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "PollenCH-App/1.0"})
        r.raise_for_status()
        features = r.json().get("features", [])
        asset_map = {}
        for feature in features:
            assets = feature.get("assets", {})
            for asset_key, asset_val in assets.items():
                href = asset_val.get("href", "")
                # We want daily (d) recent files, e.g. ogd-pollen_zue_d_recent.csv
                if "_d_recent" in href and href.endswith(".csv"):
                    # Extract station ID from filename
                    fname = href.split("/")[-1]  # ogd-pollen_zue_d_recent.csv
                    parts = fname.replace(".csv", "").split("_")
                    if len(parts) >= 3:
                        sid = parts[2].upper()  # ZUE, BER, etc.
                        asset_map[sid] = href
        return asset_map
    except Exception as e:
        return {"_error": str(e)}
 
@st.cache_data(ttl=3600)
def fetch_station_data(station_id: str, url: str) -> pd.DataFrame | None:
    """Download and parse a MeteoSwiss pollen CSV from a known URL."""
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "PollenCH-App/1.0"})
        if r.status_code != 200:
            return None
        raw = r.text
        # MeteoSwiss format: semicolon separated, date format dd.mm.yyyy
        # First row is header
        df = pd.read_csv(io.StringIO(raw), sep=";", on_bad_lines="skip")
        if df.empty or len(df.columns) < 2:
            return None
        # First column is the date/time reference
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
        df = df.dropna(subset=[date_col])
        df = df.rename(columns={date_col: "date"})
        df = df.sort_values("date").reset_index(drop=True)
        # Convert all other columns to numeric
        for col in df.columns:
            if col != "date":
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception:
        return None
 
# ── Helpers ────────────────────────────────────────────────────────────────────
LEVEL_ORDER = ["none", "low", "moderate", "high", "very high"]
 
def sensitivity_mult(sensitivity):
    return {"Low (mild symptoms)": 0.5,
            "Medium (moderate symptoms)": 1.0,
            "High (severe symptoms)": 1.5}[sensitivity]
 
def get_level(value, thresholds, mult=1.0):
    if pd.isna(value) or value < 0:
        return "none"
    v = value * mult
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
    msgs = {
        "none":      f"✅ No significant {pollen_name} detected. Safe to go outside.",
        "low":       f"🟢 Low {pollen_name}. Outdoor activities fine. Consider antihistamines if sensitive.",
        "moderate":  f"🟡 Moderate {pollen_name}. Keep windows closed mornings (06–10h). Pre-medicate before going out.",
        "high":      f"🔴 High {pollen_name}! Limit outdoor time, especially mornings. Wear sunglasses. Shower after being outside.",
        "very high": f"🟣 Very high {pollen_name}! Stay indoors if possible. Use air purifiers. Take prescribed medication.",
    }
    return msgs.get(level, "")
 
def best_time_advice(level):
    if level in ("none","low"):
        return "✅ Any time of day is fine.", "💡 Afternoon slightly better — pollen disperses more after midday."
    elif level == "moderate":
        return "🕒 Best: afternoon (14–18h) or after rain.", "⚠️ Avoid mornings (06–10h) — peak dispersal time."
    elif level == "high":
        return "🌧️ Best: during or right after rain.", "⛔ Avoid mornings entirely. Evenings (after 19h) safer."
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
    load_btn = st.button("🔄 Refresh Data", use_container_width=True)
    st.markdown("**Data:** MeteoSwiss OGD  \n**Update:** Daily at 12 UTC  \n**Stations:** 15 across CH")
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">Pollen<span>CH</span></div>
  <div class="app-subtitle">Switzerland · Real-time pollen monitoring</div>
</div>
""", unsafe_allow_html=True)
 
if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()
 
# ── Load data ──────────────────────────────────────────────────────────────────
if load_btn:
    st.cache_data.clear()
 
with st.spinner("🔍 Querying MeteoSwiss STAC API for download URLs…"):
    asset_urls = get_asset_urls()
 
if "_error" in asset_urls:
    st.error(f"Could not connect to MeteoSwiss STAC API: {asset_urls['_error']}")
    st.info("Make sure your machine has internet access and can reach data.geo.admin.ch")
    st.stop()
 
if not asset_urls:
    st.error("MeteoSwiss STAC API returned no pollen file URLs.")
    st.stop()
 
with st.spinner(f"📥 Downloading data for {len(asset_urls)} stations…"):
    station_dfs = {}
    for sid, url in asset_urls.items():
        if sid in STATIONS:
            df = fetch_station_data(sid, url)
            if df is not None and not df.empty:
                station_dfs[sid] = df
 
if not station_dfs:
    st.error("Downloaded URLs but could not parse any station CSV data.")
    with st.expander("Debug: asset URLs found"):
        for k, v in asset_urls.items():
            st.write(f"`{k}`: {v}")
    st.stop()
 
home_df = station_dfs.get(selected_station)
home_info = STATIONS[selected_station]
 
mult = sensitivity_mult(sensitivity)
 
# ── Today's values ─────────────────────────────────────────────────────────────
st.markdown(f"<div class='section-title'>📍 Today at {home_info['name']}</div>", unsafe_allow_html=True)
 
today_vals = {}
if home_df is not None and not home_df.empty:
    latest_row = home_df.iloc[-1]
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
        today_vals[pollen] = float(latest_row[col]) if col and not pd.isna(latest_row[col]) else np.nan
 
cols = st.columns(len(selected_pollens))
for i, pollen in enumerate(selected_pollens):
    val = today_vals.get(pollen, np.nan)
    level = get_level(val, THRESHOLDS[pollen], mult)
    color = level_color(level)
    display_val = f"{val:.0f}" if not pd.isna(val) else "N/A"
    unit = " gr/m³" if not pd.isna(val) else ""
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
    val = today_vals.get(pollen, np.nan)
    lv = get_level(val, THRESHOLDS[pollen], mult)
    if LEVEL_ORDER.index(lv) > LEVEL_ORDER.index(worst_level):
        worst_level = lv
 
go_out, avoid = best_time_advice(worst_level)
adv1, adv2 = st.columns(2)
with adv1:
    st.markdown(f"""<div class="advice-block"><h4>🚪 Should you go outside?</h4>
    <p style="margin:0;font-size:0.95rem">{go_out}</p></div>""", unsafe_allow_html=True)
with adv2:
    st.markdown(f"""<div class="advice-block"><h4>⏰ Best/Worst times today</h4>
    <p style="margin:0;font-size:0.95rem">{avoid}</p></div>""", unsafe_allow_html=True)
 
st.markdown("")
for pollen in selected_pollens:
    val = today_vals.get(pollen, np.nan)
    level = get_level(val, THRESHOLDS[pollen], mult)
    cls = {"none":"alert-none","low":"alert-low","moderate":"alert-moderate",
           "high":"alert-high","very high":"alert-vhigh"}.get(level,"alert-none")
    st.markdown(f'<div class="alert-card {cls}">{advice_text(level, pollen)}</div>',
                unsafe_allow_html=True)
 
# ── Map ────────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🗺️ Switzerland Pollen Map</div>", unsafe_allow_html=True)
 
# Build map data
map_rows = []
for sid, sinfo in STATIONS.items():
    df = station_dfs.get(sid)
    if df is None or df.empty:
        continue
    latest = df.iloc[-1]
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        col = next((c for c in df.columns if code.upper() in c.upper()), None)
        val = float(latest[col]) if col and not pd.isna(latest.get(col, np.nan)) else 0.0
        level = get_level(val, THRESHOLDS[pollen], mult)
        map_rows.append({"station":sid,"name":sinfo["name"],"canton":sinfo["canton"],
                         "lat":sinfo["lat"],"lon":sinfo["lon"],
                         "pollen":pollen,"value":max(val,0),"level":level})
 
map_df = pd.DataFrame(map_rows)
 
tab1, tab2 = st.tabs(["🌡️ Heatmap", "📍 Station Risk Dots"])
 
def build_map(mode="heat"):
    m = folium.Map(location=[46.8,8.2], zoom_start=8,
                   tiles="CartoDB positron", control_scale=True)
    if map_df.empty:
        return m
    agg = map_df.groupby(["station","name","canton","lat","lon"]).agg(
        total_value=("value","sum"),
        worst_level=("level", lambda x: sorted(x, key=lambda l: LEVEL_ORDER.index(l))[-1])
    ).reset_index()
 
    if mode == "heat":
        heat_data = [[r.lat, r.lon, min(r.total_value, 400)] for r in agg.itertuples()]
        HeatMap(heat_data, radius=60, blur=40, min_opacity=0.3,
                gradient={"0.0":"#4caf50","0.35":"#ffeb3b",
                          "0.65":"#ff9800","1.0":"#e53935"}).add_to(m)
 
    for r in agg.itertuples():
        clr = level_color(r.worst_level)
        popup_html = (f"<div style='font-family:sans-serif;min-width:160px'>"
                      f"<b style='font-size:1rem'>{r.name}</b><br>"
                      f"<span style='color:#777;font-size:0.8rem'>Canton {r.canton}</span>"
                      f"<hr style='margin:4px 0'>"
                      f"<b style='color:{clr}'>{r.worst_level.upper()}</b> risk<br>"
                      f"<span style='font-size:0.8rem'>Combined: {r.total_value:.0f} gr/m³</span></div>")
        folium.CircleMarker(
            location=[r.lat, r.lon], radius=14,
            color="white", weight=2, fill=True,
            fill_color=clr, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{r.name}: {r.worst_level}",
        ).add_to(m)
 
    home = STATIONS[selected_station]
    folium.Marker([home["lat"],home["lon"]], tooltip="📍 Your location",
                  icon=folium.Icon(color="green",icon="home",prefix="fa")).add_to(m)
    return m
 
with tab1:
    st_folium(build_map("heat"), height=460, use_container_width=True)
with tab2:
    st_folium(build_map("dots"), height=460, use_container_width=True)
 
# ── Trend chart ────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>📈 Trend & 5-Day Seasonal Outlook</div>", unsafe_allow_html=True)
 
if home_df is not None and not home_df.empty:
    recent = home_df.tail(30).copy()
    fig = go.Figure()
 
    for pollen in selected_pollens:
        code = POLLEN_PARAMS[pollen]["code"]
        col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
        if not col:
            continue
        vals = pd.to_numeric(recent[col], errors="coerce").clip(lower=0)
        clr = POLLEN_PARAMS[pollen]["color"]
        fig.add_trace(go.Scatter(
            x=recent["date"], y=vals, name=pollen,
            line=dict(color=clr, width=2.5),
            fill="tozeroy", fillcolor=clr+"18",
            mode="lines+markers", marker=dict(size=5),
        ))
 
    t = THRESHOLDS[selected_pollens[0]]
    fig.add_hrect(y0=0,    y1=t[0], fillcolor="#4caf50", opacity=0.04, line_width=0)
    fig.add_hrect(y0=t[0], y1=t[1], fillcolor="#ffeb3b", opacity=0.06, line_width=0)
    fig.add_hrect(y0=t[1], y1=t[2], fillcolor="#ff9800", opacity=0.06, line_width=0)
    fig.add_hrect(y0=t[2], y1=t[3], fillcolor="#e53935", opacity=0.06, line_width=0)
 
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Date", gridcolor="#f0f0f0"),
        yaxis=dict(title="Pollen concentration (grains/m³)", gridcolor="#f0f0f0"),
        margin=dict(l=10,r=10,t=40,b=10), height=360,
    )
    st.plotly_chart(fig, use_container_width=True)
 
    # 5-day seasonal outlook
    st.markdown(f"**5-day seasonal outlook** — historical averages for this time of year at {home_info['name']}")
    today = datetime.today()
    doy = today.timetuple().tm_yday
    home_df["doy"] = home_df["date"].dt.dayofyear
 
    rows = []
    for offset in range(1, 6):
        future = today + timedelta(days=offset)
        target_doy = (doy + offset) % 365
        row = {"Date": future.strftime("%a %d %b")}
        for pollen in selected_pollens:
            code = POLLEN_PARAMS[pollen]["code"]
            col = next((c for c in home_df.columns if code.upper() in c.upper()), None)
            if col:
                window = home_df[abs(home_df["doy"] - target_doy) <= 7]
                avg = pd.to_numeric(window[col], errors="coerce").clip(lower=0).mean()
                lv = get_level(avg, THRESHOLDS[pollen], mult)
                row[pollen] = f"{level_emoji(lv)} {avg:.0f} gr/m³" if not pd.isna(avg) else "N/A"
            else:
                row[pollen] = "N/A"
        rows.append(row)
 
    st.dataframe(pd.DataFrame(rows).set_index("Date"), use_container_width=True)
 
# ── All-stations comparison ────────────────────────────────────────────────────
st.markdown("<div class='section-title'>🏔️ All Stations Comparison</div>", unsafe_allow_html=True)
 
if not map_df.empty:
    pivot = map_df[map_df["pollen"].isin(selected_pollens)].pivot_table(
        index=["name","canton"], columns="pollen", values="value", aggfunc="sum"
    ).reset_index()
    fig2 = go.Figure()
    for pollen in selected_pollens:
        if pollen not in pivot.columns:
            continue
        fig2.add_trace(go.Bar(
            name=pollen, x=pivot["name"], y=pivot[pollen].clip(lower=0),
            marker_color=POLLEN_PARAMS[pollen]["color"], opacity=0.85,
        ))
    fig2.update_layout(
        barmode="group", paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(tickangle=-35, gridcolor="#f0f0f0"),
        yaxis=dict(title="Pollen (gr/m³)", gridcolor="#f0f0f0"),
        margin=dict(l=10,r=10,t=30,b=80), height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)
 
# ── Debug expander ─────────────────────────────────────────────────────────────
with st.expander("🔧 Debug info"):
    st.write(f"**Stations loaded:** {len(station_dfs)}/{len(STATIONS)}")
    st.write(f"**Asset URLs found:** {len(asset_urls)}")
    for sid, df in list(station_dfs.items())[:3]:
        st.write(f"`{sid}` — {len(df)} rows | columns: `{list(df.columns[:10])}`")
    if home_df is not None:
        st.write("**Latest home station row:**")
        st.dataframe(home_df.tail(3))
 
# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.78rem;padding:0.5rem'>"
    "Data: <a href='https://www.meteoswiss.admin.ch' style='color:#4caf50'>MeteoSwiss Open Government Data</a> · "
    "CC-BY licence · Not a substitute for medical advice"
    "</div>", unsafe_allow_html=True,
)
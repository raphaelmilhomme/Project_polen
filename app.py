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
    page_title="BlessYou · Swiss Pollen Forecast",
    page_icon="🤧",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');
 
:root {
    --cream: #F7F3ED;
    --sage: #3D5A3E;
    --sage-light: #6B8F6C;
    --sage-pale: #C8DAC8;
    --ink: #1A1A18;
    --ink-soft: #3A3A36;
    --gold: #B8935A;
    --rust: #C4532A;
    --surface: #EFEBE3;
    --surface2: #E8E2D8;
    --border: rgba(61,90,62,0.15);
}
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream) !important;
    color: var(--ink);
}
 
.stApp { background: var(--cream) !important; }
 
/* Sidebar */
[data-testid="stSidebar"] {
    background: #1A1A18 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #C8DAC8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #6B8F6C !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSidebar"] .sidebar-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.4rem;
    color: white !important;
    font-style: italic;
}
 
/* Header */
.app-header {
    padding: 3rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.app-logo {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1;
}
.app-logo em { color: var(--sage); font-style: italic; }
.app-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--sage-light);
    margin-bottom: 0.5rem;
}
.app-sub {
    font-size: 0.75rem;
    color: var(--sage-light);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.4rem;
    font-weight: 300;
}
 
/* Stat cards */
.stat-card {
    background: var(--surface);
    border-radius: 16px;
    padding: 1.25rem;
    border: 1px solid var(--border);
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: var(--sage-light); }
.stat-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
}
.stat-card .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--ink-soft);
    margin-top: 0.3rem;
    font-family: 'DM Mono', monospace;
}
.stat-card .level {
    font-size: 0.7rem;
    font-weight: 600;
    margin-top: 0.25rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.stat-card .season {
    font-size: 0.65rem;
    color: var(--sage-light);
    margin-top: 0.2rem;
    font-family: 'DM Mono', monospace;
}
 
/* Section titles */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--ink);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    font-style: italic;
}
 
/* Alert cards */
.alert-card {
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    font-weight: 400;
    border-left: 3px solid;
    font-family: 'DM Sans', sans-serif;
}
.alert-none     { background: #F5F5F0; border-color: #9e9e9e; color: var(--ink-soft); }
.alert-low      { background: #EAF3EA; border-color: var(--sage); color: #1b5e20; }
.alert-moderate { background: #FDF6EC; border-color: var(--gold); color: #7A4F00; }
.alert-high     { background: #FDF0EC; border-color: var(--rust); color: #7A2000; }
.alert-vhigh    { background: #F3ECF8; border-color: #8e24aa; color: #4a148c; }
 
/* Advice block */
.advice-block {
    background: var(--surface);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid var(--border);
}
.advice-block h4 {
    font-family: 'Playfair Display', serif;
    color: var(--ink);
    margin: 0 0 0.75rem;
    font-size: 1rem;
    font-style: italic;
}
 
/* Risk card */
.risk-hero {
    background: var(--sage);
    border-radius: 20px;
    padding: 2.5rem;
    color: var(--sage-pale);
    margin-bottom: 2rem;
}
.risk-hero .score {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 700;
    color: white;
    line-height: 1;
}
.risk-hero .score span {
    font-size: 1.8rem;
    color: var(--sage-pale);
    vertical-align: super;
}
.risk-hero .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--sage-pale);
    margin-bottom: 1rem;
}
 
/* Buttons */
.stButton > button {
    background: var(--sage) !important;
    color: white !important;
    border: none !important;
    border-radius: 40px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    background: var(--sage-light) !important;
}
 
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
 
POLLEN_PARAMS = {
    "Birch":   {"api":"birch_pollen",   "color":"#C4532A","season":"Mar–May"},
    "Grass":   {"api":"grass_pollen",   "color":"#3D5A3E","season":"May–Aug"},
    "Mugwort": {"api":"mugwort_pollen", "color":"#7B6FA0","season":"Jul–Sep"},
    "Hazel":   {"api":"alder_pollen",   "color":"#B8935A","season":"Jan–Mar"},
    "Alder":   {"api":"alder_pollen",   "color":"#6B8F6C","season":"Feb–Apr"},
}
 
THRESHOLDS = {
    "Birch":   [1, 10,  50, 200],
    "Grass":   [1, 10,  50, 200],
    "Mugwort": [1,  5,  20,  80],
    "Hazel":   [1, 10,  50, 150],
    "Alder":   [1, 10,  50, 150],
}
 
LEVEL_ORDER = ["none","low","moderate","high","very high"]
 
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
        data = r.json()
        return data.get("hourly", None)
    except Exception:
        return None
 
# ── Helpers ────────────────────────────────────────────────────────────────────
def sensitivity_mult(sensitivity):
    return {"Low":0.5, "Medium":1.0, "High":1.5}[sensitivity]
 
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
    return {"none":"#9e9e9e","low":"#3D5A3E","moderate":"#B8935A",
            "high":"#C4532A","very high":"#8e24aa"}.get(level,"#9e9e9e")
 
def level_emoji(level):
    return {"none":"⚪","low":"🟢","moderate":"🟡",
            "high":"🔴","very high":"🟣"}.get(level,"⚪")
 
def advice_text(level, pollen_name):
    return {
        "none":     f"✅ No significant {pollen_name} detected. Safe to go outside.",
        "low":      f"🟢 Low {pollen_name}. Fine for most people. Consider antihistamines if sensitive.",
        "moderate": f"🟡 Moderate {pollen_name}. Keep windows closed 6–10am. Pre-medicate before going out.",
        "high":     f"🔴 High {pollen_name}! Limit outdoor time, especially mornings. Shower after being outside.",
        "very high":f"🟣 Very high {pollen_name}! Stay indoors if possible. Use air purifiers and take medication.",
    }.get(level,"")
 
def best_time_advice(level):
    if level in ("none","low"):
        return "✅ Any time of day is fine.", "💡 Afternoon is slightly better — pollen disperses more after midday."
    elif level == "moderate":
        return "🕒 Best: afternoon (2–6pm) or after rain.", "⚠️ Avoid mornings (6–10am) — peak dispersal time."
    elif level == "high":
        return "🌧️ Best: during or right after rain.", "⛔ Avoid mornings entirely. Evenings (after 7pm) are safer."
    else:
        return "🏠 Recommend staying indoors today.", "⛔ All outdoor activities carry high risk."
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤧 BlessYou</div>', unsafe_allow_html=True)
    st.markdown("---")
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
    st.markdown("---")
    load_btn = st.button("↻  Refresh Data", use_container_width=True)
    st.markdown("""
    <div style='font-size:0.7rem;color:#6B8F6C;line-height:1.8;margin-top:1rem;font-family:DM Mono,monospace;'>
    DATA · Open-Meteo Air Quality<br>
    SOURCE · CAMS European Forecast<br>
    UPDATE · Every 24h · 5-day forecast<br>
    KEY · None required ✓
    </div>
    """, unsafe_allow_html=True)
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div>
    <div class="app-eyebrow">Swiss Pollen Monitor · {datetime.now().year}</div>
    <div class="app-logo">Bless<em>You</em></div>
    <div class="app-sub">Real-time pollen forecast · Switzerland</div>
  </div>
  <div style="text-align:right">
    <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#6B8F6C;letter-spacing:0.1em;">
      {datetime.now().strftime('%a %d %b %Y').upper()}
    </div>
    <div style="display:inline-flex;align-items:center;gap:6px;background:#3D5A3E;color:#E8F0E8;
                padding:8px 16px;border-radius:40px;font-size:0.8rem;font-weight:500;margin-top:8px;">
      <div style="width:6px;height:6px;border-radius:50%;background:#C8DAC8;"></div>
      {selected_city} · {STATIONS.get(selected_city, {}).get('canton','')}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
 
if not selected_pollens:
    st.info("👈 Select at least one pollen type in the sidebar to get started.")
    st.stop()
 
if load_btn:
    st.cache_data.clear()
 
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
st.markdown("<div class='section-title'>Today's Pollens</div>", unsafe_allow_html=True)
 
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
            <div class="value" style="color:{color}">{display_val}{unit}</div>
            <div class="label">{pollen}</div>
            <div class="level" style="color:{color}">{level_emoji(level)} {level.upper()}</div>
            <div class="season">Season: {POLLEN_PARAMS[pollen]['season']}</div>
        </div>
        """, unsafe_allow_html=True)
 
# ── Daily advice ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Today's Advice</div>", unsafe_allow_html=True)
 
worst_level = "none"
for pollen in selected_pollens:
    lv = get_level(today_vals.get(pollen, np.nan), THRESHOLDS[pollen], mult)
    if LEVEL_ORDER.index(lv) > LEVEL_ORDER.index(worst_level):
        worst_level = lv
 
go_out, avoid = best_time_advice(worst_level)
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="advice-block"><h4>Should you go outside?</h4><p style="margin:0;font-size:0.9rem;">{go_out}</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="advice-block"><h4>Best & worst times today</h4><p style="margin:0;font-size:0.9rem;">{avoid}</p></div>', unsafe_allow_html=True)
 
st.markdown("")
for pollen in selected_pollens:
    level = get_level(today_vals.get(pollen, np.nan), THRESHOLDS[pollen], mult)
    cls = {"none":"alert-none","low":"alert-low","moderate":"alert-moderate",
           "high":"alert-high","very high":"alert-vhigh"}.get(level,"alert-none")
    st.markdown(f'<div class="alert-card {cls}">{advice_text(level, pollen)}</div>', unsafe_allow_html=True)
 
# ── Forecast chart ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>5-Day Pollen Forecast</div>", unsafe_allow_html=True)
 
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
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.08)",
        mode="lines",
    ))
 
now = datetime.now()
fig.add_vline(x=now.timestamp()*1000, line_dash="dash",
              line_color="#6B8F6C", annotation_text="Now",
              annotation_position="top right")
 
t = THRESHOLDS[selected_pollens[0]]
fig.add_hrect(y0=0,    y1=t[0], fillcolor="#3D5A3E", opacity=0.03, line_width=0)
fig.add_hrect(y0=t[0], y1=t[1], fillcolor="#B8C87B", opacity=0.04, line_width=0)
fig.add_hrect(y0=t[1], y1=t[2], fillcolor="#B8935A", opacity=0.04, line_width=0)
fig.add_hrect(y0=t[2], y1=t[3], fillcolor="#C4532A", opacity=0.04, line_width=0)
 
fig.update_layout(
    paper_bgcolor="#EFEBE3",
    plot_bgcolor="#EFEBE3",
    font=dict(family="DM Sans", size=12, color="#1A1A18"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(title="", gridcolor="rgba(61,90,62,0.1)", showgrid=True),
    yaxis=dict(title="Pollen (grains/m³)", gridcolor="rgba(61,90,62,0.1)"),
    margin=dict(l=10,r=10,t=40,b=10),
    height=360,
)
st.plotly_chart(fig, use_container_width=True)
 
# ── 5-day daily summary ────────────────────────────────────────────────────────
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
st.markdown("<div class='section-title'>Switzerland Pollen Map</div>", unsafe_allow_html=True)
 
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
 
tab1, tab2 = st.tabs(["Heatmap", "Risk Dots"])
 
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
        popup_html = (f"<div style='font-family:DM Sans,sans-serif;padding:4px'>"
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
                gradient={"0.0":"#3D5A3E","0.35":"#B8935A",
                          "0.65":"#C4532A","1.0":"#8e24aa"}).add_to(m)
 
    folium.Marker(
        [home["lat"], home["lon"]], tooltip=f"📍 {selected_city}",
        icon=folium.Icon(color="green", icon="home", prefix="fa"),
    ).add_to(m)
    return m
 
with tab1:
    st_folium(build_map("heat"), height=460, use_container_width=True)
with tab2:
    st_folium(build_map("dots"), height=460, use_container_width=True)
 
# ── City comparison ────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>All Cities — Today's Peak</div>", unsafe_allow_html=True)
 
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
    paper_bgcolor="#EFEBE3",
    plot_bgcolor="#EFEBE3",
    font=dict(family="DM Sans", size=11, color="#1A1A18"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(tickangle=-35, gridcolor="rgba(61,90,62,0.1)"),
    yaxis=dict(title="Pollen peak (gr/m³)", gridcolor="rgba(61,90,62,0.1)"),
    margin=dict(l=10,r=10,t=30,b=90),
    height=380,
)
st.plotly_chart(fig2, use_container_width=True)
 
# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6B8F6C;font-size:0.72rem;padding:0.5rem;"
    "font-family:DM Mono,monospace;letter-spacing:0.08em;'>"
    "BLESSYOU · Pollen data: <a href='https://open-meteo.com' style='color:#3D5A3E'>Open-Meteo Air Quality API</a> · "
    "Source: CAMS European Air Quality Forecast · "
    "Not a substitute for medical advice"
    "</div>", unsafe_allow_html=True,
)
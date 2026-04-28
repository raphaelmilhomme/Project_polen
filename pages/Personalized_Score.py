import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Personalized Score", page_icon="🎯", layout="wide")

# ── Constants ──────────────────────────────────────────────────────────────────
STATIONS = {
    "Zürich":     {"lat": 47.376, "lon": 8.538},
    "Bern":       {"lat": 46.948, "lon": 7.447},
    "Basel":      {"lat": 47.560, "lon": 7.589},
    "Geneva":     {"lat": 46.204, "lon": 6.143},
    "Lausanne":   {"lat": 46.519, "lon": 6.633},
    "Luzern":     {"lat": 47.050, "lon": 8.309},
    "St. Gallen": {"lat": 47.422, "lon": 9.369},
    "Lugano":     {"lat": 46.004, "lon": 8.960},
    "Sion":       {"lat": 46.233, "lon": 7.360},
    "Davos":      {"lat": 46.813, "lon": 9.844},
}

THRESHOLDS = {
    "Birch":   [1, 10, 50, 200],
    "Grass":   [1, 10, 50, 200],
    "Mugwort": [1,  5, 20,  80],
    "Hazel":   [1, 10, 50, 150],
    "Alder":   [1, 10, 50, 150],
}

POLLEN_API = {
    "Birch":   "birch_pollen",
    "Grass":   "grass_pollen",
    "Mugwort": "mugwort_pollen",
    "Hazel":   "alder_pollen",
    "Alder":   "alder_pollen",
}

LEVEL_ORDER = ["none", "low", "moderate", "high", "very high"]
level_scores = {"none": 0, "low": 2, "moderate": 5, "high": 7, "very high": 10}

# ── API Functions ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_pollen_forecast(lat, lon, pollen_vars):
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

@st.cache_data(ttl=3600)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"precipitation,wind_speed_10m"
        f"&timezone=Europe%2FZurich"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("current", None)
    except Exception:
        return None

# ── Helper functions ───────────────────────────────────────────────────────────
def get_level(value, thresholds, mult=1.0):
    if value is None or np.isnan(float(value)):
        return "none"
    v = float(value) * mult
    if v < thresholds[0]:   return "none"
    elif v < thresholds[1]: return "low"
    elif v < thresholds[2]: return "moderate"
    elif v < thresholds[3]: return "high"
    else:                   return "very high"

def sensitivity_mult(sensitivity):
    return {"Low": 0.5, "Medium": 1.0, "High": 1.5}[sensitivity]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🎯 Your Personalized Risk Score")
st.caption("Automatically calculated from live pollen data, weather, and your personal profile.")
st.divider()

# ── Section 1: Personal Profile ───────────────────────────────────────────────
st.subheader("👤 Your Personal Profile")

col1, col2, col3 = st.columns(3)
with col1:
    selected_city = st.selectbox("📍 Your location", options=list(STATIONS.keys()))
    selected_pollens = st.multiselect(
        "🌿 Your pollen allergies",
        options=list(THRESHOLDS.keys()),
        default=["Birch", "Grass"],
    )
    sensitivity = st.select_slider(
        "🎚️ Sensitivity level",
        options=["Low", "Medium", "High"],
        value="Medium",
    )

with col2:
    age = st.number_input("🎂 Your age", min_value=1, max_value=100, value=25)
    has_asthma = st.radio("🫁 Do you have asthma?", ["No", "Yes"], horizontal=True)
    hours_outside = st.slider("🚶 Hours outside today", 0, 12, 2)

with col3:
    medication = st.radio(
        "💊 Are you taking allergy medication?",
        [
            "No medication",
            "Antihistamines (e.g. Cetirizine)",
            "Nasal spray",
            "Both antihistamines + nasal spray",
        ]
    )

st.divider()

if not selected_pollens:
    st.info("👈 Select at least one pollen type to calculate your score.")
    st.stop()

# ── Fetch live data ────────────────────────────────────────────────────────────
home = STATIONS[selected_city]
pollen_vars = list({POLLEN_API[p] for p in selected_pollens})

with st.spinner("Fetching live pollen and weather data..."):
    hourly = fetch_pollen_forecast(home["lat"], home["lon"], pollen_vars)
    weather = fetch_weather(home["lat"], home["lon"])

if not hourly:
    st.error("❌ Could not load pollen data. Check your connection.")
    st.stop()

# Process pollen data
df = pd.DataFrame(hourly)
df["time"] = pd.to_datetime(df["time"])
today = datetime.now().date()
today_df = df[df["time"].dt.date == today]

mult = sensitivity_mult(sensitivity)
today_vals = {}
for pollen in selected_pollens:
    api_key = POLLEN_API[pollen]
    if api_key in today_df.columns:
        vals = pd.to_numeric(today_df[api_key], errors="coerce").dropna()
        today_vals[pollen] = float(vals.max()) if len(vals) > 0 else np.nan
    else:
        today_vals[pollen] = np.nan

pollen_levels = {
    p: get_level(today_vals.get(p, np.nan), THRESHOLDS[p], mult)
    for p in selected_pollens
}

# ── Section 2: Risk Score ──────────────────────────────────────────────────────
st.subheader("🎯 Your Risk Score")

# Calculate score
raw_scores = [level_scores[pollen_levels[p]] for p in selected_pollens]
avg_raw = sum(raw_scores) / len(raw_scores)

# Personal factors
age_factor = 1.2 if age < 12 or age > 65 else 1.0
asthma_factor = 1.3 if has_asthma == "Yes" else 1.0
medication_factor = {
    "No medication": 1.0,
    "Antihistamines (e.g. Cetirizine)": 0.7,
    "Nasal spray": 0.8,
    "Both antihistamines + nasal spray": 0.5,
}[medication]
exposure_factor = 1 + (hours_outside * 0.05)

# Weather factor
weather_factor = 1.0
if weather:
    wind = weather.get("wind_speed_10m", 0)
    rain = weather.get("precipitation", 0)
    humidity = weather.get("relative_humidity_2m", 50)
    if isinstance(wind, (int, float)) and wind > 20:
        weather_factor += 0.2
    if isinstance(rain, (int, float)) and rain > 0:
        weather_factor -= 0.2
    if isinstance(humidity, (int, float)) and humidity < 40:
        weather_factor += 0.1

final_score = min(round(
    avg_raw * age_factor * asthma_factor * medication_factor
    * exposure_factor * weather_factor, 1
), 10.0)

# Badge
if final_score <= 2:
    badge = "🟢 Safe Day"
    color = "success"
elif final_score <= 4:
    badge = "🟡 Low Risk Day"
    color = "success"
elif final_score <= 6:
    badge = "🟠 Caution Day"
    color = "warning"
elif final_score <= 8:
    badge = "🔴 High Risk Day"
    color = "error"
else:
    badge = "🟣 Stay Inside Day"
    color = "error"

col_score, col_badge, col_explain = st.columns([1, 1, 2])
with col_score:
    st.metric(label="Personal Risk Score", value=f"{final_score} / 10")
    st.progress(int(final_score * 10))

with col_badge:
    st.markdown(f"### {badge}")
    st.caption("Based on your profile + live data")

with col_explain:
    st.info(
        f"**Score breakdown:**\n\n"
        f"- Pollen: {', '.join([f'{p} ({pollen_levels[p]})' for p in selected_pollens])}\n"
        f"- Sensitivity: **{sensitivity}**\n"
        f"- Asthma: **{has_asthma}**\n"
        f"- Medication: **{medication}**\n"
        f"- Hours outside: **{hours_outside}h**\n"
        f"- Weather impact: **{'↑ worse' if weather_factor > 1 else '↓ better' if weather_factor < 1 else 'neutral'}**\n"
        f"- Age factor: **{'Yes' if age < 12 or age > 65 else 'No'}**"
    )

st.divider()

# ── Section 3: Best Day This Week ─────────────────────────────────────────────
st.subheader("📅 Best Day to Go Outside This Week")

df["date"] = df["time"].dt.date
daily_scores = []
for d in sorted(df["date"].unique()):
    day_data = df[df["date"] == d]
    day_vals = {}
    for pollen in selected_pollens:
        api_key = POLLEN_API[pollen]
        if api_key in day_data.columns:
            peak = pd.to_numeric(day_data[api_key], errors="coerce").max()
            day_vals[pollen] = float(peak) if not np.isnan(peak) else 0.0
        else:
            day_vals[pollen] = 0.0
    day_levels = {p: get_level(day_vals[p], THRESHOLDS[p], mult) for p in selected_pollens}
    day_raw = sum([level_scores[day_levels[p]] for p in selected_pollens]) / len(selected_pollens)
    daily_scores.append({
        "date": d,
        "label": pd.Timestamp(d).strftime("%A %d %b"),
        "score": round(day_raw, 1),
        "levels": day_levels,
    })

best_day = min(daily_scores, key=lambda x: x["score"])
worst_day = max(daily_scores, key=lambda x: x["score"])

col_best, col_worst = st.columns(2)
with col_best:
    st.success(
        f"**✅ Best day: {best_day['label']}**\n\n"
        f"Pollen score: {best_day['score']}/10\n\n"
        f"Great day for outdoor activities!"
    )
with col_worst:
    st.error(
        f"**⚠️ Worst day: {worst_day['label']}**\n\n"
        f"Pollen score: {worst_day['score']}/10\n\n"
        f"Try to stay indoors if possible."
    )

st.divider()

# ── Section 4: Medication Reminder ────────────────────────────────────────────
st.subheader("💊 Medication & Timing Advice")

if medication == "No medication":
    if final_score >= 5:
        st.warning(
            "⚠️ Your risk score is high. Consider speaking to a doctor about "
            "antihistamines like Cetirizine or Loratadine."
        )
    else:
        st.success("✅ No medication needed today based on your risk level.")

elif "Antihistamines" in medication:
    st.success(
        "💊 **Antihistamine reminder:**\n\n"
        "Take your antihistamine **2 hours before** going outside for best effect.\n\n"
        f"Since pollen peaks at 6–10am, we recommend taking it by **7am** today.\n\n"
        "✅ Antihistamines reduce your risk score by ~30%."
    )

elif medication == "Nasal spray":
    st.success(
        "🌿 **Nasal spray reminder:**\n\n"
        "Use your nasal spray **every morning** before going outside.\n\n"
        "For best effect, use it **30 minutes** before exposure.\n\n"
        "✅ Nasal sprays reduce inflammation and are most effective used consistently."
    )

elif medication == "Both antihistamines + nasal spray":
    st.success(
        "💊🌿 **Combined medication reminder:**\n\n"
        "1. Take your **antihistamine** 2 hours before going outside\n"
        "2. Use your **nasal spray** 30 minutes before going outside\n\n"
        f"Best time today: antihistamine by **7am**, nasal spray by **8:30am**\n\n"
        "✅ Combined treatment reduces your risk score by ~50%!"
    )

st.divider()

# ── Section 5: Community Tips ─────────────────────────────────────────────────
st.subheader("🤝 Community Tips")
st.caption("Share tips with other allergy sufferers in Switzerland!")

# Load existing tips from storage
try:
    existing = window.storage.get("community_tips")
    tips = existing if existing else []
except:
    tips = []

# Show existing tips
if tips:
    for tip in tips[-10:]:
        st.markdown(f"💬 **{tip['city']}** · {tip['date']}: {tip['tip']}")
else:
    st.info("No tips yet — be the first to share!")

# Add new tip
with st.form("tip_form"):
    new_tip = st.text_input("Share a tip with the community (e.g. 'Wearing sunglasses helps a lot!')")
    submitted = st.form_submit_button("Share tip 💬")
    if submitted and new_tip:
        tips.append({
            "city": selected_city,
            "date": datetime.now().strftime("%d %b"),
            "tip": new_tip,
        })
        st.success("✅ Tip shared!")
        st.rerun()
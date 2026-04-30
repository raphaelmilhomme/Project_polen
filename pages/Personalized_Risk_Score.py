import streamlit as st
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from user_profile import (
    init_profile, get_profile, set_profile, profile_banner,
    STATIONS, POLLEN_PARAMS, THRESHOLDS,
    sensitivity_mult, get_level,
)

st.set_page_config(page_title="Personalized Risk Score", page_icon="🎯", layout="wide")

init_profile()

POLLEN_API    = {k: v["api"] for k, v in POLLEN_PARAMS.items()}
level_scores  = {"none": 0, "low": 2, "moderate": 5, "high": 7, "very high": 10}

# ── API Functions ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_pollen_forecast(lat, lon, pollen_vars):
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

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🎯 Your Personalized Risk Score")
st.caption("Fill in your profile once — it will be remembered across all pages of BlessYou.")
st.divider()
profile_banner()
st.divider()

# ── Section 1: Personal Profile ───────────────────────────────────────────────
st.subheader("👤 Your Personal Profile")

p = get_profile()

col1, col2, col3 = st.columns(3)
with col1:
    selected_city = st.selectbox(
        "📍 Your location",
        options=list(STATIONS.keys()),
        index=list(STATIONS.keys()).index(p["city"]) if p["city"] in STATIONS else 0,
    )
    selected_pollens = st.multiselect(
        "🌿 Your pollen allergies",
        options=list(THRESHOLDS.keys()),
        default=p["pollens"] if p["pollens"] else ["Birch", "Grass"],
    )
    sensitivity = st.select_slider(
        "🎚️ Sensitivity level",
        options=["Low", "Medium", "High"],
        value=list(p["sensitivities"].values())[0] if p["sensitivities"] else "Medium",
    )

with col2:
    age_group = st.radio(
        "🎂 Your age group",
        ["Under 12", "12–65", "Over 65"],
        index=["Under 12", "12–65", "Over 65"].index(p["age_group"]) if p["age_group"] in ["Under 12", "12–65", "Over 65"] else 1,
        horizontal=True,
    )
    has_asthma = st.radio(
        "🫁 Do you have asthma?",
        ["No", "Yes"],
        index=["No", "Yes"].index(p["asthma"]),
        horizontal=True,
    )
    hours_outside = st.slider("🚶 Hours outside today", 0, 12, p["hours_outside"])

with col3:
    med_options = [
        "No medication",
        "Antihistamines (e.g. Cetirizine)",
        "Nasal spray",
        "Both antihistamines + nasal spray",
    ]
    medication = st.radio(
        "💊 Are you taking allergy medication?",
        med_options,
        index=med_options.index(p["medication"]) if p["medication"] in med_options else 0,
    )

st.divider()

if not selected_pollens:
    st.info("👈 Select at least one pollen type to calculate your score.")
    st.stop()

# ── Fetch live data ────────────────────────────────────────────────────────────
home        = STATIONS[selected_city]
pollen_vars = list({POLLEN_API[p_] for p_ in selected_pollens})

with st.spinner("Fetching live pollen and weather data..."):
    hourly  = fetch_pollen_forecast(home["lat"], home["lon"], pollen_vars)
    weather = fetch_weather(home["lat"], home["lon"])

if not hourly:
    st.error("❌ Could not load pollen data. Check your connection.")
    st.stop()

df       = pd.DataFrame(hourly)
df["time"] = pd.to_datetime(df["time"])
today    = datetime.now().date()
today_df = df[df["time"].dt.date == today]

mult       = sensitivity_mult(sensitivity)
today_vals = {}
for pollen in selected_pollens:
    api_key = POLLEN_API[pollen]
    if api_key in today_df.columns:
        vals = pd.to_numeric(today_df[api_key], errors="coerce").dropna()
        today_vals[pollen] = float(vals.max()) if len(vals) > 0 else np.nan
    else:
        today_vals[pollen] = np.nan

pollen_levels = {
    p_: get_level(today_vals.get(p_, np.nan), THRESHOLDS[p_], mult)
    for p_ in selected_pollens
}

# ── Score calculation ──────────────────────────────────────────────────────────
raw_scores   = [level_scores[pollen_levels[p_]] for p_ in selected_pollens]
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
if weather:
    wind     = weather.get("wind_speed_10m", 0)
    rain     = weather.get("precipitation", 0)
    humidity = weather.get("relative_humidity_2m", 50)
    if isinstance(wind,     (int, float)) and wind     > 20: weather_factor += 0.2
    if isinstance(rain,     (int, float)) and rain     > 0:  weather_factor -= 0.2
    if isinstance(humidity, (int, float)) and humidity < 40: weather_factor += 0.1

final_score = min(round(
    avg_raw * age_factor * asthma_factor * medication_factor
    * exposure_factor * weather_factor, 1
), 10.0)

if final_score <= 2:   badge, color = "🟢 Safe Day",        "success"
elif final_score <= 4: badge, color = "🟡 Low Risk Day",    "success"
elif final_score <= 6: badge, color = "🟠 Caution Day",     "warning"
elif final_score <= 8: badge, color = "🔴 High Risk Day",   "error"
else:                  badge, color = "🟣 Stay Inside Day", "error"

# ── Save full profile ──────────────────────────────────────────────────────────
set_profile({
    "city":          selected_city,
    "pollens":       selected_pollens,
    "sensitivities": {p_: sensitivity for p_ in selected_pollens},
    "age_group":     age_group,
    "asthma":        has_asthma,
    "medication":    medication,
    "hours_outside": hours_outside,
    "risk_score":    final_score,
    "risk_badge":    badge,
    "setup_done":    True,
})

# ── Section 2: Risk Score ──────────────────────────────────────────────────────
st.subheader("🎯 Your Risk Score")

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
        f"- Pollen: {', '.join([f'{p_} ({pollen_levels[p_]})' for p_ in selected_pollens])}\n"
        f"- Sensitivity: **{sensitivity}**\n"
        f"- Asthma: **{has_asthma}**\n"
        f"- Medication: **{medication}**\n"
        f"- Hours outside: **{hours_outside}h**\n"
        f"- Weather impact: **{'↑ worse' if weather_factor > 1 else '↓ better' if weather_factor < 1 else 'neutral'}**\n"
        f"- Age factor: **{'Yes' if age_group in ['Under 12', 'Over 65'] else 'No'}**"
    )

st.success("✅ Your profile is saved and visible across all BlessYou pages!")
st.divider()

# ── Section 3: Best Day This Week ─────────────────────────────────────────────
st.subheader("📅 Best Day to Go Outside This Week")

df["date"]   = df["time"].dt.date
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
    day_levels = {p_: get_level(day_vals[p_], THRESHOLDS[p_], mult) for p_ in selected_pollens}
    day_raw    = sum([level_scores[day_levels[p_]] for p_ in selected_pollens]) / len(selected_pollens)
    daily_scores.append({
        "date":   d,
        "label":  pd.Timestamp(d).strftime("%A %d %b"),
        "score":  round(day_raw, 1),
        "levels": day_levels,
    })

best_day  = min(daily_scores, key=lambda x: x["score"])
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
        st.warning("⚠️ Your risk score is high. Consider speaking to a doctor about antihistamines like Cetirizine or Loratadine.")
    else:
        st.success("✅ No medication needed today based on your risk level.")
elif "Antihistamines" in medication:
    st.success(
        "💊 **Antihistamine reminder:**\n\n"
        "Take your antihistamine **2 hours before** going outside for best effect.\n\n"
        "Since pollen peaks at 6–10am, we recommend taking it by **7am** today.\n\n"
        "✅ Antihistamines reduce your risk score by ~30%."
    )
elif medication == "Nasal spray":
    st.success(
        "🌿 **Nasal spray reminder:**\n\n"
        "Use your nasal spray **every morning** before going outside.\n\n"
        "For best effect, use it **30 minutes** before exposure.\n\n"
        "✅ Nasal sprays are most effective used consistently."
    )
elif medication == "Both antihistamines + nasal spray":
    st.success(
        "💊🌿 **Combined medication reminder:**\n\n"
        "1. Take your **antihistamine** 2 hours before going outside\n"
        "2. Use your **nasal spray** 30 minutes before going outside\n\n"
        "Best time today: antihistamine by **7am**, nasal spray by **8:30am**\n\n"
        "✅ Combined treatment reduces your risk score by ~50%!"
    )

st.divider()
st.caption("🎯 BlessYou · Your profile is saved for this session across all pages.")
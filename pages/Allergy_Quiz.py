import streamlit as st
import requests
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Allergy Quiz", page_icon="🩺", layout="wide")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🩺 Allergy Assessment Quiz")
st.caption("Answer a few questions and we'll help identify your potential pollen allergies.")

st.warning("""
⚠️ **Medical Disclaimer:** This quiz is for informational purposes only and is 
NOT a medical diagnosis. Always consult a qualified doctor or allergist for 
proper diagnosis and treatment.
""")

st.divider()

# ── Step 1: Basic Symptoms ─────────────────────────────────────────────────────
st.subheader("Step 1: 🤧 Your Symptoms")
st.caption("How often do you experience these symptoms when outdoors?")

options = ["Never", "Rarely", "Sometimes", "Often", "Always"]

col1, col2 = st.columns(2)
with col1:
    sneezing = st.select_slider("🤧 Sneezing", options=options, value="Never")
    itchy_eyes = st.select_slider("👁️ Itchy or watery eyes", options=options, value="Never")
    runny_nose = st.select_slider("👃 Runny or blocked nose", options=options, value="Never")
    itchy_throat = st.select_slider("🗣️ Itchy throat", options=options, value="Never")

with col2:
    skin_rash = st.select_slider("🔴 Skin rash or hives", options=options, value="Never")
    breathing = st.select_slider("😮‍💨 Difficulty breathing", options=options, value="Never")
    fatigue = st.select_slider("😴 Unusual fatigue", options=options, value="Never")
    headache = st.select_slider("🤕 Headaches", options=options, value="Never")

st.divider()

# ── Step 2: Triggers ───────────────────────────────────────────────────────────
st.subheader("Step 2: 🌍 What Makes It Worse?")

col3, col4 = st.columns(2)
with col3:
    worse_wind = st.radio("🌬️ Symptoms worse on windy days?", ["No", "A little", "Yes, much worse"], horizontal=True)
    better_rain = st.radio("🌧️ Symptoms better when it rains?", ["No", "A little", "Yes, much better"], horizontal=True)
    worse_outside = st.radio("🌳 Symptoms worse when outside?", ["No", "A little", "Yes, much worse"], horizontal=True)

with col4:
    better_inside = st.radio("🏠 Symptoms better indoors?", ["No", "A little", "Yes, much better"], horizontal=True)
    worse_morning = st.radio("🌅 Symptoms worse in the morning?", ["No", "A little", "Yes, much worse"], horizontal=True)
    helped_antihistamine = st.radio("💊 Have antihistamines helped before?", ["Never tried", "No", "A little", "Yes"], horizontal=True)

st.divider()

# ── Step 3: Seasonal Pattern ───────────────────────────────────────────────────
st.subheader("Step 3: 📅 When Are Symptoms Worst?")

worst_months = st.multiselect(
    "Which months are your symptoms worst?",
    options=["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"],
    default=[],
)

st.divider()

# ── Step 4: Severity ───────────────────────────────────────────────────────────
st.subheader("Step 4: 📊 How Severe Are Your Symptoms?")

severity = st.select_slider(
    "Overall severity of your symptoms",
    options=["No symptoms", "Mild", "Moderate", "Severe", "Unbearable"],
    value="No symptoms",
)

years_suffering = st.slider("How many years have you had these symptoms?", 0, 30, 0)

st.divider()

# ── Calculate Results ──────────────────────────────────────────────────────────
if st.button("🔍 Analyse My Symptoms", use_container_width=True):

    # Score mapping
    freq_score = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4}
    trigger_score = {"No": 0, "A little": 1, "Yes, much worse": 2, "Yes, much better": 2}
    severity_score = {"No symptoms": 0, "Mild": 1, "Moderate": 2, "Severe": 3, "Unbearable": 4}

    # Base symptom score
    symptom_total = (
        freq_score[sneezing] +
        freq_score[itchy_eyes] +
        freq_score[runny_nose] +
        freq_score[itchy_throat] +
        freq_score[skin_rash] +
        freq_score[breathing] +
        freq_score[fatigue] +
        freq_score[headache]
    )

    # Trigger score
    trigger_total = (
        trigger_score.get(worse_wind, 0) +
        trigger_score.get(better_rain, 0) +
        trigger_score.get(worse_outside, 0) +
        trigger_score.get(better_inside, 0) +
        trigger_score.get(worse_morning, 0)
    )

    # Overall allergy likelihood
    overall = symptom_total + trigger_total + severity_score[severity]
    max_score = 32
    likelihood = min(int((overall / max_score) * 100), 100)

    # Pollen type matching based on months
    pollen_months = {
        "Hazel":   ["January", "February", "March"],
        "Alder":   ["February", "March", "April"],
        "Birch":   ["March", "April", "May"],
        "Grass":   ["May", "June", "July", "August"],
        "Mugwort": ["July", "August", "September"],
    }

    pollen_scores = {}
    for pollen, months in pollen_months.items():
        match = len(set(worst_months) & set(months))
        base = (match / max(len(months), 1)) * 60
        # Add symptom boost
        if freq_score[sneezing] >= 2:      base += 10
        if freq_score[itchy_eyes] >= 2:    base += 10
        if freq_score[runny_nose] >= 2:    base += 10
        if worse_wind == "Yes, much worse": base += 5
        if better_rain == "Yes, much better": base += 5
        pollen_scores[pollen] = min(int(base), 99)

    # Sort by score
    sorted_pollens = sorted(pollen_scores.items(), key=lambda x: x[1], reverse=True)

    # ── Display Results ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔬 Your Results")

    # Overall likelihood
    if likelihood < 20:
        st.success(f"**✅ Low likelihood of pollen allergy ({likelihood}%)**\n\nYour symptoms don't strongly suggest a pollen allergy. They could be caused by other factors like a cold or dust allergy.")
    elif likelihood < 50:
        st.warning(f"**🟡 Moderate likelihood of pollen allergy ({likelihood}%)**\n\nSome of your symptoms suggest a possible pollen allergy. Consider speaking to a doctor.")
    elif likelihood < 75:
        st.error(f"**🔴 High likelihood of pollen allergy ({likelihood}%)**\n\nYour symptoms strongly suggest a pollen allergy. We recommend consulting a doctor or allergist.")
    else:
        st.error(f"**🟣 Very high likelihood of pollen allergy ({likelihood}%)**\n\nYour symptoms are very consistent with a pollen allergy. Please consult a doctor as soon as possible.")

    st.divider()

    # Pollen type breakdown
    st.subheader("🌿 Which Pollen Are You Most Likely Allergic To?")

    for pollen, score in sorted_pollens:
        if score > 0:
            if score >= 70:
                emoji = "🔴"
                label = "High match"
            elif score >= 40:
                emoji = "🟡"
                label = "Moderate match"
            else:
                emoji = "🟢"
                label = "Low match"

            col_name, col_bar = st.columns([1, 3])
            with col_name:
                st.markdown(f"**{emoji} {pollen}**\n\n{label}")
            with col_bar:
                st.progress(score)
                st.caption(f"{score}% match")

    st.divider()

    # Severity assessment
    st.subheader("📊 Severity Assessment")
    sev_map = {
        "No symptoms": ("🟢", "No treatment needed"),
        "Mild": ("🟡", "Over-the-counter antihistamines may help"),
        "Moderate": ("🟠", "Consider seeing a doctor for prescription medication"),
        "Severe": ("🔴", "Strongly recommend seeing a doctor or allergist"),
        "Unbearable": ("🟣", "Please see a doctor as soon as possible — immunotherapy may help"),
    }
    sev_emoji, sev_advice = sev_map[severity]
    st.info(f"{sev_emoji} **Severity: {severity}**\n\n💡 {sev_advice}")

    st.divider()

    # Recommendations
    st.subheader("💊 Recommendations")

    top_pollen = sorted_pollens[0][0] if sorted_pollens else "Birch"
    top_score = sorted_pollens[0][1] if sorted_pollens else 0

    if likelihood >= 50:
        st.success(
            f"**Based on your results:**\n\n"
            f"1. 🩺 See a doctor or allergist for a proper allergy test\n"
            f"2. 💊 Ask about antihistamines like Cetirizine or Loratadine\n"
            f"3. 📅 Be extra careful during **{', '.join(pollen_months.get(top_pollen, []))}** (peak season for {top_pollen})\n"
            f"4. 🌬️ Check our **Home page** for daily pollen forecasts\n"
            f"5. 🎯 Set up your **Personalized Score** with {top_pollen} as your main allergy"
        )
    else:
        st.success(
            "**Based on your results:**\n\n"
            "1. 🩺 If symptoms persist, see a doctor to rule out other causes\n"
            "2. 🌬️ Keep an eye on our **Home page** for pollen forecasts\n"
            "3. 📝 Take note of when symptoms appear to track patterns"
        )

    st.divider()

    # Printable report
    st.subheader("📋 Your Report Summary")
    st.caption("You can screenshot this and show it to your doctor!")

    st.code(f"""
BLESSYOU ALLERGY ASSESSMENT REPORT
Date: {datetime.now().strftime("%d %B %Y")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERALL LIKELIHOOD: {likelihood}%
SEVERITY: {severity}
YEARS OF SYMPTOMS: {years_suffering}

WORST MONTHS: {', '.join(worst_months) if worst_months else 'Not specified'}

POLLEN MATCHES:
{chr(10).join([f"  • {p}: {s}% match" for p, s in sorted_pollens])}

MAIN SYMPTOMS:
  • Sneezing: {sneezing}
  • Itchy eyes: {itchy_eyes}
  • Runny nose: {runny_nose}
  • Itchy throat: {itchy_throat}

TRIGGERS:
  • Worse on windy days: {worse_wind}
  • Better when raining: {better_rain}
  • Better indoors: {better_inside}

⚠️ This is NOT a medical diagnosis.
   Please consult a qualified doctor.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
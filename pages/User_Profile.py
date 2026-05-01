# user_profile.py — shared across all pages via st.session_state

import streamlit as st

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

DEFAULT_PROFILE = {
    "city": "Zürich",
    "pollens": [],
    "sensitivities": {},
    "age_group": "12–65",
    "asthma": "No",
    "medication": "No medication",
    "hours_outside": 2,
    "risk_score": None,
    "risk_badge": None,
    "setup_done": False,
    "quiz_done": False,   # ← make sure this line is there
}

def init_profile():
    if "profile" not in st.session_state:
        st.session_state["profile"] = DEFAULT_PROFILE.copy()

def get_profile():
    init_profile()
    return st.session_state["profile"]

def set_profile(updates: dict):
    init_profile()
    st.session_state["profile"].update(updates)

def profile_banner():
    p = get_profile()
    if not p["setup_done"] and not p["quiz_done"]:
        st.info(
            "👤 **Your profile is not set up yet!** "
            "Answer the **🌿 Allergy Quiz** to discover your allergies, "
            "or visit the **🏠 Home** page to set up your profile manually."
        )
        return
    pollens_str = ", ".join(p["pollens"]) if p["pollens"] else "None selected"
    badge       = p["risk_badge"] or "Not calculated yet"
    cols = st.columns([2, 2, 2, 2])
    with cols[0]:
        st.caption("📍 Your city")
        st.markdown(f"**{p['city']}**")
    with cols[1]:
        st.caption("🌿 Your allergies")
        st.markdown(f"**{pollens_str}**")
    with cols[2]:
        st.caption("🎯 Today's risk")
        st.markdown(f"**{badge}**")
    with cols[3]:
        st.caption("💊 Medication")
        st.markdown(f"**{p['medication']}**")

def sensitivity_mult(sensitivity):
    return {"Low": 0.5, "Medium": 1.0, "High": 1.5}[sensitivity]

def get_level(value, thresholds, mult=1.0):
    import numpy as np
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
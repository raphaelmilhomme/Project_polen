import streamlit as st
import numpy as np

st.set_page_config(page_title="Risk Score", page_icon="🎯")

st.title("🎯 Your Personalized Risk Score")
st.caption("A score calculated from your pollen levels, sensitivity, and recent reactions.")

print("hello")

THRESHOLDS = {
    "Birch":   [1, 10,  50, 200],
    "Grass":   [1, 10,  50, 200],
    "Mugwort": [1,  5,  20,  80],
    "Hazel":   [1, 10,  50, 150],
    "Alder":   [1, 10,  50, 150],
}

LEVEL_ORDER = ["none", "low", "moderate", "high", "very high"]

level_scores = {
    "none":      0,
    "low":       2,
    "moderate":  5,
    "high":      7,
    "very high": 10,
}

def sensitivity_mult(sensitivity):
    return {"Low": 0.5, "Medium": 1.0, "High": 1.5}[sensitivity]

def get_level(value, thresholds, mult=1.0):
    if value is None or np.isnan(float(value)):
        return "none"
    v = float(value) * mult
    if v < thresholds[0]:   return "none"
    elif v < thresholds[1]: return "low"
    elif v < thresholds[2]: return "moderate"
    elif v < thresholds[3]: return "high"
    else:                   return "very high"

st.divider()

# User inputs
selected_pollens = st.multiselect(
    "Your pollen allergies",
    options=list(THRESHOLDS.keys()),
    default=["Birch", "Grass"],
)

sensitivity = st.select_slider(
    "Your sensitivity level",
    options=["Low", "Medium", "High"],
    value="Medium",
)

had_reactions = st.radio(
    "Have you had allergy reactions in the past 3 days?",
    options=["No", "Mild", "Strong"],
    horizontal=True,
)

st.divider()

# Manual pollen input
st.subheader("Enter today's pollen levels")
st.caption("You can find these on the Home page 👈")

pollen_values = {}
cols = st.columns(len(selected_pollens)) if selected_pollens else []
for i, pollen in enumerate(selected_pollens):
    with cols[i]:
        pollen_values[pollen] = st.number_input(
            f"{pollen} (gr/m³)",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

st.divider()

if selected_pollens:
    mult = sensitivity_mult(sensitivity)
    history_weight = {"No": 1.0, "Mild": 1.2, "Strong": 1.5}[had_reactions]

    pollen_levels = {
        p: get_level(pollen_values[p], THRESHOLDS[p], mult)
        for p in selected_pollens
    }

    raw_scores = [level_scores[pollen_levels[p]] for p in selected_pollens]
    avg_raw = sum(raw_scores) / len(raw_scores)
    final_score = min(round(avg_raw * history_weight, 1), 10.0)

    if final_score <= 2:
        emoji = "🟢"; label = "Very Low Risk"
    elif final_score <= 4:
        emoji = "🟡"; label = "Low Risk"
    elif final_score <= 6:
        emoji = "🟠"; label = "Moderate Risk"
    elif final_score <= 8:
        emoji = "🔴"; label = "High Risk"
    else:
        emoji = "🟣"; label = "Very High Risk"

    col_score, col_explain = st.columns([1, 2])
    with col_score:
        st.metric(
            label=f"{emoji} Personal Risk Score",
            value=f"{final_score} / 10",
            delta=label,
        )
        st.progress(int(final_score * 10))

    with col_explain:
        st.info(
            f"**How your score was calculated:**\n\n"
            f"- Pollen levels: {', '.join([f'{p} ({pollen_levels[p]})' for p in selected_pollens])}\n"
            f"- Sensitivity: **{sensitivity}**\n"
            f"- Recent reactions: **{had_reactions}**\n"
            f"- Final score: **{final_score}/10**"
        )
else:
    st.info("👈 Select at least one pollen type above to calculate your score.")
    
import streamlit as st
from user_profile import init_profile, get_profile, set_profile

st.set_page_config(page_title="Allergy Quiz", page_icon="🌿", layout="wide")

init_profile()
p = get_profile()

# ── Quiz questions ─────────────────────────────────────────────────────────────
# Each question points to specific pollens if answered Yes
QUESTIONS = [
    {
        "question": "Do you sneeze a lot in spring, between March and May?",
        "pollens":  ["Birch", "Hazel", "Alder"],
    },
    {
        "question": "Do you sneeze a lot in summer, between June and August?",
        "pollens":  ["Grass"],
    },
    {
        "question": "Do you have symptoms very early in the year, in January or February?",
        "pollens":  ["Hazel"],
    },
    {
        "question": "Do your eyes get itchy and watery when you are outside?",
        "pollens":  ["Birch", "Grass"],
    },
    {
        "question": "Does your nose run a lot when you are outdoors?",
        "pollens":  ["Birch", "Grass", "Mugwort"],
    },
    {
        "question": "Do you get a scratchy or itchy throat when you are outside?",
        "pollens":  ["Grass", "Mugwort"],
    },
    {
        "question": "Do your symptoms get worse on windy days?",
        "pollens":  ["Birch", "Grass", "Hazel", "Alder"],
    },
    {
        "question": "Do you feel better when you stay indoors or on rainy days?",
        "pollens":  ["Birch", "Grass", "Mugwort", "Hazel", "Alder"],
    },
    {
        "question": "Do you react when you are near freshly cut grass or open fields?",
        "pollens":  ["Grass"],
    },
    {
        "question": "Do you react when you are near trees or walking in a forest?",
        "pollens":  ["Birch", "Alder", "Hazel"],
    },
    {
        "question": "Do you have symptoms in late summer, between July and September?",
        "pollens":  ["Mugwort"],
    },
    {
        "question": "Do you sometimes react when eating raw apples, cherries or peaches?",
        "pollens":  ["Birch"],
    },
]

POLLEN_INFO = {
    "Birch":   {"emoji": "🌳", "season": "Mar–May",  "desc": "Very common tree pollen. Causes strong eye, nose and throat symptoms."},
    "Grass":   {"emoji": "🌾", "season": "Jun–Aug",  "desc": "Most widespread pollen in Switzerland. Affects many people in summer."},
    "Mugwort": {"emoji": "🌿", "season": "Jul–Sep",  "desc": "Late summer pollen found along roadsides and in gardens."},
    "Hazel":   {"emoji": "🌰", "season": "Jan–Mar",  "desc": "One of the earliest pollens — starts in winter before spring begins."},
    "Alder":   {"emoji": "🌲", "season": "Feb–Apr",  "desc": "Early spring tree pollen, often appears alongside hazel."},
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌿 Allergy Quiz")
st.markdown("### Find out which pollens you might be allergic to!")
st.caption("Answer these simple questions based on how you typically feel. This is not a medical diagnosis — always consult a doctor for confirmation.")
st.divider()

# ── If quiz already done ───────────────────────────────────────────────────────
if p["quiz_done"] and p["pollens"]:
    st.success(
        f"✅ You already completed the quiz!\n\n"
        f"Your likely allergies are: **{', '.join(p['pollens'])}**\n\n"
        f"These are saved and used on the 🏠 Home page."
    )
    if st.button("🔄 Retake the quiz"):
        set_profile({"quiz_done": False, "pollens": [], "sensitivities": {}})
        st.rerun()
    st.divider()

# ── Quiz ───────────────────────────────────────────────────────────────────────
if not p["quiz_done"]:
    st.subheader("👤 A bit about you")
    col1, col2 = st.columns(2)
    with col1:
        quiz_city = st.selectbox(
            "📍 Your city",
            options=["Zürich", "Bern", "Basel", "Geneva", "Lausanne", "Luzern",
                     "St. Gallen", "Lugano", "Sion", "Davos", "Neuchâtel",
                     "Aarau", "Chur", "Frauenfeld", "Bellinzona"],
        )
        quiz_age = st.radio(
            "🎂 Your age group",
            ["Under 12", "12–65", "Over 65"],
            index=1, horizontal=True,
        )
    with col2:
        quiz_asthma = st.radio(
            "🫁 Do you have asthma or breathing issues?",
            ["No", "Yes"], index=0, horizontal=True,
        )

    st.divider()
    st.subheader("🤧 Your Symptoms")
    st.caption("Just answer Yes, No or Not sure for each question.")

    answers = {}
    for i, q in enumerate(QUESTIONS):
        st.markdown(f"**{i+1}. {q['question']}**")
        answers[i] = st.radio(
            f"q{i}",
            ["No", "Yes", "Not sure"],
            index=0,
            horizontal=True,
            key=f"q_{i}",
            label_visibility="collapsed",
        )
        st.markdown("")

    st.divider()

    if st.button("🌿 Get my results!", use_container_width=True):
        # Count pollen scores
        pollen_scores = {"Birch": 0, "Grass": 0, "Mugwort": 0, "Hazel": 0, "Alder": 0}
        for i, q in enumerate(QUESTIONS):
            if answers[i] == "Yes":
                for pollen in q["pollens"]:
                    pollen_scores[pollen] += 1

        likely_pollens  = [p_ for p_, score in pollen_scores.items() if score >= 2]
        possible_pollens = [p_ for p_, score in pollen_scores.items() if score == 1]

        if not likely_pollens and possible_pollens:
            likely_pollens = possible_pollens

        default_sensitivity = "High" if quiz_asthma == "Yes" else "Medium"
        sensitivities = {p_: default_sensitivity for p_ in likely_pollens}

        set_profile({
            "city":          quiz_city,
            "pollens":       likely_pollens,
            "sensitivities": sensitivities,
            "age_group":     quiz_age,
            "asthma":        quiz_asthma,
            "quiz_done":     True,
            "setup_done":    True,
        })
        st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────
if p["quiz_done"]:
    st.subheader("🎯 Your Results")

    if p["pollens"]:
        st.markdown("#### You are likely allergic to:")

        cols = st.columns(len(p["pollens"]))
        for i, pollen in enumerate(p["pollens"]):
            info = POLLEN_INFO.get(pollen, {})
            with cols[i]:
                st.metric(
                    label=f"{info.get('emoji', '🌿')} {pollen}",
                    value=info.get("season", ""),
                )
                st.caption(info.get("desc", ""))

        st.divider()

        sensitivity = "High" if p["asthma"] == "Yes" else "Medium"
        st.info(
            f"**Your sensitivity:** {sensitivity}\n\n"
            f"{'Since you have asthma, your sensitivity is set to High.' if p['asthma'] == 'Yes' else 'You can adjust this anytime on the Home page.'}"
        )

        st.success(
            "✅ **Your results are saved!**\n\n"
            "Go to the **🏠 Home** page to see your personalised pollen levels and risk score!"
        )

        if p["asthma"] == "Yes":
            st.warning(
                "⚠️ You mentioned breathing issues. This could be pollen-induced asthma. "
                "Please consult a doctor for a proper diagnosis and treatment plan."
            )

    else:
        st.info(
            "🤔 No strong pollen allergy was detected based on your answers.\n\n"
            "This doesn't mean you don't have allergies — symptoms vary a lot. "
            "Consider seeing a doctor for an allergy test if you suspect you might be allergic."
        )

    st.divider()
    st.caption("🌿 BlessYou · This quiz is for informational purposes only and is not a medical diagnosis.")
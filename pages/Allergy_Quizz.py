import streamlit as st
from datetime import datetime
from user_profile import init_profile, get_profile, set_profile, profile_banner

st.set_page_config(page_title="Allergy Quiz", page_icon="🌿", layout="wide")

init_profile()
p = get_profile()

# ── Quiz questions ─────────────────────────────────────────────────────────────
# Each question has a list of pollens it points to if answered "Yes"
QUESTIONS = [
    {
        "question": "Do your symptoms (sneezing, runny nose, itchy eyes) get worse in spring, between March and May?",
        "hint":     "Birch and Hazel pollinate heavily in early spring.",
        "pollens":  ["Birch", "Hazel"],
    },
    {
        "question": "Do you sneeze a lot when you're near trees like birch, oak or alder?",
        "hint":     "Tree pollen is one of the most common allergy triggers in Switzerland.",
        "pollens":  ["Birch", "Alder"],
    },
    {
        "question": "Do your symptoms get worse in summer, between May and August?",
        "hint":     "Grass pollen peaks in early summer and is very widespread.",
        "pollens":  ["Grass"],
    },
    {
        "question": "Do you sneeze or get itchy eyes when you're near freshly cut grass or in open fields?",
        "hint":     "Grass pollen is the most common pollen allergy worldwide.",
        "pollens":  ["Grass"],
    },
    {
        "question": "Do your symptoms continue or get worse in late summer, between July and September?",
        "hint":     "Mugwort pollinates in late summer and is often missed.",
        "pollens":  ["Mugwort"],
    },
    {
        "question": "Do you react near wild plants, herbs or roadsides in summer?",
        "hint":     "Mugwort grows along roadsides and in gardens.",
        "pollens":  ["Mugwort"],
    },
    {
        "question": "Do you have symptoms very early in the year, in January or February?",
        "hint":     "Hazel is one of the first trees to pollinate, even in winter.",
        "pollens":  ["Hazel"],
    },
    {
        "question": "Do your symptoms get worse on windy days?",
        "hint":     "Wind carries pollen much further, increasing your exposure.",
        "pollens":  ["Birch", "Grass", "Hazel", "Alder"],
    },
    {
        "question": "Do you feel better on rainy days?",
        "hint":     "Rain washes pollen out of the air, reducing your exposure.",
        "pollens":  ["Birch", "Grass", "Mugwort", "Hazel", "Alder"],
    },
    {
        "question": "Do your eyes itch and water a lot, more than your nose?",
        "hint":     "Eye symptoms are especially common with grass and birch pollen.",
        "pollens":  ["Grass", "Birch"],
    },
    {
        "question": "Do you sometimes have trouble breathing or feel tightness in your chest during pollen season?",
        "hint":     "This can be a sign of pollen-induced asthma. Consider seeing a doctor.",
        "pollens":  ["Grass", "Birch", "Mugwort"],
    },
    {
        "question": "Do you react when you eat certain raw fruits like apples, cherries or peaches?",
        "hint":     "This is called oral allergy syndrome and is linked to birch pollen cross-reactivity.",
        "pollens":  ["Birch"],
    },
]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌿 Allergy Quiz")
st.markdown("### Find out which pollens you might be allergic to!")
st.caption("Answer these questions based on your typical symptoms. This is not a medical diagnosis — always consult a doctor for confirmation.")
st.divider()

profile_banner()
st.divider()

# ── If quiz already done, show results and option to redo ──────────────────────
if p["quiz_done"] and p["pollens"]:
    st.success(
        f"✅ You already completed the quiz! Your likely allergies are: **{', '.join(p['pollens'])}**\n\n"
        f"These have been saved to your profile and are used on the Home page."
    )
    if st.button("🔄 Retake the quiz", use_container_width=False):
        set_profile({"quiz_done": False, "pollens": [], "sensitivities": {}})
        st.rerun()
    st.divider()

# ── Quiz form ──────────────────────────────────────────────────────────────────
if not p["quiz_done"]:
    st.subheader("👤 First, a bit about you")

    col1, col2 = st.columns(2)
    with col1:
        quiz_city = st.selectbox(
            "📍 Your city",
            options=["Zürich", "Bern", "Basel", "Geneva", "Lausanne", "Luzern",
                     "St. Gallen", "Lugano", "Sion", "Davos", "Neuchâtel",
                     "Aarau", "Chur", "Frauenfeld", "Bellinzona"],
            index=0,
        )
        quiz_age = st.radio(
            "🎂 Your age group",
            ["Under 12", "12–65", "Over 65"],
            index=1, horizontal=True,
        )
    with col2:
        quiz_asthma = st.radio(
            "🫁 Do you have asthma or respiratory issues?",
            ["No", "Yes"], index=0, horizontal=True,
        )
        quiz_medication = st.radio(
            "💊 Are you currently taking allergy medication?",
            ["No medication", "Antihistamines (e.g. Cetirizine)", "Nasal spray", "Both antihistamines + nasal spray"],
            index=0,
        )

    st.divider()
    st.subheader("🤧 Your Symptoms")
    st.caption("Answer Yes or No to each question based on how you typically feel during pollen season.")

    answers = {}
    for i, q in enumerate(QUESTIONS):
        st.markdown(f"**{i+1}. {q['question']}**")
        st.caption(f"💡 {q['hint']}")
        answers[i] = st.radio(
            f"Answer {i+1}",
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

        # Pollens with at least 1 point are flagged
        # Pollens with 2+ points are strongly flagged
        likely_pollens  = [p_ for p_, score in pollen_scores.items() if score >= 2]
        possible_pollens = [p_ for p_, score in pollen_scores.items() if score == 1]

        # If nothing flagged strongly, use possible ones
        if not likely_pollens and possible_pollens:
            likely_pollens = possible_pollens

        # Default sensitivity: High if asthma, Medium otherwise
        default_sensitivity = "High" if quiz_asthma == "Yes" else "Medium"
        sensitivities = {p_: default_sensitivity for p_ in likely_pollens}

        # Save to profile
        set_profile({
            "city":          quiz_city,
            "pollens":       likely_pollens,
            "sensitivities": sensitivities,
            "age_group":     quiz_age,
            "asthma":        quiz_asthma,
            "medication":    quiz_medication,
            "quiz_done":     True,
            "setup_done":    True,
        })

        st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────
if p["quiz_done"]:
    st.subheader("🎯 Your Quiz Results")

    if p["pollens"]:
        st.markdown("#### Based on your symptoms, you are likely allergic to:")
        cols = st.columns(len(p["pollens"]))
        pollen_info = {
            "Birch":   {"emoji": "🌳", "season": "Mar–May",  "desc": "Very common. Causes strong eye and nose symptoms."},
            "Grass":   {"emoji": "🌾", "season": "May–Aug",  "desc": "Most widespread pollen. Affects many people."},
            "Mugwort": {"emoji": "🌿", "season": "Jul–Sep",  "desc": "Late summer pollen. Often causes skin reactions too."},
            "Hazel":   {"emoji": "🌰", "season": "Jan–Mar",  "desc": "One of the earliest pollens. Starts in winter."},
            "Alder":   {"emoji": "🌲", "season": "Feb–Apr",  "desc": "Early spring pollen, often alongside hazel."},
        }
        for i, pollen in enumerate(p["pollens"]):
            info = pollen_info.get(pollen, {})
            with cols[i]:
                st.metric(
                    label=f"{info.get('emoji', '🌿')} {pollen}",
                    value=info.get("season", ""),
                )
                st.caption(info.get("desc", ""))

        st.divider()

        # Sensitivity result
        sensitivity = "High" if p["asthma"] == "Yes" else "Medium"
        st.info(
            f"**Your sensitivity has been set to: {sensitivity}**\n\n"
            f"{'Since you have asthma, your sensitivity is set to High.' if p['asthma'] == 'Yes' else 'You can adjust this on the Home page.'}"
        )

        st.success(
            "✅ **Your results have been saved!**\n\n"
            "Go to the **🏠 Home** page to see your personalised pollen levels and risk score. "
            "Your allergies will be pre-selected automatically!"
        )

        # Warning if chest symptoms
        chest_q = next((i for i, q in enumerate(QUESTIONS) if "breathing" in q["question"]), None)
        if chest_q is not None and "answers" in dir() and answers.get(chest_q) == "Yes":
            st.warning(
                "⚠️ You mentioned breathing difficulties. This could be pollen-induced asthma. "
                "Please consult a doctor for a proper diagnosis."
            )

    else:
        st.info(
            "🤔 Based on your answers, no strong pollen allergy was detected. "
            "This doesn't mean you don't have allergies — symptoms can vary. "
            "Consider consulting a doctor for an allergy test."
        )

    st.divider()
    st.caption("🌿 BlessYou · This quiz is for informational purposes only and is not a medical diagnosis.")
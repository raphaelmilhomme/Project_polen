import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Community", page_icon="🤝", layout="wide")

# ── Initialize session state ───────────────────────────────────────────────────
if "community_tips" not in st.session_state:
    st.session_state.community_tips = [
        {"city": "Zürich", "date": "28 Apr", "tip": "Wearing sunglasses helps protect your eyes from pollen! 😎", "votes": 12},
        {"city": "Bern", "date": "28 Apr", "tip": "Showering after being outside removes pollen from hair and skin!", "votes": 8},
        {"city": "Geneva", "date": "28 Apr", "tip": "Keep windows closed between 6-10am when pollen is highest.", "votes": 15},
        {"city": "Zürich", "date": "28 Apr", "tip": "Local tip: avoid Zürichsee promenade on windy days — very high birch!", "votes": 6},
        {"city": "Basel", "date": "28 Apr", "tip": "Rinsing your nose with saline spray after being outside really helps!", "votes": 9},
    ]

if "community_reports" not in st.session_state:
    st.session_state.community_reports = {
        "Zürich": {"😊 Fine": 5, "😐 Mild": 8, "😰 Bad": 12, "😭 Unbearable": 3},
        "Bern": {"😊 Fine": 3, "😐 Mild": 6, "😰 Bad": 4, "😭 Unbearable": 1},
        "Basel": {"😊 Fine": 7, "😐 Mild": 4, "😰 Bad": 3, "😭 Unbearable": 0},
        "Geneva": {"😊 Fine": 9, "😐 Mild": 5, "😰 Bad": 2, "😭 Unbearable": 1},
    }

if "sightings" not in st.session_state:
    st.session_state.sightings = [
        {"city": "Zürich", "pollen": "Birch", "date": "28 Apr", "description": "Heavy pollen cloud near Zürichsee!"},
        {"city": "Bern", "pollen": "Grass", "date": "28 Apr", "description": "Lots of grass pollen in Bern parks today."},
    ]

if "weekly_discussion" not in st.session_state:
    st.session_state.weekly_discussion = [
        {"user": "Zürich", "date": "28 Apr", "comment": "Taking antihistamines the night before really helps me!"},
        {"user": "Bern", "date": "28 Apr", "comment": "I always check the BlessYou forecast before planning outdoor activities."},
    ]

if "voted_tips" not in st.session_state:
    st.session_state.voted_tips = set()

if "user_reported" not in st.session_state:
    st.session_state.user_reported = False

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤝 BlessYou Community")
st.markdown("### Connect with other allergy sufferers across Switzerland!")
st.divider()

# ── City selector ──────────────────────────────────────────────────────────────
STATIONS = ["Zürich", "Bern", "Basel", "Geneva", "Lausanne", "Luzern",
            "St. Gallen", "Lugano", "Sion", "Davos"]

selected_city = st.selectbox("📍 Your city", options=STATIONS)

st.divider()

# ── Section 1: Today's Community Report ───────────────────────────────────────
st.subheader("🌡️ How Is Everyone Feeling Today?")
st.caption("Report how your allergies are today and see how others in your city feel!")

# Initialize city if not exists
if selected_city not in st.session_state.community_reports:
    st.session_state.community_reports[selected_city] = {
        "😊 Fine": 0, "😐 Mild": 0, "😰 Bad": 0, "😭 Unbearable": 0
    }

city_reports = st.session_state.community_reports[selected_city]
total_reports = sum(city_reports.values())

# Show current results
if total_reports > 0:
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    for i, (feeling, count) in enumerate(city_reports.items()):
        pct = int((count / total_reports) * 100) if total_reports > 0 else 0
        with cols[i]:
            st.metric(label=feeling, value=f"{pct}%", delta=f"{count} reports")
    st.caption(f"Based on {total_reports} reports in {selected_city} today")
else:
    st.info("No reports yet for this city today — be the first!")

# Report your feeling
if not st.session_state.user_reported:
    st.markdown("**How are YOUR allergies today?**")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("😊 Fine", use_container_width=True):
            st.session_state.community_reports[selected_city]["😊 Fine"] += 1
            st.session_state.user_reported = True
            st.rerun()
    with col_b:
        if st.button("😐 Mild", use_container_width=True):
            st.session_state.community_reports[selected_city]["😐 Mild"] += 1
            st.session_state.user_reported = True
            st.rerun()
    with col_c:
        if st.button("😰 Bad", use_container_width=True):
            st.session_state.community_reports[selected_city]["😰 Bad"] += 1
            st.session_state.user_reported = True
            st.rerun()
    with col_d:
        if st.button("😭 Unbearable", use_container_width=True):
            st.session_state.community_reports[selected_city]["😭 Unbearable"] += 1
            st.session_state.user_reported = True
            st.rerun()
else:
    st.success("✅ Thanks for your report! Come back tomorrow to report again.")

st.divider()

# ── Section 2: City-specific Tips ─────────────────────────────────────────────
st.subheader("💡 Community Tips")
st.caption("Share and discover tips from allergy sufferers across Switzerland!")

# Filter by city
show_all = st.toggle("Show tips from all cities", value=False)

if show_all:
    filtered_tips = st.session_state.community_tips
else:
    filtered_tips = [t for t in st.session_state.community_tips if t["city"] == selected_city]
    if not filtered_tips:
        st.info(f"No tips yet for {selected_city} — be the first to share!")

# Show tips with voting
for i, tip in enumerate(filtered_tips):
    col_tip, col_vote = st.columns([4, 1])
    with col_tip:
        st.markdown(f"💬 **{tip['city']}** · {tip['date']}")
        st.markdown(f"{tip['tip']}")
    with col_vote:
        vote_key = f"vote_{i}"
        if vote_key not in st.session_state.voted_tips:
            if st.button(f"👍 {tip['votes']}", key=f"btn_{i}"):
                st.session_state.community_tips[i]["votes"] += 1
                st.session_state.voted_tips.add(vote_key)
                st.rerun()
        else:
            st.markdown(f"✅ **{tip['votes']}** votes")
    st.markdown("---")

# Add new tip
st.markdown("**Share your own tip!**")
with st.form("tip_form"):
    new_tip = st.text_input(f"Your tip for {selected_city}:")
    submitted = st.form_submit_button("Share tip 💬", use_container_width=True)
    if submitted and new_tip:
        st.session_state.community_tips.append({
            "city": selected_city,
            "date": datetime.now().strftime("%d %b"),
            "tip": new_tip,
            "votes": 0,
        })
        st.success("✅ Tip shared! Thank you!")
        st.rerun()

st.divider()

# ── Section 3: Pollen Sightings ────────────────────────────────────────────────
st.subheader("🌿 Pollen Sightings")
st.caption("Spotted a lot of pollen in your area? Report it!")

# Show existing sightings
for sighting in st.session_state.sightings[-5:]:
    st.markdown(
        f"🌿 **{sighting['city']}** · {sighting['date']} · "
        f"_{sighting['pollen']} pollen_: {sighting['description']}"
    )

# Report new sighting
with st.form("sighting_form"):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sighting_pollen = st.selectbox("Which pollen?", ["Birch", "Grass", "Mugwort", "Hazel", "Alder"])
    with col_s2:
        sighting_desc = st.text_input("Describe what you saw:")
    submitted_sighting = st.form_submit_button("Report sighting 🌿", use_container_width=True)
    if submitted_sighting and sighting_desc:
        st.session_state.sightings.append({
            "city": selected_city,
            "pollen": sighting_pollen,
            "date": datetime.now().strftime("%d %b"),
            "description": sighting_desc,
        })
        st.success("✅ Sighting reported! Thank you!")
        st.rerun()

st.divider()

# ── Section 4: Weekly Discussion ──────────────────────────────────────────────
st.subheader("💬 Weekly Discussion")

week_num = datetime.now().isocalendar()[1]
questions = [
    "What's your best tip for surviving birch season? 🌳",
    "Which antihistamine works best for you? 💊",
    "What outdoor activities do you avoid during pollen season? 🏃",
    "How do you track your allergy symptoms? 📊",
]
weekly_question = questions[week_num % len(questions)]

st.info(f"**This week's question:** {weekly_question}")

# Show existing comments
for comment in st.session_state.weekly_discussion[-10:]:
    st.markdown(f"💬 **{comment['user']}** · {comment['date']}: {comment['comment']}")

# Add comment
with st.form("discussion_form"):
    new_comment = st.text_input("Share your answer:")
    submitted_comment = st.form_submit_button("Post comment 💬", use_container_width=True)
    if submitted_comment and new_comment:
        st.session_state.weekly_discussion.append({
            "user": selected_city,
            "date": datetime.now().strftime("%d %b"),
            "comment": new_comment,
        })
        st.success("✅ Comment posted!")
        st.rerun()

st.divider()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.caption("🤝 BlessYou Community · Together we breathe easier 🌿")


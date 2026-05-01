import streamlit as st
from datetime import datetime
from supabase import create_client
from user_profile import init_profile, get_profile, profile_banner

st.set_page_config(page_title="Community", page_icon="🤝", layout="wide")

init_profile()
p = get_profile()

# ── Supabase ───────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://vcnsrqdfrccfdlzmbume.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjbnNycWRmcmNjZmRsem1idW1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc1NDQ3NDUsImV4cCI6MjA5MzEyMDc0NX0.tIJE5YqXy1n9VBwzx--RYIBK2MlQBnFxiIMg_FqQSTY"

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

def fetch_tips():
    try:
        return supabase.table("tips").select("*").order("id", desc=False).execute().data
    except:
        return []

def fetch_reports(city):
    try:
        return supabase.table("reports").select("*").eq("city", city).execute().data
    except:
        return []

def fetch_sightings():
    try:
        return supabase.table("sightings").select("*").order("id", desc=False).execute().data
    except:
        return []

def fetch_comments():
    try:
        return supabase.table("comments").select("*").order("id", desc=False).execute().data
    except:
        return []

# ── Profile info ───────────────────────────────────────────────────────────────
user_badge    = p["risk_badge"] or ""
user_pollens  = ", ".join(p["pollens"]) if p["pollens"] else ""
profile_ready = p["setup_done"]

# City comes from profile — no city selector here
selected_city = p["city"]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤝 BlessYou Community")
st.markdown("### Connect with other allergy sufferers across Switzerland!")
st.divider()

profile_banner()

# Show which city is being used
st.caption(f"📍 Showing community data for **{selected_city}** — change your city on the 🏠 Home page or in the 🌿 Allergy Quiz.")
st.divider()

# ── Section 1: Community Report ───────────────────────────────────────────────
st.subheader("🌡️ How Is Everyone Feeling Today?")
st.caption("Report how your allergies are today and see how others in your city feel!")

city_reports = fetch_reports(selected_city)
feelings     = ["😊 Fine", "😐 Mild", "😰 Bad", "😭 Unbearable"]
counts       = {f: sum(1 for r in city_reports if r["feeling"] == f) for f in feelings}
total        = sum(counts.values())

if total > 0:
    col1, col2, col3, col4 = st.columns(4)
    for i, feeling in enumerate(feelings):
        pct = int((counts[feeling] / total) * 100)
        with [col1, col2, col3, col4][i]:
            st.metric(label=feeling, value=f"{pct}%", delta=f"{counts[feeling]} reports")
    st.caption(f"Based on {total} reports in {selected_city} today")
else:
    st.info(f"No reports yet for {selected_city} today — be the first!")

if "user_reported" not in st.session_state:
    st.session_state.user_reported = False

if not st.session_state.user_reported:
    if profile_ready:
        st.markdown(f"**How are YOUR allergies today?** *(Your risk score: {user_badge})*")
    else:
        st.markdown("**How are YOUR allergies today?**")
    col_a, col_b, col_c, col_d = st.columns(4)
    for col, feeling in zip([col_a, col_b, col_c, col_d], feelings):
        with col:
            if st.button(feeling, use_container_width=True):
                try:
                    supabase.table("reports").insert({
                        "city":    selected_city,
                        "feeling": feeling,
                        "date":    datetime.now().strftime("%d %b"),
                    }).execute()
                    st.session_state.user_reported = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save: {e}")
else:
    st.success("✅ Thanks for your report! Come back tomorrow to report again.")

st.divider()

# ── Section 2: Community Tips ─────────────────────────────────────────────────
st.subheader("💡 Community Tips")
st.caption("Share and discover tips from allergy sufferers across Switzerland!")

show_all      = st.toggle("Show tips from all cities", value=False)
all_tips      = fetch_tips()
filtered_tips = all_tips if show_all else [t for t in all_tips if t["city"] == selected_city]

if not filtered_tips:
    st.info(f"No tips yet for {selected_city} — be the first to share!")

if "voted_tips" not in st.session_state:
    st.session_state.voted_tips = set()

for tip in filtered_tips:
    col_tip, col_vote = st.columns([4, 1])
    with col_tip:
        badge_str   = f" · {tip['badge']}"      if tip.get("badge")   else ""
        pollens_str = f" · 🌿 {tip['pollens']}" if tip.get("pollens") else ""
        st.markdown(f"💬 **{tip['city']}** · {tip['date']}{badge_str}{pollens_str}")
        st.markdown(f"{tip['tip']}")
    with col_vote:
        tip_id = str(tip["id"])
        if tip_id not in st.session_state.voted_tips:
            if st.button(f"👍 {tip['votes']}", key=f"vote_{tip_id}"):
                try:
                    supabase.table("tips").update({"votes": tip["votes"] + 1}).eq("id", tip["id"]).execute()
                    st.session_state.voted_tips.add(tip_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not update vote: {e}")
        else:
            st.markdown(f"✅ **{tip['votes']}** votes")
    st.markdown("---")

st.markdown("**Share your own tip!**")
with st.form("tip_form"):
    new_tip   = st.text_input(f"Your tip for {selected_city}:")
    submitted = st.form_submit_button("Share tip 💬", use_container_width=True)
    if submitted and new_tip:
        try:
            supabase.table("tips").insert({
                "city":    selected_city,
                "tip":     new_tip,
                "votes":   0,
                "date":    datetime.now().strftime("%d %b"),
                "badge":   user_badge   if profile_ready else "",
                "pollens": user_pollens if profile_ready else "",
            }).execute()
            st.success("✅ Tip shared!")
            st.rerun()
        except Exception as e:
            st.error(f"Could not save: {e}")

st.divider()

# ── Section 3: Pollen Sightings ────────────────────────────────────────────────
st.subheader("🌿 Pollen Sightings")
st.caption("Spotted a lot of pollen in your area? Report it!")

for sighting in fetch_sightings()[-10:]:
    badge_str = f" · {sighting['badge']}" if sighting.get("badge") else ""
    st.markdown(
        f"🌿 **{sighting['city']}** · {sighting['date']}{badge_str} · "
        f"_{sighting['pollen']} pollen_: {sighting['description']}"
    )

with st.form("sighting_form"):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sighting_pollen = st.selectbox("Which pollen?", ["Birch", "Grass", "Mugwort", "Hazel", "Alder"])
    with col_s2:
        sighting_desc = st.text_input("Describe what you saw:")
    if st.form_submit_button("Report sighting 🌿", use_container_width=True) and sighting_desc:
        try:
            supabase.table("sightings").insert({
                "city":        selected_city,
                "pollen":      sighting_pollen,
                "description": sighting_desc,
                "date":        datetime.now().strftime("%d %b"),
                "badge":       user_badge if profile_ready else "",
            }).execute()
            st.success("✅ Sighting reported!")
            st.rerun()
        except Exception as e:
            st.error(f"Could not save: {e}")

st.divider()

# ── Section 4: Weekly Discussion ──────────────────────────────────────────────
st.subheader("💬 Weekly Discussion")

week_num        = datetime.now().isocalendar()[1]
questions       = [
    "What's your best tip for surviving birch season? 🌳",
    "Which antihistamine works best for you? 💊",
    "What outdoor activities do you avoid during pollen season? 🏃",
    "How do you track your allergy symptoms? 📊",
]
weekly_question = questions[week_num % len(questions)]
st.info(f"**This week's question:** {weekly_question}")

for comment in fetch_comments()[-20:]:
    badge_str   = f" · {comment['badge']}"      if comment.get("badge")   else ""
    pollens_str = f" · 🌿 {comment['pollens']}" if comment.get("pollens") else ""
    st.markdown(f"💬 **{comment['city']}** · {comment['date']}{badge_str}{pollens_str}: {comment['comment']}")

with st.form("discussion_form"):
    new_comment = st.text_input("Share your answer:")
    if st.form_submit_button("Post comment 💬", use_container_width=True) and new_comment:
        try:
            supabase.table("comments").insert({
                "city":    selected_city,
                "comment": new_comment,
                "date":    datetime.now().strftime("%d %b"),
                "badge":   user_badge   if profile_ready else "",
                "pollens": user_pollens if profile_ready else "",
            }).execute()
            st.success("✅ Comment posted!")
            st.rerun()
        except Exception as e:
            st.error(f"Could not save: {e}")

st.divider()
st.caption("🤝 BlessYou Community · Together we breathe easier 🌿")
from user_profile import init_profile, get_profile, profile_banner
#importing the necessary libraries and functions from user_profile.py
 
st.set_page_config(page_title="Community", page_icon="🤝", layout="wide")
#setting up the streamlit page with title, logo and layout
 
init_profile()
p = get_profile()
#creating/initializing a user profile and storing it in p for easier access
 
# ── Supabase connection ────────────────────────────────────────────────────────
SUPABASE_URL = "https://vcnsrqdfrccfdlzmbume.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZjbnNycWRmcmNjZmRsem1idW1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc1NDQ3NDUsImV4cCI6MjA5MzEyMDc0NX0.tIJE5YqXy1n9VBwzx--RYIBK2MlQBnFxiIMg_FqQSTY"
#Supabase project URL and public API key used to connect to the database
 
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
#creates and caches the Supabase client so it is not recreated on every page reload
 
supabase = get_supabase()
#stores the Supabase client in a variable for easier access throughout the page
 
def fetch_tips():
    try:
        return supabase.table("tips").select("*").order("id", desc=False).execute().data
    except:
        return []
#reads all community tips from the database, ordered by submission time, returns empty list if it fails
 
def fetch_reports(city):
    try:
        return supabase.table("reports").select("*").eq("city", city).execute().data
    except:
        return []
#reads all feeling reports for a specific city from the database, returns empty list if it fails
 
def fetch_sightings():
    try:
        return supabase.table("sightings").select("*").order("id", desc=False).execute().data
    except:
        return []
#reads all pollen sightings from the database, ordered by submission time, returns empty list if it fails
 
def fetch_comments():
    try:
        return supabase.table("comments").select("*").order("id", desc=False).execute().data
    except:
        return []
#reads all weekly discussion comments from the database, ordered by submission time, returns empty list if it fails
 
user_badge    = p["risk_badge"] or ""
user_pollens  = ", ".join(p["pollens"]) if p["pollens"] else ""
profile_ready = p["setup_done"]
#reads the user's risk badge and allergies from the shared profile to attach to their posts
#profile_ready checks if the user has set up their profile, so we know whether to show their badge or not
 
selected_city = p["city"]
#city comes directly from the shared profile — no city selector on this page
#to change city, the user must go to the Home page or the Allergy Quiz
 
st.title("🤝 BlessYou Community")
st.markdown("### Connect with other allergy sufferers across Switzerland!")
st.divider()
#page header with title and subtitle
 
profile_banner() #shows a summary of the user's city, allergies, risk score and medication
st.caption(f"📍 Showing community data for **{selected_city}** — change your city on the 🏠 Home page or in the 🌿 Allergy Quiz.")
st.divider()
 
# ── Section 1: Community Report ───────────────────────────────────────────────
st.subheader("🌡️ How Is Everyone Feeling Today?")
st.caption("Report how your allergies are today and see how others in your city feel!")
 
city_reports = fetch_reports(selected_city) #gets all feeling reports for the selected city
feelings     = ["😊 Fine", "😐 Mild", "😰 Bad", "😭 Unbearable"]
counts       = {f: sum(1 for r in city_reports if r["feeling"] == f) for f in feelings}
total        = sum(counts.values())
#counts how many people reported each feeling for the selected city
 
if total > 0:
    col1, col2, col3, col4 = st.columns(4)
    for i, feeling in enumerate(feelings):
        pct = int((counts[feeling] / total) * 100)
        with [col1, col2, col3, col4][i]:
            st.metric(label=feeling, value=f"{pct}%", delta=f"{counts[feeling]} reports")
    st.caption(f"Based on {total} reports in {selected_city} today")
else:
    st.info(f"No reports yet for {selected_city} today — be the first!")
#shows the results as 4 percentage cards, one per feeling, or a message if no reports yet
 
if "user_reported" not in st.session_state:
    st.session_state.user_reported = False
#tracks whether the user already submitted a report this session to prevent duplicate submissions
 
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
#shows 4 feeling buttons if the user hasn't reported yet, saves the report to Supabase when clicked
#once submitted, shows a thank you message instead of the buttons
 
st.divider()
 
# ── Section 2: Community Tips ─────────────────────────────────────────────────
st.subheader("💡 Community Tips")
st.caption("Share and discover tips from allergy sufferers across Switzerland!")
 
show_all      = st.toggle("Show tips from all cities", value=False) #toggle to show tips from all cities or just the selected one
all_tips      = fetch_tips() #gets all tips from the database
filtered_tips = all_tips if show_all else [t for t in all_tips if t["city"] == selected_city]
#filters tips by city unless the toggle is on
 
if not filtered_tips:
    st.info(f"No tips yet for {selected_city} — be the first to share!")
 
if "voted_tips" not in st.session_state:
    st.session_state.voted_tips = set()
#tracks which tips the user already voted for this session to prevent duplicate votes
 
for tip in filtered_tips:
    col_tip, col_vote = st.columns([4, 1])
    with col_tip:
        badge_str   = f" · {tip['badge']}"      if tip.get("badge")   else ""
        pollens_str = f" · 🌿 {tip['pollens']}" if tip.get("pollens") else ""
        st.markdown(f"💬 **{tip['city']}** · {tip['date']}{badge_str}{pollens_str}")
        st.markdown(f"{tip['tip']}")
        #shows tip with the author's city, date, risk badge and allergies if available
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
        #shows a vote button if not already voted, otherwise shows the vote count
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
#form to submit a new tip, saves it to Supabase with the user's city, badge and allergies
 
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
#shows the 10 most recent pollen sightings with city, date, risk badge and description
 
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
#form to report a new pollen sighting, saves it to Supabase with the user's city and badge
 
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
#rotates the weekly question based on the current week number so it changes automatically every week
 
for comment in fetch_comments()[-20:]:
    badge_str   = f" · {comment['badge']}"      if comment.get("badge")   else ""
    pollens_str = f" · 🌿 {comment['pollens']}" if comment.get("pollens") else ""
    st.markdown(f"💬 **{comment['city']}** · {comment['date']}{badge_str}{pollens_str}: {comment['comment']}")
#shows the 20 most recent comments with the author's city, date, risk badge and allergies
 
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
#form to post a comment, saves it to Supabase with the user's city, badge and allergies
 
st.divider()
st.caption("🤝 BlessYou Community · Together we breathe easier 🌿") #sources in light grey at bottom of page
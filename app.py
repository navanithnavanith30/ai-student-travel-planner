import streamlit as st
import google.generativeai as genai

# ================= CONFIG =================
genai.configure(api_key="AIzaSyAbA1hampqSitgWznrNu2OPFCDfmzWP-4w")

# 🔹 AUTO-DETECT A WORKING MODEL
available_models = [
    m.name for m in genai.list_models()
    if "generateContent" in m.supported_generation_methods
]

if not available_models:
    st.error("❌ No Gemini models available for this API key.")
    st.stop()

model = genai.GenerativeModel(available_models[0])

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Student Travel Planner ✈️",
    layout="centered"
)

# ================= SESSION =================
if "users" not in st.session_state:
    st.session_state.users = {}

if "page" not in st.session_state:
    st.session_state.page = "login"

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# ================= AUTH =================
def signup(u, p):
    if not u or not p:
        st.error("⚠️ Username and password required")
        return
    if u in st.session_state.users:
        st.error("⚠️ User already exists")
        return

    st.session_state.users[u] = p
    st.session_state.current_user = u
    st.session_state.page = "planner"
    st.success("✅ Account created & logged in!")
    st.rerun()

def login(u, p):
    if u in st.session_state.users and st.session_state.users[u] == p:
        st.session_state.current_user = u
        st.session_state.page = "planner"
        st.rerun()
    else:
        st.error("❌ Invalid credentials")

def logout():
    st.session_state.page = "login"
    st.session_state.current_user = ""
    st.rerun()

# ================= LOGIN PAGE =================
if st.session_state.page == "login":
    st.markdown("## 🎒 AI STUDENT TRAVEL PLANNER")
    st.markdown("##### ✨ Plan smart, travel more, spend less!")

    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        u = st.text_input("👤 Username")
        p = st.text_input("🔑 Password", type="password")
        if st.button("➡️ Login"):
            login(u, p)

    with tab2:
        nu = st.text_input("👤 Create Username")
        np = st.text_input("🔑 Create Password", type="password")
        if st.button("📝 Sign Up"):
            signup(nu, np)

# ================= MAIN APP =================
else:
    st.markdown("## ✈️ AI STUDENT TRAVEL PLANNER")
    st.success(f"👋 Welcome **{st.session_state.current_user}**")
    st.button("🚪 Logout", on_click=logout)
    st.divider()

    # -------- Student Inputs --------
    st.markdown("### 🧑‍🎓 Student Details")

    name = st.text_input("📛 Student Name")

    start_location = st.text_input(
        "📍 Starting Location (City / Town)",
        placeholder="Eg: Bengaluru, Mysuru, Chennai"
    )

    # ---- Trip members ----
    trip_type = st.selectbox(
        "👥 Trip Type",
        [
            "Solo Trip (1 person)",
            "Couple (2 people)",
            "Friends Group (3–5 people)",
            "Family Trip (4–6 people)"
        ]
    )

    # Extract member count (for AI clarity)
    members_map = {
        "Solo Trip (1 person)": "1 person",
        "Couple (2 people)": "2 people",
        "Friends Group (3–5 people)": "3 to 5 people",
        "Family Trip (4–6 people)": "4 to 6 people"
    }
    members = members_map[trip_type]

    col1, col2 = st.columns(2)
    with col1:
        budget = st.number_input("💰 Total Budget (₹)", min_value=1000)
    with col2:
        days = st.number_input("📅 Number of Days", min_value=1)

    interest = st.selectbox(
        "🎯 Travel Interest",
        [
            "Nature 🌿","Adventure 🧗","Beach 🏖️","Hill Station 🏔️","Wildlife 🐅",
            "History 🏛️","Culture 🎭","Spiritual 🛕","Education 🎓",
            "Food 🍲","Photography 📸","Festival 🎉","Backpacking 🎒","Budget 💸"
        ]
    )

    # -------- AI FUNCTIONS --------
    def suggest_places():
        prompt = f"""
Suggest 5 student-friendly Indian travel destinations.

Starting Location: {start_location}
Trip Type: {trip_type}
Number of Members: {members}
Budget: ₹{budget}
Days: {days}
Interest: {interest}

Prefer bus or train travel.
Bullet points only.
"""
        return model.generate_content(prompt).text

    def generate_plan(destination):
        prompt = f"""
Create a student travel plan.

Student Name: {name}
Starting Location: {start_location}
Destination: {destination}
Trip Type: {trip_type}
Number of Members: {members}
Total Budget: ₹{budget}
Days: {days}
Interest: {interest}

Include:
- Transport from starting location
- Cost breakup per person
- Stay options (hostel / budget hotel)
- Daily itinerary
- Safety & budget tips
"""
        return model.generate_content(prompt).text

    # -------- Validation --------
    if not start_location:
        st.warning("⚠️ Please enter your starting location to continue.")

    st.divider()

    if st.button("🌍 Suggest Places"):
        if start_location:
            with st.spinner("🤖 AI is finding best places for you..."):
                st.text_area(
                    "📍 Suggested Destinations",
                    suggest_places(),
                    height=200
                )

    destination = st.text_input("📌 Choose one destination")

    if st.button("🧭 Generate Travel Plan"):
        if start_location and destination:
            with st.spinner("🧠 AI is creating your travel plan..."):
                st.text_area(
                    "🗺️ AI Travel Plan",
                    generate_plan(destination),
                    height=350
                )

    st.markdown("---")
    st.markdown("💡 *Group travel saves money — solo travel builds confidence!* 😊")
import streamlit as st
import google.generativeai as genai

# ================= CONFIG =================
genai.configure(api_key="YOUR_GOOGLE_API_KEY")

# 🔹 AUTO-DETECT A WORKING MODEL (NO 404 EVER)
available_models = [
    m.name for m in genai.list_models()
    if "generateContent" in m.supported_generation_methods
]

if not available_models:
    st.error("❌ No Gemini models available for this API key.")
    st.stop()

model_name = available_models[0]  # pick first valid model
model = genai.GenerativeModel(model_name)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI STUDENT TRAVEL PLANNER",
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
        st.error("Username and password required")
    elif u in st.session_state.users:
        st.error("User already exists")
    else:
        st.session_state.users[u] = p
        st.success("Account created. Please login.")

def login(u, p):
    if u in st.session_state.users and st.session_state.users[u] == p:
        st.session_state.current_user = u
        st.session_state.page = "planner"
        st.rerun()
    else:
        st.error("Invalid credentials")

def logout():
    st.session_state.page = "login"
    st.session_state.current_user = ""
    st.rerun()

# ================= LOGIN PAGE =================
if st.session_state.page == "login":
    st.title("🔐 AI STUDENT TRAVEL PLANNER")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            login(u, p)

    with tab2:
        nu = st.text_input("Create Username")
        np = st.text_input("Create Password", type="password")
        if st.button("Sign Up"):
            signup(nu, np)

# ================= MAIN APP =================
else:
    st.title("🎓 AI STUDENT TRAVEL PLANNER")
    st.write(f"Welcome **{st.session_state.current_user}** 👋")
    st.button("Logout", on_click=logout)
    st.divider()

    name = st.text_input("Student Name")
    budget = st.number_input("Total Budget (₹)", min_value=1000)
    days = st.number_input("Number of Days", min_value=1)

    interest = st.selectbox(
        "Travel Interest",
        [
            "Nature","Adventure","Beach","Hill Station","Wildlife",
            "History","Culture","Spiritual","Education",
            "Food","Photography","Festival","Solo","Backpacking","Budget"
        ]
    )

    # ================= AI FUNCTIONS =================
    def suggest_places():
        prompt = f"""
Suggest 5 student-friendly Indian travel destinations.
Budget: ₹{budget}
Days: {days}
Interest: {interest}
Bullet points only.
"""
        return model.generate_content(prompt).text

    def generate_plan(destination):
        prompt = f"""
Create a student travel plan.

Name: {name}
Destination: {destination}
Budget: ₹{budget}
Days: {days}
Interest: {interest}

Include trip type, budget/day, transport, stay, and tips.
"""
        return model.generate_content(prompt).text

    if st.button("🤖 Suggest Places"):
        with st.spinner("AI suggesting places..."):
            st.text_area("Suggested Destinations", suggest_places(), height=200)

    destination = st.text_input("Choose one destination")

    if st.button("🧠 Generate Travel Plan"):
        with st.spinner("AI generating plan..."):
            st.text_area(
                "AI Travel Plan",
                generate_plan(destination),
                height=350
            )

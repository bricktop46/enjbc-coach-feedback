import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- Config ---
st.set_page_config(page_title="ENJBC Coach Feedback", layout="centered")

PARTICIPANTS_CSV = os.path.join(os.path.dirname(__file__), "participants.csv")
FEEDBACK_DIR = os.path.join(os.path.dirname(__file__), "feedback")
SUBMITTED_FILE = os.path.join(os.path.dirname(__file__), "submitted_teams.json")

os.makedirs(FEEDBACK_DIR, exist_ok=True)

# --- Master Users ---
MASTER_USERS = {
    "president@enjbc.org.au": "@Jc31423142",
    "operations@enjbc.org.au": "VinnieJets",
}

# --- Helper Functions ---
def load_submitted_teams():
    if os.path.exists(SUBMITTED_FILE):
        with open(SUBMITTED_FILE, "r") as f:
            return json.load(f)
    return {}

def save_submitted_team(team_name, coach_name):
    data = load_submitted_teams()
    data[team_name] = {"coach": coach_name, "submitted_at": datetime.now().isoformat()}
    with open(SUBMITTED_FILE, "w") as f:
        json.dump(data, f)

def load_roster():
    df = pd.read_csv(PARTICIPANTS_CSV)
    return df

def get_teams(df):
    players = df[df["Role"] == "Player"]
    teams = sorted(players["Team"].dropna().unique().tolist())
    return teams

def get_players_for_team(df, team):
    players = df[(df["Role"] == "Player") & (df["Team"] == team)]
    return players[["First Name", "Last Name"]].reset_index(drop=True)

# --- Session State Init ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_master" not in st.session_state:
    st.session_state.is_master = False
if "coach_name" not in st.session_state:
    st.session_state.coach_name = ""
if "confirmed_submit" not in st.session_state:
    st.session_state.confirmed_submit = False

# --- Login Page ---
if not st.session_state.authenticated:
    st.title("🏀 ENJBC End of Season Coach Feedback")
    st.markdown("---")
    
    login_type = st.radio("Login as:", ["Coach", "Admin (President/Operations)"])
    
    if login_type == "Coach":
        coach_name = st.text_input("Enter your full name:")
        if st.button("Login"):
            if coach_name.strip():
                st.session_state.authenticated = True
                st.session_state.is_master = False
                st.session_state.coach_name = coach_name.strip()
                st.rerun()
            else:
                st.error("Please enter your name.")
    else:
        email = st.text_input("Email:")
        password = st.text_input("Password:", type="password")
        if st.button("Login"):
            if email in MASTER_USERS and MASTER_USERS[email] == password:
                st.session_state.authenticated = True
                st.session_state.is_master = True
                st.session_state.coach_name = email
                st.rerun()
            else:
                st.error("Invalid credentials.")
    st.stop()

# --- Master Admin View ---
if st.session_state.is_master:
    st.title("🏀 ENJBC Feedback Admin Panel")
    st.markdown(f"Logged in as: **{st.session_state.coach_name}**")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.is_master = False
        st.rerun()
    
    st.markdown("---")
    st.subheader("Submitted Feedback")
    
    feedback_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith(".csv")]
    
    if not feedback_files:
        st.info("No feedback submitted yet.")
    else:
        for f in sorted(feedback_files):
            team_name = f.replace(".csv", "").replace("_", " ")
            st.markdown(f"### {team_name}")
            df = pd.read_csv(os.path.join(FEEDBACK_DIR, f))
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
    st.stop()

# --- Coach Feedback Form ---
st.title("🏀 ENJBC End of Season Coach Feedback")
st.markdown(f"Welcome, **{st.session_state.coach_name}**")

if st.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.markdown("---")

# Load data
df = load_roster()
teams = get_teams(df)
submitted_teams = load_submitted_teams()

# Team selection
selected_team = st.selectbox("Select your team:", ["-- Select --"] + teams)

if selected_team == "-- Select --":
    st.info("Please select your team to begin.")
    st.stop()

# Check if already submitted
if selected_team in submitted_teams:
    st.error(f"Feedback for **{selected_team}** has already been submitted by {submitted_teams[selected_team]['coach']}. Only one submission per team is allowed.")
    st.stop()

# Get players
players = get_players_for_team(df, selected_team)

if players.empty:
    st.warning("No players found for this team.")
    st.stop()

st.subheader(f"Players in {selected_team}")
st.markdown("Rate each player from **1** (lowest) to **5** (highest).")

# Grade level info
st.markdown("---")
st.markdown("""
<small><b>Grade Level Guide:</b><br>
<b>At Grade Level</b> – Player is playing at their correct natural grade level.<br>
<b>Below Grade Level</b> – Player's skill level is below the current standard.<br>
<b>Above Grade Level</b> – Player's skill level is above the current standard.</small>
""", unsafe_allow_html=True)
st.markdown("---")

GRADE_LEVELS = ["At Grade Level", "Below Grade Level", "Above Grade Level"]
SKILLS = ["Teamwork", "Coachability", "Shooting", "Dribbling", "Defence"]

# Collect feedback for all players
feedback_data = []
all_valid = True

for idx, row in players.iterrows():
    player_name = f"{row['First Name']} {row['Last Name']}"
    st.markdown(f"### {player_name}")
    
    cols = st.columns(len(SKILLS))
    ratings = {}
    for i, skill in enumerate(SKILLS):
        with cols[i]:
            ratings[skill] = st.slider(skill, 1, 5, 3, key=f"{idx}_{skill}")
    
    col1, col2 = st.columns(2)
    with col1:
        grade_level = st.selectbox("Grade Level", GRADE_LEVELS, key=f"{idx}_grade")
    with col2:
        comments = st.text_area("Comments", key=f"{idx}_comments", height=80)
    
    feedback_data.append({
        "Player": player_name,
        **ratings,
        "Grade Level": grade_level,
        "Comments": comments,
    })
    st.markdown("---")

# Coach certification
st.subheader("Coach Certification")
st.markdown("By signing below, I certify that this feedback is my honest assessment of each player.")

certify_name = st.text_input("Type your full name to certify:", value=st.session_state.coach_name)

st.markdown("**Digital Signature:**")
signature_text = st.text_input("Type your full name as your digital signature:", key="signature_input")
agree_checkbox = st.checkbox("I confirm this is my digital signature and this feedback is my honest assessment.", key="sig_confirm")

has_signature = bool(signature_text.strip()) and agree_checkbox

# Submit
st.markdown("---")

if not st.session_state.confirmed_submit:
    if st.button("Submit Feedback", type="primary"):
        if not certify_name.strip():
            st.error("Please type your name to certify.")
        elif not has_signature:
            st.error("Please provide your signature.")
        else:
            st.session_state.confirmed_submit = True
            st.rerun()
else:
    st.warning("⚠️ **All submissions are final – are you ready to submit?**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Submit", type="primary"):
            # Save feedback
            feedback_df = pd.DataFrame(feedback_data)
            feedback_df["Coach"] = certify_name.strip()
            feedback_df["Team"] = selected_team
            feedback_df["Submitted At"] = datetime.now().isoformat()
            
            filename = selected_team.replace(" ", "_") + ".csv"
            feedback_df.to_csv(os.path.join(FEEDBACK_DIR, filename), index=False)
            save_submitted_team(selected_team, certify_name.strip())
            
            st.success("✅ Feedback submitted successfully! Thank you.")
            st.session_state.confirmed_submit = False
            st.balloons()
            st.stop()
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.confirmed_submit = False
            st.rerun()

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set up page layout and title
st.set_page_config(page_title="Community Hero", page_icon="🦸‍♂️", layout="wide")

st.title("🦸‍♂️ Community Hero - Hyperlocal Problem Solver")
st.markdown("Empowering citizens to identify, validate, and track community challenges through collaboration.")

# --- MOCK DATA (Starting state) ---
if "issues" not in st.session_state:
    st.session_state.issues = pd.DataFrame([
        {
            "id": 1,
            "title": "Deep Pothole on Main St",
            "description": "A very deep pothole near the crossing, dangerous for cyclists.",
            "category": "Road & Infrastructure",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "status": "Verified",
            "votes": 12,
            "reporter": "Alice Smith"
        },
        {
            "id": 2,
            "title": "Broken Streetlight",
            "description": "Streetlight has been flickering and is now completely out.",
            "category": "Streetlights & Electricity",
            "latitude": 37.7849,
            "longitude": -122.4094,
            "status": "In Progress",
            "votes": 8,
            "reporter": "Bob Jones"
        },
        {
            "id": 3,
            "title": "Water Pipe Leakage",
            "description": "Clean water wasting from a cracked pipe on the sidewalk.",
            "category": "Water & Sanitation",
            "latitude": 37.7649,
            "longitude": -122.4294,
            "status": "Pending",
            "votes": 3,
            "reporter": "Charlie Brown"
        }
    ])

if "user_points" not in st.session_state:
    st.session_state.user_points = {
        "Alice Smith": 120,
        "Bob Jones": 85,
        "Charlie Brown": 45,
        "You (Hero)": 0
    }

# --- SEPARATED VALIDATION UTILITIES ---

def is_valid_coordinate(lat, lon):
    """Checks if coordinates are within standard Earth boundaries."""
    if not (-90.0 <= lat <= 90.0):
        return False, "Latitude must be between -90 and 90."
    if not (-180.0 <= lon <= 180.0):
        return False, "Longitude must be between -180 and 180."
    
    # Check if the coordinates are roughly in our region (California/West Coast area)
    if not (30 <= lat <= 45) or not (-125 <= lon <= -110):
        return True, "Warning: Location is outside our community area, but coordinates are valid."
        
    return True, ""

def validate_title(text):
    """Ensures title is present and doesn't contain obvious spam."""
    text = text.strip()
    if len(text) < 3:
        return False, "Title is too short. Please use at least 3 characters."
    
    words = text.split()
    for word in words:
        if len(word) > 15:
            return False, f"Title contains an unusually long word: '{word[:10]}...'."
            
    return True, ""

def validate_description(text):
    """Ensures description is reasonably informative and not nonsense."""
    text = text.strip()
    words = text.split()
    
    if len(words) < 3:
        return False, "Please describe the issue using at least 3 words."
        
    for word in words:
        # Check for ridiculously long words (e.g. 'asdfghjklqwerty')
        if len(word) > 15:
            return False, f"Description contains an unusually long word: '{word[:10]}...'."
            
        # Check for vowels in longer words to prevent simple consonant-spam gibberish
        if len(word) > 3:
            vowels = sum(1 for char in word.lower() if char in "aeiouy")
            if vowels == 0:
                return False, f"The word '{word}' looks like nonsense (no vowels)."
                
    return True, ""

# --- SIMULATED AI CATEGORIZATION ---
def ai_classify_issue(description):
    desc = description.lower()
    
    # 1. Check for Animal & Safety issues FIRST (stops "street dogs" from triggering "street" infrastructure)
    if any(word in desc for word in ["dog", "cat", "animal", "rabies", "stray", "bite", "danger", "safety", "health"]):
        return "Public Health & Safety"
        
    # 2. Check for Road & Infrastructure
    elif any(word in desc for word in ["pothole", "road", "street", "sidewalk", "crack", "pavement"]):
        return "Road & Infrastructure"
        
    # 3. Check for Water & Sanitation
    elif any(word in desc for word in ["water", "leak", "pipe", "drain", "sewer", "flooding"]):
        return "Water & Sanitation"
        
    # 4. Check for Streetlights & Electricity
    elif any(word in desc for word in ["light", "lamp", "dark", "electricity", "power"]):
        return "Streetlights & Electricity"
        
    # 5. Check for Waste Management
    elif any(word in desc for word in ["garbage", "trash", "waste", "dump", "litter"]):
        return "Waste Management"
        
    else:
        return "General / Other"

# --- SIDEBAR: REPORT A NEW ISSUE ---
st.sidebar.header("📝 Report a New Issue")
with st.sidebar.form(key="report_form"):
    title = st.text_input("Issue Title", placeholder="e.g., Stray animal hazard")
    description = st.text_area("Describe the Issue", placeholder="e.g., Street dogs carrying rabies near the school playground.")
    
    st.markdown("**Location Coordinates**")
    lat = st.number_input("Latitude", value=37.7749, format="%.4f")
    lon = st.number_input("Longitude", value=-122.4194, format="%.4f")
    
    submit_button = st.form_submit_button(label="Submit Report")

if submit_button:
    # 1. Clean inputs
    title_clean = title.strip()
    description_clean = description.strip()
    
    # 2. Run validations
    title_valid, title_msg = validate_title(title_clean)
    desc_valid, desc_msg = validate_description(description_clean)
    coords_valid, coord_msg = is_valid_coordinate(lat, lon)
    
    if not title_valid:
        st.sidebar.error(f"❌ Invalid Title: {title_msg}")
    elif not desc_valid:
        st.sidebar.error(f"❌ Invalid Description: {desc_msg}")
    elif not coords_valid:
        st.sidebar.error(f"❌ Invalid Location: {coord_msg}")
    else:
        # Everything is valid! Proceed with submission
        detected_category = ai_classify_issue(description_clean)
        new_id = len(st.session_state.issues) + 1
        new_row = {
            "id": new_id,
            "title": title_clean,
            "description": description_clean,
            "category": detected_category,
            "latitude": lat,
            "longitude": lon,
            "status": "Pending",
            "votes": 1,
            "reporter": "You (Hero)"
        }
        
        st.session_state.issues = pd.concat([st.session_state.issues, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.user_points["You (Hero)"] += 50
        
        st.sidebar.success(f"🎉 Issue Reported! AI classified this as: **{detected_category}** (+50 Hero Points!)")
        if coord_msg:  # If there was a coordinate warning, show it
            st.sidebar.warning(coord_msg)

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Hyperlocal Map & Issues")
    
    # Display Map
    map_data = st.session_state.issues[["latitude", "longitude"]]
    st.map(map_data)
    
    st.subheader("📋 Active Issues List")
    
    for idx, row in st.session_state.issues.iterrows():
        with st.container():
            st.markdown(f"### {row['title']} ({row['category']})")
            st.write(f"**Reported by:** {row['reporter']} | **Status:** `{row['status']}`")
            st.write(row['description'])
            
            col_vote_1, col_vote_2 = st.columns([1, 4])
            with col_vote_1:
                if st.button(f"👍 Upvote ({row['votes']})", key=f"vote_{row['id']}"):
                    st.session_state.issues.at[idx, 'votes'] += 1
                    st.session_state.user_points["You (Hero)"] += 10
                    st.rerun()
            with col_vote_2:
                if row['votes'] >= 10:
                    st.info("🔥 Highly Verified by the Community")
            st.markdown("---")

with col2:
    st.subheader("📊 Community Insights & Gamification")
    
    total_issues = len(st.session_state.issues)
    st.metric(label="Total Issues Reported", value=total_issues)
    
    st.markdown("#### Status Breakdown")
    status_counts = st.session_state.issues["status"].value_counts()
    
    fig, ax = plt.subplots(figsize=(4, 3))
    colors = ['#ff9999','#66b3ff','#99ff99']
    status_counts.plot(kind='bar', color=colors[:len(status_counts)], ax=ax)
    ax.set_ylabel('Number of Issues')
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.markdown("### 🏆 Community Leaderboard")
    st.write("Earn Hero Points by submitting valid reports and verifying others' entries.")
    
    leaderboard_df = pd.DataFrame(
        list(st.session_state.user_points.items()), 
        columns=["Citizen", "Hero Points"]
    ).sort_values(by="Hero Points", ascending=False)
    
    st.table(leaderboard_df.reset_index(drop=True))
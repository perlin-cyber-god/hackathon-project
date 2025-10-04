import streamlit as st
import os
import tempfile
import shutil
from judge import HackathonJudge
from llm_analyzer import API_KEY # Your API key is managed here

# --- Page Configuration and CSS ---
st.set_page_config(
    page_title="AI Judge Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Your awesome "Cosmic" theme CSS - now with more colors, animations, and smooth edges!
css_styles = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

.stApp {
    background-color: #000011;
    background-image: radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px), radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px), radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px), radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 2px, transparent 30px);
    background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px;
    background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
    color: white;
}

/* Main content font */
body, .stMarkdown, .stTextInput, .stTextArea {
    font-family: 'Orbitron', sans-serif;
}

h1, h2, h3 {
    color: #00ffff; /* Neon blue/cyan color */
}

/* Main button with pulsing animation */
@keyframes pulse {
    0% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); }
    50% { box-shadow: 0 0 35px rgba(0, 255, 255, 0.8); }
    100% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); }
}

div[data-testid="stButton"] > button {
    border: 2px solid #00ffff;
    background-image: linear-gradient(45deg, #00d4ff, #7b2ff7);
    color: white;
    transition: all 0.3s ease-in-out;
    width: 100%;
    border-radius: 12px; /* Smoother edges */
    animation: pulse 2s infinite;
}
div[data-testid="stButton"] > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 40px rgba(0, 255, 255, 1);
}

/* Custom segmented control buttons */
div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button {
    background-image: none;
    background-color: transparent;
    animation: none; /* Disable pulse for smaller buttons */
}

/* Style for inputs */
.stTextArea textarea, .stTextInput input, .stFileUploader {
    background-color: rgba(10, 20, 40, 0.8);
    border: 1px solid #00aaff;
    border-radius: 12px; /* Smoother edges */
    color: white;
    transition: all 0.3s ease-in-out;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.6);
    border-color: #00ffff;
}

/* Style for the report code block */
pre {
    background-color: rgba(10, 20, 40, 0.8);
    border: 1px solid #00aaff;
    border-radius: 12px;
    padding: 20px;
    white-space: pre-wrap;
    word-wrap: break-word;
}
"""
st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)

# Initialize the Judge and submissions in session state
if 'judge' not in st.session_state:
    st.session_state.judge = HackathonJudge(api_key=API_KEY)
if 'submissions' not in st.session_state:
    st.session_state.submissions = []
# Initialize button states
if 'description_source' not in st.session_state:
    st.session_state.description_source = 'Manual Entry'
if 'code_source' not in st.session_state:
    st.session_state.code_source = 'GitHub URL'

# --- Main Page Layout ---
st.title("🌌 AI Judge: Project Nebula")
st.markdown("##### Welcome, Mission Commander! Awaiting project telemetry for orbital evaluation.")
st.markdown("---")

# Center the form on the page
_, form_col, _ = st.columns([1, 2, 1])

with form_col:
    with st.container():
        project_name = st.text_input("Project Name", "Project Alpha")
        
        # --- Interactive Description Source Buttons ---
        st.write("Description Source")
        desc_cols = st.columns(2)
        if desc_cols[0].button('Manual Entry', use_container_width=True):
            st.session_state.description_source = 'Manual Entry'
        if desc_cols[1].button('Upload .txt', use_container_width=True):
            st.session_state.description_source = 'Upload .txt'
        
        description = ""
        if st.session_state.description_source == "Manual Entry":
            description = st.text_area("Project Description (README/Pitch)", "This project is a revolutionary AI synergy for blockchain.", height=150)
        else:
            uploaded_desc_file = st.file_uploader("Upload Description (.txt)", type=['txt'], label_visibility="collapsed")
            if uploaded_desc_file:
                description = uploaded_desc_file.read().decode('utf-8')

        video_file = st.file_uploader("Upload Presentation Video (.mp4)", type=['mp4'])

        # --- Interactive Code Source Buttons ---
        st.write("Code Source")
        code_cols = st.columns(3)
        if code_cols[0].button('GitHub URL', use_container_width=True):
            st.session_state.code_source = 'GitHub URL'
        if code_cols[1].button('Manual Entry ', use_container_width=True): # Space to make key unique
            st.session_state.code_source = 'Manual Entry'
        if code_cols[2].button('Upload Files', use_container_width=True):
            st.session_state.code_source = 'Upload Files'
            
        code_path = None
        uploaded_code_files = None
        if st.session_state.code_source == "GitHub URL":
            code_path = st.text_input("GitHub Repository URL", "https://github.com/user/repo", label_visibility="collapsed")
        elif st.session_state.code_source == "Manual Entry":
            code_path = st.text_area("Paste Code Here", "print('hello world')", height=200, label_visibility="collapsed")
        else: # Upload Files
            uploaded_code_files = st.file_uploader("Upload Code (.py or .zip)", type=['py', 'zip'], accept_multiple_files=True, label_visibility="collapsed")

        st.write("") # Spacer
        launch_button = st.button("🚀 Launch Evaluation")

if launch_button:
    # --- Input Validation and Judging Logic (same as before) ---
    is_valid = True
    if not project_name:
        st.error("Mission Aborted: Project Name is required.")
        is_valid = False
    if not description:
        st.error("Mission Aborted: Project Description is required.")
        is_valid = False
    if not video_file:
        st.error("Mission Aborted: Video Presentation is required.")
        is_valid = False
    if st.session_state.code_source in ['GitHub URL', 'Manual Entry'] and not code_path:
        st.error("Mission Aborted: Code submission is required.")
        is_valid = False
    if st.session_state.code_source == 'Upload Files' and not uploaded_code_files:
        st.error("Mission Aborted: Code submission is required.")
        is_valid = False
        
    if is_valid:
        with st.spinner("Analyzing mission parameters... This may take a few moments..."):
            temp_dir = tempfile.mkdtemp()
            try:
                # 1. Process Video
                video_bytes = video_file.getvalue()
                temp_video_path = os.path.join(temp_dir, video_file.name)
                with open(temp_video_path, 'wb') as f: f.write(video_bytes)
                presentation_text = st.session_state.judge.transcribe_video(temp_video_path)

                # 2. Process Code
                code_processing_dir = os.path.join(temp_dir, "code_src")
                os.makedirs(code_processing_dir, exist_ok=True)
                code_directory_for_judge = None
                if st.session_state.code_source == "GitHub URL":
                    code_directory_for_judge = st.session_state.judge.process_code_from_github(code_path, code_processing_dir)
                elif st.session_state.code_source == "Manual Entry":
                    code_directory_for_judge = st.session_state.judge.process_code_from_manual(code_path, code_processing_dir)
                else: # Uploaded files
                    saved_files = []
                    for u_file in uploaded_code_files:
                        path = os.path.join(temp_dir, u_file.name)
                        with open(path, 'wb') as f: f.write(u_file.getvalue())
                        saved_files.append(path)
                    code_directory_for_judge = st.session_state.judge.process_code_from_files(saved_files, code_processing_dir)

                # 3. Run Evaluation
                if code_directory_for_judge:
                    with st.spinner("AI Judge is computing orbital trajectories... Firing retro-thrusters..."):
                        result = st.session_state.judge.evaluate_submission(
                            project_name=project_name,
                            description=description,
                            code_directory=code_directory_for_judge,
                            presentation_text=presentation_text
                        )
                        st.session_state.submissions.append(result)
                        st.success(f"Evaluation for '{project_name}' complete!")
                        st.balloons()
                else:
                    st.error("Code processing failed. Please check the source and try again.")

            except Exception as e:
                st.error(f"A critical mission anomaly occurred: {e}")
            finally:
                shutil.rmtree(temp_dir)

# --- Display Results ---
if st.session_state.submissions:
    st.markdown("---")
    st.header("👑 Mission Leaderboard")
    
    sorted_submissions = sorted(st.session_state.submissions, key=lambda x: x['final_score'], reverse=True)
    
    # Header row for the leaderboard
    l_cols = st.columns([1, 4, 2, 2])
    l_cols[0].write("**Rank**")
    l_cols[1].write("**Project Name**")
    l_cols[2].write("**Final Score**")
    l_cols[3].write("**Rating**")

    # Display each submission in the leaderboard
    for i, sub in enumerate(sorted_submissions):
        l_cols = st.columns([1, 4, 2, 2])
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"**{i+1}**"
        l_cols[0].markdown(f"### {medal}")
        l_cols[1].write(sub['project_name'])
        l_cols[2].write(f"**{sub['final_score']:.2f}** / 100")
        l_cols[3].write(sub['rating'])

    st.markdown("---")
    st.header("🏆 Individual Project Debriefs")
    for sub in st.session_state.submissions:
        with st.expander(f"Show Full Report for: {sub['project_name']}"):
            report = st.session_state.judge.generate_judge_report(sub)
            st.code(report, language='markdown')
else:
    st.info("Awaiting new submissions for evaluation...")


import streamlit as st
import os
import zipfile
import shutil
from judge import main as judge_project
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Judge Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for the Space Theme ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Create a style.css file or keep it as a string
css_styles = """
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

/* Main background */
.stApp {
    background-color: #000011;
    background-image:
        radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
        radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
        radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px),
        radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 2px, transparent 30px);
    background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px;
    background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
    color: white;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background: rgba(10, 10, 25, 0.8);
    border-right: 1px solid #00ffff;
    backdrop-filter: blur(5px);
}

/* Font styles */
h1, h2, h3, .stButton>button, .stMetricLabel {
    font-family: 'Orbitron', sans-serif;
    color: #00ffff; /* Neon blue/cyan color */
}

/* Button style */
.stButton>button {
    border: 2px solid #00ffff;
    background-color: transparent;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #00ffff;
    color: black !important;
    border: 2px solid #00ffff;
}

/* Metric card styling */
.stMetric {
    background-color: rgba(10, 20, 40, 0.7);
    border: 1px solid #00aaff;
    border-radius: 10px;
    padding: 15px;
    backdrop-filter: blur(3px);
    color: white !important; /* This fixes the score visibility */
}
.stMetric > div > div > span {
    color: white !important; /* This fixes the score value visibility */
}

/* File uploader styling */
.stFileUploader {
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    padding: 10px;
}
"""

st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.header("🛰️ Mission Control")
    st.write("Prepare your project for deep space analysis. Upload the mission data package as a `.zip` file.")
    
    uploaded_file = st.file_uploader(
        "Upload Mission Data",
        type=["zip"],
        label_visibility="collapsed"
    )
    
    # Placeholder for the button to control its state
    if "judge_clicked" not in st.session_state:
        st.session_state.judge_clicked = False
    
    def on_judge_click():
        st.session_state.judge_clicked = True
        
    st.button("🚀 Launch Analysis", on_click=on_judge_click)

# --- Main Page ---
st.title("🌌 AI Judge: Project Nebula by TriByte")
st.markdown("##### Welcome, Mission Commander! Your project is ready for its orbital evaluation.")
st.markdown("---")

# --- Logic to run the judge ---
if st.session_state.judge_clicked:
    if uploaded_file is not None:
        temp_dir = "temp_submission"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        try:
            # Save and extract zip
            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            submission_folder = os.path.join(temp_dir, os.listdir(temp_dir)[0])

            # Run analysis with animated spinner text
            spinner_texts = [
                "🛰️ Calibrating sensor arrays...",
                "📡 Establishing uplink to Gemini...",
                "✨ Analyzing project telemetry...",
                "🪐 Calculating orbital trajectories of code...",
            ]
            with st.spinner(spinner_texts[0]):
                for i in range(len(spinner_texts)):
                    st.spinner(spinner_texts[i])
                    time.sleep(1.5) # Simulate different stages of analysis
                
                final_score, final_report = judge_project(submission_folder)

            st.success("Analysis Complete! Telemetry received.")
            st.balloons()

            # Display Results
            st.header("🏆 Mission Debrief: Final Report")
            
            st.metric(label="FINAL MISSION SCORE", value=f"{final_score:.2f} / 100")
            st.progress(int(final_score))
            
            st.markdown("---")
            st.subheader("Detailed System Analysis")

            col1, col2 = st.columns(2)
            criteria_items = list(final_report.items())

            for i, (criterion, details) in enumerate(criteria_items):
                target_col = col1 if i < (len(criteria_items) + 1) // 2 else col2
                with target_col:
                    st.markdown(f"<h5>{criterion} (Weight: {details['weight']})</h5>", unsafe_allow_html=True)
                    st.metric(label="Performance Rating", value=details['score'])
                    st.info(f"**Log Entry:** {details['evidence']}")

        except Exception as e:
            st.error(f"**Mission Anomaly Detected:** {e}")
            st.error("Ensure the data package (.zip) contains a single folder with 'code' subfolder, description file, and video.")
        
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            st.session_state.judge_clicked = False # Reset button state
            
    else:
        st.warning("⚠️ Warning: No mission data package uploaded. Please select a file to proceed.")
        st.session_state.judge_clicked = False # Reset button state
else:
    st.info("Awaiting your command to launch the analysis...")
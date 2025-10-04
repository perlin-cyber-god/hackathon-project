# judge.py
import os
import json
import argparse
import sys

# Import all the functions from your analyzer modules
from text_analyzer import analyze_text_quality
from code_analyzer import analyze_code_quality, check_text_originality
from video_analyzer import transcribe_video
from llm_analyzer import analyze_with_gemini

def find_file(directory, extensions):
    """Finds the first file in a directory with any of the given extensions."""
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                return os.path.join(root, file)
    return None

def main(project_dir):
    """Main function to run the AI Hackathon Judge. Now returns the report."""
    
    criteria = {
        "Originality": {"weight": 0.30},
        "Technical Feasibility": {"weight": 0.25},
        "Impact": {"weight": 0.20},
        "Presentation Quality": {"weight": 0.15},
        "Code Quality": {"weight": 0.10}
    }

    print(f"\n---  JUDGING PROJECT: {project_dir} ---")
    
    scores = {}
    report = {}

    print("\n[1/4] Analyzing Code Quality...")
    code_dir = os.path.join(project_dir, 'code')
    if os.path.exists(code_dir):
        score, evidence = analyze_code_quality(code_dir)
        scores['Code Quality'] = score
        report['Code Quality'] = evidence
    else:
        scores['Code Quality'] = 0
        report['Code Quality'] = "No 'code' directory found."

    print("[2/4] Analyzing Project Description...")
    description_file = find_file(project_dir, ['.txt', '.md'])
    if description_file:
        with open(description_file, 'r', encoding='utf-8') as f:
            description_text = f.read()
        
        score, evidence = check_text_originality(description_text)
        scores['Originality'] = score
        report['Originality'] = evidence
        
        pres_score, pres_evidence = analyze_text_quality(description_text)
    else:
        description_text = ""
        scores['Originality'] = 0
        report['Originality'] = "No description file (.txt, .md) found."
        pres_score, pres_evidence = 0, "No description text to analyze."

    print("[3/4] Analyzing Video Presentation...")
    video_file = find_file(project_dir, ['.mp4', '.mov', '.mkv'])
    if video_file:
        transcript, trans_evidence = transcribe_video(video_file)
        if transcript:
            vid_pres_score, vid_pres_evidence = analyze_text_quality(transcript)
            report['Video Transcript'] = trans_evidence
        else:
            vid_pres_score, vid_pres_evidence = 0, trans_evidence
    else:
        transcript = ""
        vid_pres_score, vid_pres_evidence = 0, "No video file found."
        
    avg_presentation_score = (pres_score + vid_pres_score) / 2 if (pres_score > 0 or vid_pres_score > 0) else 0
    scores['Presentation Quality'] = avg_presentation_score
    report['Presentation Quality'] = f"Text: [{pres_evidence}] Video: [{vid_pres_evidence}]"

    print("[4/4] Performing Advanced LLM Analysis...")
    analysis_text = description_text + "\n" + transcript
    if analysis_text.strip():
        impact_res, feas_res = analyze_with_gemini(analysis_text)
        scores['Impact'] = impact_res.get('score', 0)
        report['Impact'] = impact_res.get('reasoning', 'N/A')
        scores['Technical Feasibility'] = feas_res.get('score', 0)
        report['Technical Feasibility'] = feas_res.get('reasoning', 'N/A')
    else:
        scores['Impact'], report['Impact'] = 0, "No text available for analysis."
        scores['Technical Feasibility'], report['Technical Feasibility'] = 0, "No text available for analysis."

    # --- This section is modified to return the results ---
    final_score = 0
    final_report = {}
    for criterion, details in criteria.items():
        weight = details['weight']
        score = scores.get(criterion, 0)
        final_score += score * weight
        final_report[criterion] = {
            "score": f"{score:.2f}/100",
            "evidence": report.get(criterion, 'N/A'),
            "weight": f"{weight*100}%"
        }
    
    return final_score, final_report

# --- THIS BLOCK IS NOW REMOVED TO PREVENT THE ERROR ---
# The app.py file now handles running this script, so the
# command-line parser is no longer needed here.
# llm_analyzer.py
import os
import json
import google.generativeai as genai
from typing import Tuple

# --- IMPORTANT ---
# Make sure your API key is pasted here.
API_KEY = "AIzaSyAOr3JM9iPKTYED1P2RZCDfe5w7n-QZ6-Y"

try:
    genai.configure(api_key=API_KEY)
    # This line has been updated to the stable model name
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    print("✅ Gemini API configured successfully.")
except Exception as e:
    model = None
    print(f"❌ Failed to configure Gemini API: {e}")

def analyze_with_gemini(project_description: str) -> Tuple[dict, dict]:
    """
    Uses the Gemini API to score Impact and Technical Feasibility.
    """
    if not model:
        default_score = {'score': 0, 'reasoning': 'API key is not configured or is invalid.'}
        return default_score, default_score

    prompt = f"""
    You are an expert hackathon judge. Analyze the following project description.
    Provide your output ONLY in a valid JSON format with two main keys: "impact" and "feasibility".
    For each key, provide a "score" (an integer from 0 to 100) and a brief "reasoning" (a string of no more than 20 words).
    
    Project Description: "{project_description}"
    
    JSON Output:
    """
    
    try:
        response = model.generate_content(prompt)
        json_response_str = response.text.strip().replace("```json", "").replace("```", "")
        analysis = json.loads(json_response_str)
        
        impact_results = analysis.get('impact', {'score': 0, 'reasoning': 'Failed to parse impact.'})
        feasibility_results = analysis.get('feasibility', {'score': 0, 'reasoning': 'Failed to parse feasibility.'})
        
        return impact_results, feasibility_results
        
    except Exception as e:
        print(f"Error during API call or JSON parsing: {e}")
        error_score = {'score': 0, 'reasoning': f"An error occurred: {e}"}
        return error_score, error_score

# This block allows you to test the file directly
if __name__ == '__main__':
    print("\n--- Running a quick test on the API analyzer ---")
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ ERROR: Please replace 'YOUR_API_KEY_HERE' with your actual Gemini API key.")
    else:
        sample_desc = "Our project is 'HealthChain', a decentralized platform using blockchain to secure patient medical records, making them instantly accessible to doctors worldwide while giving patients full control over their data."
        
        impact, feasibility = analyze_with_gemini(sample_desc)
        
        print(f"\nImpact Score: {impact.get('score', 'N/A')}/100")
        print(f"Reasoning: {impact.get('reasoning', 'N/A')}")
        
        print(f"\nTechnical Feasibility Score: {feasibility.get('score', 'N/A')}/100")
        print(f"Reasoning: {feasibility.get('reasoning', 'N/A')}")
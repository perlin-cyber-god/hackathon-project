# code_analyzer.py
import os
import subprocess
import json
from radon.complexity import cc_visit

def analyze_code_quality(code_directory):
    """Analyzes a directory of Python code for linting errors and complexity."""
    py_files = [os.path.join(root, f) for root, _, files in os.walk(code_directory) for f in files if f.endswith('.py')]
    if not py_files:
        return 0, "No Python files found to analyze."

    # 1. Linting with Pylint (IMPROVED SECTION)
    linting_score = 0.0
    pylint_evidence = "Pylint analysis failed or could not produce a score."
    try:
        pylint_process = subprocess.run(
            ['pylint', '--exit-zero'] + py_files,
            capture_output=True, text=True
        )
        
        rating_line = [line for line in pylint_process.stdout.split('\n') if "/10" in line]
        if rating_line:
            score_str = rating_line[0].split(' at ')[1].split('/')[0]
            linting_score = float(score_str) * 10
            pylint_evidence = f"Pylint rated the code at {linting_score:.1f}/100."
        else:
            linting_score = 0.0
            pylint_evidence = "Pylint found too many errors to provide a rating."
    
    # --- THIS IS THE FIX ---
    # The original code had a syntax error in the f-string here
    except Exception as e:
        linting_score = 0.0
        pylint_evidence = f"Pylint analysis failed with an error: {e}"
        
    # 2. Cyclomatic Complexity with Radon (same as before)
    total_complexity = 0
    total_blocks = 0
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                blocks = cc_visit(code)
                for block in blocks:
                    total_complexity += block.complexity
                    total_blocks += 1
        except Exception as e:
            print(f"Radon failed on file {file_path}: {e}") # Handle potential file read errors
    
    avg_complexity = (total_complexity / total_blocks) if total_blocks > 0 else 0
    complexity_score = max(0, 100 - (max(0, avg_complexity - 5) * 10))

    # 3. Final score and evidence construction
    final_score = (linting_score + complexity_score) / 2
    evidence = (
        f"{pylint_evidence} "
        f"Average Cyclomatic Complexity is {avg_complexity:.2f} ({complexity_score:.1f}/100)."
    )
    return final_score, evidence

def check_text_originality(project_description_text):
    """A simple placeholder to check for common boilerplate phrases."""
    boilerplate_phrases = ["built with react", "powered by ai", "a decentralized application", "on the blockchain"]
    found_phrases = [p for p in boilerplate_phrases if p in project_description_text.lower()]
    
    originality_score = max(0, 100 - (len(found_phrases) * 25))
    evidence = f"Found {len(found_phrases)} generic boilerplate phrases."
    return originality_score, evidence
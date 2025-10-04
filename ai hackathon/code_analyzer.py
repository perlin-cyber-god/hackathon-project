# code_analyzer.py
import os
import subprocess
import json
import ast
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from typing import Tuple, List, Dict

try:
    from bandit.core import manager as bandit_manager
    from bandit.core import config as bandit_config
    BANDIT_AVAILABLE = True
except ImportError:
    print("⚠️ WARNING: 'bandit' not found. Security analysis will be skipped. Install with: pip install bandit")
    BANDIT_AVAILABLE = False

class CodeAnalyzer:
    def __init__(self):
        print("🔧 Initializing Code Analyzer...")
        print("✅ Code Analyzer ready!\n")

    def _get_rating(self, score: float) -> str:
        if score >= 90: return "⭐⭐⭐⭐⭐ Excellent"
        if score >= 80: return "⭐⭐⭐⭐ Very Good"
        if score >= 70: return "⭐⭐⭐ Good"
        if score >= 60: return "⭐⭐ Fair"
        if score >= 50: return "⭐ Poor"
        return "❌ Needs Major Improvement"

    def _analyze_linting(self, py_files: List[str]) -> Tuple[float, str]:
        try:
            pylint_process = subprocess.run(
                ['pylint', '--exit-zero'] + py_files, capture_output=True, text=True
            )
            rating_line = [line for line in pylint_process.stdout.split('\n') if "/10" in line]
            if rating_line:
                score_str = rating_line[0].split(' at ')[1].split('/')[0]
                score = float(score_str) * 10
                return score, f"Pylint rated the code at {score:.1f}/100."
            else:
                return 5.0, "Pylint found an excessive number of errors."
        except Exception as e:
            return 5.0, f"Pylint analysis failed critically: {e}"

    def _analyze_complexity_and_maintainability(self, all_code: str) -> Tuple[float, float, str]:
        try:
            cc_blocks = cc_visit(all_code)
            avg_complexity = sum(b.complexity for b in cc_blocks) / len(cc_blocks) if cc_blocks else 0
            complexity_score = max(0, 100 - (max(0, avg_complexity - 5) * 10))
            
            mi_score = mi_visit(all_code, multi=True)
            maintainability_score = (mi_score / 100) * 100
            
            evidence = f"Avg Complexity: {avg_complexity:.2f}, Maintainability Index: {mi_score:.2f}"
            return complexity_score, maintainability_score, evidence
        except Exception as e:
            return 50.0, 50.0, f"Radon analysis failed: {e}"

    def _analyze_documentation(self, all_code: str) -> Tuple[float, str]:
        score = 100.0
        if not all_code.strip().startswith('"""') and not all_code.strip().startswith("'''"):
            score -= 30
        functions = re.findall(r'def \w+', all_code)
        docstrings = re.findall(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', all_code)
        if len(functions) > 0 and len(docstrings) < len(functions):
            score -= (1 - (len(docstrings) / len(functions))) * 40
        lines = all_code.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        comment_lines = [l for l in lines if l.strip().startswith('#')]
        if len(code_lines) > 0 and (len(comment_lines) / len(code_lines)) < 0.05:
            score -= 30
        score = max(0, score)
        return score, f"{len(docstrings)} docstrings, {len(comment_lines)} comments found."

    def _analyze_security(self, py_files: List[str]) -> Tuple[float, str]:
        if not BANDIT_AVAILABLE:
            return 50.0, "Bandit not installed, security scan skipped."
        try:
            b_conf = bandit_config.BanditConfig()
            b_mgr = bandit_manager.BanditManager(b_conf, "custom")
            b_mgr.discover_files(py_files)
            b_mgr.run_tests()
            high_severity = len([r for r in b_mgr.results if r.severity == 'HIGH'])
            medium_severity = len([r for r in b_mgr.results if r.severity == 'MEDIUM'])
            score = 100.0 - (high_severity * 25) - (medium_severity * 10)
            score = max(0, score)
            return score, f"Bandit found {high_severity} HIGH and {medium_severity} MEDIUM severity issues."
        except Exception as e:
            return 50.0, f"Bandit security scan failed: {e}"

    def analyze_directory(self, code_directory: str) -> Tuple[float, str]:
        py_files = [os.path.join(root, f) for root, _, files in os.walk(code_directory) for f in files if f.endswith('.py')]
        if not py_files:
            return 0.0, "No Python files found to analyze."

        # --- THIS IS THE NEW, STRICTER LOGIC ---
        # First, run the linting analysis.
        linting_score, linting_evidence = self._analyze_linting(py_files)
        
        # If linting fails critically, the code is too flawed. Return a low score immediately.
        if linting_score <= 5.0:
            return 5.0, f"Critical Failure: {linting_evidence} The code has severe quality or syntax issues and cannot be properly rated."
        # ----------------------------------------

        all_code = ""
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_code += f.read() + "\n"
            except Exception:
                continue

        # Continue with other analyses only if linting passed
        complexity_score, maintainability_score, radon_evidence = self._analyze_complexity_and_maintainability(all_code)
        documentation_score, doc_evidence = self._analyze_documentation(all_code)
        security_score, sec_evidence = self._analyze_security(py_files)
        
        weights = {
            'linting': 0.30, 'complexity': 0.20, 'maintainability': 0.20,
            'documentation': 0.15, 'security': 0.15
        }
        
        final_score = (
            linting_score * weights['linting'] +
            complexity_score * weights['complexity'] +
            maintainability_score * weights['maintainability'] +
            documentation_score * weights['documentation'] +
            security_score * weights['security']
        )
        
        full_evidence = (
            f"Linting: [{linting_evidence}] "
            f"Complexity & Maintainability: [{radon_evidence}] "
            f"Documentation: [{doc_evidence}] "
            f"Security: [{sec_evidence}]"
        )
        
        return final_score, full_evidence

if __name__ == "__main__":
    code_analyzer = CodeAnalyzer()
    path_to_your_code_folder = "temp_code_for_testing"
    
    if os.path.exists(path_to_your_code_folder) and os.path.isdir(path_to_your_code_folder):
        final_score, evidence = code_analyzer.analyze_directory(path_to_your_code_folder)
        print(f"\n{'='*70}\n📊 FINAL ANALYSIS SUMMARY FOR: '{path_to_your_code_folder}'\n{'='*70}\n")
        print(f"🏆 Final Weighted Score: {final_score:.2f} / 100")
        print(f"📈 Rating: {code_analyzer._get_rating(final_score)}")
        print(f"\n📋 Evidence Summary:\n{evidence}")
    else:
        print(f"❌ ERROR: The directory '{path_to_your_code_folder}' was not found.")
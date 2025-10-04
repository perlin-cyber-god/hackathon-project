# judge.py
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import shutil
import tempfile
import zipfile
import subprocess

# Import all analyzers
from code_analyzer import CodeAnalyzer
from llm_analyzer import analyze_with_gemini, extract_claims_with_gemini, API_KEY
from text_analyzer import TextAnalyzer

# Video transcription imports
from moviepy.editor import VideoFileClip
import speech_recognition as sr

class HackathonJudge:
    """
    Comprehensive Hackathon Judging System that evaluates submissions.
    """
    
    def __init__(self, api_key: str):
        """Initialize all analyzers with the API key."""
        print("=" * 80)
        print("🏆 INITIALIZING HACKATHON JUDGING SYSTEM")
        print("=" * 80)
        
        self.api_key = api_key
        # --- THIS IS THE FIX ---
        # The CodeAnalyzer class you are using does not need an API key.
        self.code_analyzer = CodeAnalyzer() 
        self.text_analyzer = TextAnalyzer(api_key=self.api_key)
        
        self.weights = {
            'originality': 0.30, 'feasibility': 0.25, 'impact': 0.20,
            'presentation': 0.15, 'code_quality': 0.10
        }
        self.submissions = []
        print("\n✅ All systems ready!\n")

    # --- All helper methods are now correctly inside the class ---

    def transcribe_video(self, video_path: str) -> Optional[str]:
        """Transcribe video to text using speech recognition."""
        print(f"\n🎥 Transcribing video: {video_path}")
        audio_path = os.path.splitext(video_path)[0] + "_temp.wav"
        try:
            print("  ⏳ Extracting audio from video...")
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)
            
            print("  🎤 Transcribing audio to text...")
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
            
            text = recognizer.recognize_google(audio_data)
            print(f"  ✅ Transcription complete! ({len(text)} characters)")
            return text
        except Exception as e:
            print(f"  ⚠️ Transcription failed: {e}")
            return None
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def process_code_from_github(self, github_url: str, temp_dir: str) -> Optional[str]:
        """Clone GitHub repository and prepare for analysis."""
        print(f"\n💾 Cloning GitHub repository: {github_url}")
        try:
            subprocess.run(
                ['git', 'clone', github_url, temp_dir],
                capture_output=True, text=True, check=True, timeout=60
            )
            print(f"  ✅ Repository cloned successfully")
            return temp_dir
        except Exception as e:
            print(f"  ❌ Error cloning repository: {e}")
            return None

    def process_code_from_manual(self, code_text: str, temp_dir: str) -> Optional[str]:
        """Save manually entered code to temporary file for analysis."""
        print(f"\n📝 Processing manually entered code")
        code_file = os.path.join(temp_dir, "submitted_code.py")
        try:
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code_text)
            print(f"  ✅ Code saved to temporary file")
            return temp_dir
        except Exception as e:
            print(f"  ❌ Error saving code: {e}")
            return None

    def process_code_from_files(self, file_paths: List[str], temp_dir: str) -> Optional[str]:
        """Process uploaded Python files or zip archives."""
        print(f"\n📦 Processing uploaded code files")
        try:
            for file_path in file_paths:
                if file_path.endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    print(f"  ✅ Extracted {os.path.basename(file_path)}")
                elif file_path.endswith('.py'):
                    shutil.copy(file_path, temp_dir)
                    print(f"  ✅ Copied {os.path.basename(file_path)}")
            return temp_dir
        except Exception as e:
            print(f"  ❌ Error processing files: {e}")
            return None
    
    # --- The rest of your class methods remain the same ---

    def _get_rating(self, score: float) -> str:
        if score >= 90: return "⭐⭐⭐⭐⭐ Excellent"
        if score >= 80: return "⭐⭐⭐⭐ Very Good"
        if score >= 70: return "⭐⭐⭐ Good"
        if score >= 60: return "⭐⭐ Fair"
        if score >= 50: return "⭐ Average"
        return "❌ Needs Improvement"
    
    def _verify_claims(self, claims: List[str], code_directory: str) -> Dict:
        if not claims or not os.path.exists(code_directory):
            return {'verified': [], 'unverified': [], 'verification_score': 100.0}
        
        verified, unverified = [], []
        all_code = ""
        for root, _, files in os.walk(code_directory):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            all_code += f.read().lower() + "\n"
                    except: continue
        
        for claim in claims:
            keywords = claim.lower().split()
            if any(keyword in all_code for keyword in keywords if len(keyword) > 3):
                verified.append(claim)
            else:
                unverified.append(claim)
        
        verification_score = (len(verified) / len(claims)) * 100 if claims else 100.0
        return {'verified': verified, 'unverified': unverified, 'verification_score': verification_score}
    
    def evaluate_submission(self, project_name: str, description: str, code_directory: str, presentation_text: Optional[str] = None) -> Dict:
        """Evaluate a single hackathon submission."""
        print(f"\n🔍 EVALUATING SUBMISSION: {project_name}")
        results = {'project_name': project_name, 'timestamp': datetime.now().isoformat(), 'scores': {}, 'evidence': {}, 'warnings': [], 'final_score': 0.0}
        
        # 1. Core Concept Analysis
        impact_res, feas_res = analyze_with_gemini(description)
        results['scores']['originality'] = feas_res.get('score', 50)
        results['evidence']['originality'] = feas_res.get('reasoning', 'N/A')
        results['scores']['feasibility'] = feas_res.get('score', 50)
        results['evidence']['feasibility'] = feas_res.get('reasoning', 'N/A')
        results['scores']['impact'] = impact_res.get('score', 50)
        results['evidence']['impact'] = impact_res.get('reasoning', 'N/A')
        
        # 2. Presentation Quality
        combined_text = description + ("\n\n" + presentation_text if presentation_text else "")
        text_analysis = self.text_analyzer.analyze(combined_text)
        results['scores']['presentation'] = (text_analysis.get('grammar_score', 0) * 0.4 + text_analysis.get('sentiment_score', 0) * 0.3 + text_analysis.get('human_written_score', 0) * 0.3)
        results['evidence']['presentation'] = text_analysis # Store full dictionary
        if text_analysis.get('human_written_score', 100) < 50:
            results['warnings'].append(f"Low human-written probability ({text_analysis['human_written_score']:.1f}%).")
            
        # 3. Code Quality
        if code_directory and os.path.isdir(code_directory):
            code_score, code_evidence = self.code_analyzer.analyze_directory(code_directory) # Use the correct class instance
            results['scores']['code_quality'] = code_score
            results['evidence']['code_quality'] = code_evidence
            if code_score <= 10.0:
                 results['warnings'].append("Critical code quality issues detected.")
        else:
            results['scores']['code_quality'] = 0.0
            results['evidence']['code_quality'] = "No code directory found."
        
        # 4. Claim Verification
        claims = extract_claims_with_gemini(description)
        if claims:
            verification = self._verify_claims(claims, code_directory)
            results['evidence']['claim_verification'] = verification
            if verification['unverified']:
                results['warnings'].append(f"Unverified claims: {', '.join(verification['unverified'][:3])}")
        
        # 5. Final Score
        final_score = sum(results['scores'][crit] * self.weights[crit] for crit in self.weights)
        results['final_score'] = round(final_score, 2)
        results['rating'] = self._get_rating(final_score)
        
        self.submissions.append(results)
        print(f"✅ Evaluation Complete! Final Score: {results['final_score']}/100")
        return results
    
    def generate_judge_report(self, submission: Dict) -> str:
        # (Implementation from your file)
        report = [f"📋 JUDGE REPORT: {submission['project_name']}", f"🏆 FINAL SCORE: {submission['final_score']}/100 ({submission['rating']})\n"]
        for crit, weight in self.weights.items():
            report.append(f"--- {crit.upper()} ({weight*100:.0f}%) ---")
            report.append(f"Score: {submission['scores'][crit]:.2f}/100")
            # Custom formatting for presentation evidence
            if crit == 'presentation':
                pres_ev = submission['evidence']['presentation']
                report.append(f"  - Grammar: {pres_ev.get('grammar_rating', 'N/A')}, Sentiment: {pres_ev.get('sentiment_label', 'N/A')}")
                report.append(f"  - AI Suggestion: {pres_ev.get('ai_suggestion', 'N/A')}")
            else:
                report.append(f"Evidence: {submission['evidence'][crit]}")
            report.append("")
        if submission['warnings']:
            report.append("--- ⚠️ WARNINGS ---")
            report.extend(submission['warnings'])
        return "\n".join(report)

    def generate_leaderboard(self) -> str:
        # (Implementation from your file)
        if not self.submissions: return "No submissions to rank."
        sorted_submissions = sorted(self.submissions, key=lambda x: x['final_score'], reverse=True)
        leaderboard = ["🏆 HACKATHON LEADERBOARD 🏆"]
        for rank, sub in enumerate(sorted_submissions, 1):
            leaderboard.append(f"{rank}. {sub['project_name']} - {sub['final_score']:.2f}/100 ({sub['rating']})")
        return "\n".join(leaderboard)


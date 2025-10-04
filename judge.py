# judge.py - Integrated with Frontend
import os
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import shutil
import tempfile
import zipfile

# Import all analyzers
from code_analyzer import CodeAnalyzer
from llm_analyzer import analyze_with_gemini, extract_claims_with_gemini
from text_analyzer import TextAnalyzer

# Video transcription imports
from moviepy.editor import VideoFileClip
import speech_recognition as sr

class HackathonJudge:
    """
    Comprehensive Hackathon Judging System with video, text, and code analysis.
    Designed to integrate with web frontend.
    """
    
    def __init__(self, api_key: str):
        """Initialize all analyzers with the API key."""
        print("=" * 80)
        print("🏆 INITIALIZING HACKATHON JUDGING SYSTEM")
        print("=" * 80)
        
        self.api_key = api_key
        self.code_analyzer = CodeAnalyzer()
        self.text_analyzer = TextAnalyzer(api_key=api_key)
        
        # Weightage for final score calculation
        self.weights = {
            'originality': 0.30,
            'feasibility': 0.25,
            'impact': 0.20,
            'presentation': 0.15,
            'code_quality': 0.10
        }
        
        self.submissions = []
        print("\n✅ All systems ready!\n")
    
    def _get_rating(self, score: float) -> str:
        """Convert numeric score to rating label."""
        if score >= 90: return "⭐⭐⭐⭐⭐ Excellent"
        if score >= 80: return "⭐⭐⭐⭐ Very Good"
        if score >= 70: return "⭐⭐⭐ Good"
        if score >= 60: return "⭐⭐ Fair"
        if score >= 50: return "⭐ Average"
        return "❌ Needs Improvement"
    
    def transcribe_video(self, video_path: str) -> Optional[str]:
        """
        Transcribe video to text using speech recognition.
        
        Args:
            video_path: Path to the MP4 video file
            
        Returns:
            Transcribed text or None if failed
        """
        print(f"\n🎥 Transcribing video: {video_path}")
        
        audio_path = os.path.splitext(video_path)[0] + "_temp.wav"
        
        try:
            print("  ⏳ Extracting audio from video...")
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)
            video.close()
            
            print("  🎤 Transcribing audio to text...")
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
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
    
    def process_code_from_github(self, github_url: str, temp_dir: str) -> str:
        """
        Clone GitHub repository and prepare for analysis.
        
        Args:
            github_url: GitHub repository URL
            temp_dir: Temporary directory to clone into
            
        Returns:
            Path to cloned repository
        """
        print(f"\n💾 Cloning GitHub repository: {github_url}")
        
        try:
            # Simple git clone (requires git to be installed)
            import subprocess
            result = subprocess.run(
                ['git', 'clone', github_url, temp_dir],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"  ✅ Repository cloned successfully")
                return temp_dir
            else:
                print(f"  ❌ Clone failed: {result.stderr}")
                return None
        
        except Exception as e:
            print(f"  ❌ Error cloning repository: {e}")
            return None
    
    def process_code_from_manual(self, code_text: str, temp_dir: str) -> str:
        """
        Save manually entered code to temporary file for analysis.
        
        Args:
            code_text: Python code as string
            temp_dir: Temporary directory
            
        Returns:
            Path to saved code file
        """
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
    
    def process_code_from_files(self, file_paths: List[str], temp_dir: str) -> str:
        """
        Process uploaded Python files or zip archives.
        
        Args:
            file_paths: List of uploaded file paths
            temp_dir: Temporary directory
            
        Returns:
            Path to processed code directory
        """
        print(f"\n📦 Processing uploaded code files")
        
        try:
            for file_path in file_paths:
                if file_path.endswith('.zip'):
                    # Extract zip file
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    print(f"  ✅ Extracted {file_path}")
                
                elif file_path.endswith('.py'):
                    # Copy Python file
                    shutil.copy(file_path, temp_dir)
                    print(f"  ✅ Copied {file_path}")
            
            return temp_dir
        
        except Exception as e:
            print(f"  ❌ Error processing files: {e}")
            return None
    
    def _verify_claims(self, claims: List[str], code_directory: str) -> Dict:
        """Verify technical claims against actual code implementation."""
        if not claims or not os.path.exists(code_directory):
            return {'verified': [], 'unverified': [], 'verification_score': 100.0}
        
        verified = []
        unverified = []
        
        # Read all code files
        all_code = ""
        for root, _, files in os.walk(code_directory):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            all_code += f.read().lower() + "\n"
                    except:
                        continue
        
        # Check each claim
        for claim in claims:
            claim_lower = claim.lower()
            keywords = claim_lower.split()
            if any(keyword in all_code for keyword in keywords if len(keyword) > 3):
                verified.append(claim)
            else:
                unverified.append(claim)
        
        # Calculate verification score
        total_claims = len(claims)
        if total_claims == 0:
            verification_score = 100.0
        else:
            verification_score = (len(verified) / total_claims) * 100
        
        return {
            'verified': verified,
            'unverified': unverified,
            'verification_score': verification_score
        }
    
    def evaluate_submission(
        self,
        project_name: str,
        description: str,
        video_path: str,
        code_source: str,
        code_data: any,
        additional_text: str = None
    ) -> Dict:
        """
        Evaluate a hackathon submission from frontend.
        
        Args:
            project_name: Name of the project
            description: Project description/pitch
            video_path: Path to MP4 video file
            code_source: 'github', 'manual', or 'file'
            code_data: GitHub URL, code text, or list of file paths
            additional_text: Optional additional documentation
        
        Returns:
            Complete evaluation

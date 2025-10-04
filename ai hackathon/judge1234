# judge.py
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime

# Import all analyzers
from code_analyzer import CodeAnalyzer
from llm_analyzer import analyze_with_gemini, extract_claims_with_gemini
from text_analyzer import TextAnalyzer

class HackathonJudge:
    """
    Comprehensive Hackathon Judging System that evaluates submissions based on:
    - Originality (30%)
    - Technical Feasibility (25%)
    - Impact (20%)
    - Presentation Quality (15%)
    - Code Quality (10%)
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
            # Simple keyword matching for verification
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
        code_directory: str,
        presentation_text: str = None
    ) -> Dict:
        """
        Evaluate a single hackathon submission.
        
        Args:
            project_name: Name of the project
            description: Project description (README, pitch, etc.)
            code_directory: Path to the code directory
            presentation_text: Optional transcribed presentation/video text
        
        Returns:
            Complete evaluation results dictionary
        """
        print("\n" + "=" * 80)
        print(f"🔍 EVALUATING SUBMISSION: {project_name}")
        print("=" * 80)
        
        results = {
            'project_name': project_name,
            'timestamp': datetime.now().isoformat(),
            'scores': {},
            'evidence': {},
            'warnings': [],
            'final_score': 0.0
        }
        
        # 1. ORIGINALITY & IMPACT ANALYSIS (using Gemini)
        print("\n📊 Phase 1: Analyzing Originality and Impact...")
        impact_results, feasibility_results = analyze_with_gemini(description)
        
        originality_score = feasibility_results.get('score', 50)  # Using feasibility as proxy for originality
        results['scores']['originality'] = originality_score
        results['evidence']['originality'] = feasibility_results.get('reasoning', 'No reasoning provided')
        
        # 2. TECHNICAL FEASIBILITY
        print("\n🔧 Phase 2: Evaluating Technical Feasibility...")
        results['scores']['feasibility'] = feasibility_results.get('score', 50)
        results['evidence']['feasibility'] = feasibility_results.get('reasoning', 'No reasoning provided')
        
        # 3. IMPACT ANALYSIS
        print("\n🌍 Phase 3: Assessing Impact...")
        results['scores']['impact'] = impact_results.get('score', 50)
        results['evidence']['impact'] = impact_results.get('reasoning', 'No reasoning provided')
        
        # 4. PRESENTATION QUALITY
        print("\n📝 Phase 4: Analyzing Presentation Quality...")
        combined_text = description
        if presentation_text:
            combined_text += "\n\n" + presentation_text
        
        text_analysis = self.text_analyzer.analyze(combined_text)
        
        # Calculate presentation score (grammar, sentiment, human-written)
        grammar_weight = 0.40
        sentiment_weight = 0.30
        human_weight = 0.30
        
        presentation_score = (
            text_analysis['grammar_score'] * grammar_weight +
            text_analysis['sentiment_score'] * sentiment_weight +
            text_analysis['human_written_score'] * human_weight
        )
        
        results['scores']['presentation'] = presentation_score
        results['evidence']['presentation'] = {
            'grammar_score': text_analysis['grammar_score'],
            'grammar_issues': text_analysis['top_grammatical_changes'][:3],
            'sentiment': text_analysis['sentiment_label'],
            'human_written_probability': text_analysis['human_written_score'],
            'ai_suggestion': text_analysis['ai_suggestion']
        }
        
        # Check for AI-generated content
        if text_analysis['human_written_score'] < 50:
            results['warnings'].append(
                f"⚠️ Low human-written probability ({text_analysis['human_written_score']:.1f}%). "
                "Content may be AI-generated."
            )
        
        # 5. CODE QUALITY ANALYSIS
        print("\n💻 Phase 5: Evaluating Code Quality...")
        if os.path.exists(code_directory) and os.path.isdir(code_directory):
            code_score, code_evidence = self.code_analyzer.analyze_directory(code_directory)
            results['scores']['code_quality'] = code_score
            results['evidence']['code_quality'] = code_evidence
            
            if code_score <= 5.0:
                results['warnings'].append(
                    "⚠️ Critical code quality issues detected. The code has severe problems."
                )
        else:
            results['scores']['code_quality'] = 0.0
            results['evidence']['code_quality'] = "No code directory found."
            results['warnings'].append("⚠️ No code submitted or directory not found.")
        
        # 6. CLAIM VERIFICATION
        print("\n🔍 Phase 6: Verifying Technical Claims...")
        claims = extract_claims_with_gemini(description)
        if claims:
            verification_results = self._verify_claims(claims, code_directory)
            results['evidence']['claim_verification'] = verification_results
            
            if verification_results['unverified']:
                penalty = (1 - verification_results['verification_score'] / 100) * 15
                results['scores']['originality'] = max(0, results['scores']['originality'] - penalty)
                results['warnings'].append(
                    f"⚠️ Unverified claims detected: {', '.join(verification_results['unverified'][:3])}"
                )
        
        # 7. CALCULATE FINAL WEIGHTED SCORE
        print("\n⚖️ Phase 7: Calculating Final Score...")
        final_score = (
            results['scores']['originality'] * self.weights['originality'] +
            results['scores']['feasibility'] * self.weights['feasibility'] +
            results['scores']['impact'] * self.weights['impact'] +
            results['scores']['presentation'] * self.weights['presentation'] +
            results['scores']['code_quality'] * self.weights['code_quality']
        )
        
        results['final_score'] = round(final_score, 2)
        results['rating'] = self._get_rating(final_score)
        
        # Store submission
        self.submissions.append(results)
        
        print(f"\n✅ Evaluation Complete! Final Score: {results['final_score']}/100")
        return results
    
    def generate_judge_report(self, submission: Dict) -> str:
        """Generate a detailed judge report for a submission."""
        report = []
        report.append("=" * 80)
        report.append(f"📋 JUDGE REPORT: {submission['project_name']}")
        report.append("=" * 80)
        report.append(f"\nTimestamp: {submission['timestamp']}")
        report.append(f"\n🏆 FINAL SCORE: {submission['final_score']}/100")
        report.append(f"Rating: {submission['rating']}\n")
        
        report.append("\n" + "-" * 80)
        report.append("📊 DETAILED BREAKDOWN")
        report.append("-" * 80)
        
        # Originality
        report.append(f"\n1️⃣ ORIGINALITY (Weight: {self.weights['originality']*100}%)")
        report.append(f"   Score: {submission['scores']['originality']:.2f}/100")
        report.append(f"   Evidence: {submission['evidence']['originality']}")
        
        # Feasibility
        report.append(f"\n2️⃣ TECHNICAL FEASIBILITY (Weight: {self.weights['feasibility']*100}%)")
        report.append(f"   Score: {submission['scores']['feasibility']:.2f}/100")
        report.append(f"   Evidence: {submission['evidence']['feasibility']}")
        
        # Impact
        report.append(f"\n3️⃣ IMPACT (Weight: {self.weights['impact']*100}%)")
        report.append(f"   Score: {submission['scores']['impact']:.2f}/100")
        report.append(f"   Evidence: {submission['evidence']['impact']}")
        
        # Presentation
        report.append(f"\n4️⃣ PRESENTATION QUALITY (Weight: {self.weights['presentation']*100}%)")
        report.append(f"   Score: {submission['scores']['presentation']:.2f}/100")
        pres = submission['evidence']['presentation']
        report.append(f"   - Grammar Score: {pres['grammar_score']:.2f}/100")
        report.append(f"   - Sentiment: {pres['sentiment']}")
        report.append(f"   - Human-Written: {pres['human_written_probability']:.2f}%")
        if pres['grammar_issues']:
            report.append("   - Grammar Issues Found:")
            for issue in pres['grammar_issues']:
                report.append(f"     • '{issue['mistake']}' → '{issue['correction']}'")
        report.append(f"   - AI Suggestion: {pres['ai_suggestion']}")
        
        # Code Quality
        report.append(f"\n5️⃣ CODE QUALITY (Weight: {self.weights['code_quality']*100}%)")
        report.append(f"   Score: {submission['scores']['code_quality']:.2f}/100")
        report.append(f"   Evidence: {submission['evidence']['code_quality']}")
        
        # Claim Verification
        if 'claim_verification' in submission['evidence']:
            report.append("\n🔍 CLAIM VERIFICATION")
            cv = submission['evidence']['claim_verification']
            report.append(f"   Verification Score: {cv['verification_score']:.2f}%")
            if cv['verified']:
                report.append(f"   ✅ Verified Claims: {', '.join(cv['verified'])}")
            if cv['unverified']:
                report.append(f"   ❌ Unverified Claims: {', '.join(cv['unverified'])}")
        
        # Warnings
        if submission['warnings']:
            report.append("\n⚠️ WARNINGS & RED FLAGS")
            for warning in submission['warnings']:
                report.append(f"   {warning}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)
    
    def generate_leaderboard(self) -> str:
        """Generate a ranked leaderboard of all submissions."""
        if not self.submissions:
            return "No submissions to rank."
        
        # Sort by final score (descending)
        sorted_submissions = sorted(
            self.submissions,
            key=lambda x: x['final_score'],
            reverse=True
        )
        
        leaderboard = []
        leaderboard.append("\n" + "=" * 80)
        leaderboard.append("🏆 HACKATHON LEADERBOARD")
        leaderboard.append("=" * 80)
        leaderboard.append(f"\nTotal Submissions: {len(sorted_submissions)}\n")
        leaderboard.append(f"{'Rank':<6} {'Project Name':<35} {'Score':<10} {'Rating'}")
        leaderboard.append("-" * 80)
        
        for rank, submission in enumerate(sorted_submissions, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            leaderboard.append(
                f"{medal} #{rank:<3} {submission['project_name']:<35} "
                f"{submission['final_score']:.2f}/100  {submission['rating']}"
            )
        
        leaderboard.append("=" * 80)
        return "\n".join(leaderboard)
    
    def save_results(self, output_dir: str = "judge_results"):
        """Save all results to JSON files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual reports
        for submission in self.submissions:
            filename = f"{submission['project_name'].replace(' ', '_')}_report.txt"
            filepath = os.path.join(output_dir, filename)
            
            report = self.generate_judge_report(submission)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
        
        # Save JSON data
        json_filepath = os.path.join(output_dir, "all_results.json")
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.submissions, f, indent=2)
        
        # Save leaderboard
        leaderboard_filepath = os.path.join(output_dir, "leaderboard.txt")
        with open(leaderboard_filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate_leaderboard())
        
        print(f"\n✅ All results saved to '{output_dir}' directory")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    # Initialize the judge with your API key
    API_KEY = "AIzaSyAOr3JM9iPKTYED1P2RZCDfe5w7n-QZ6-Y"
    judge = HackathonJudge(api_key=API_KEY)
    
    # Example: Evaluate a submission
    submission1 = judge.evaluate_submission(
        project_name="AI Healthcare Assistant",
        description="""
        Our project is an AI-powered healthcare assistant that uses machine learning
        to predict patient outcomes. We built it using Python, TensorFlow, and Flask.
        The system analyzes patient data and provides real-time recommendations to doctors.
        It uses a neural network trained on 100,000 patient records and achieves 95% accuracy.
        """,
        code_directory="./sample_project_code",  # Replace with actual path
        presentation_text="Thank you for watching our demo. Our AI system is revolutionary..."
    )
    
    # Generate and print the judge report
    print("\n" + judge.generate_judge_report(submission1))
    
    # You can evaluate more submissions
    # submission2 = judge.evaluate_submission(...)
    # submission3 = judge.evaluate_submission(...)
    
    # Generate leaderboard
    print(judge.generate_leaderboard())
    
    # Save all results
    judge.save_results()

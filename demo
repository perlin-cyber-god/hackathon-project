"""
Configuration and batch evaluation script for Hackathon Judge
"""

import os
import json
from pathlib import Path
from typing import List
from dataclasses import asdict

# Import from main system
# from hackathon_judge import HackathonJudge, JudgingCriteria, ProjectSubmission

class BatchEvaluator:
    """Evaluate multiple projects and rank them"""
    
    def __init__(self, judge):
        self.judge = judge
        self.results = []
    
    def evaluate_all_projects(self, submissions: List) -> List[dict]:
        """Evaluate multiple projects"""
        
        for submission in submissions:
            try:
                result = self.judge.evaluate_project(submission)
                self.results.append(result)
                
                # Generate individual report
                report = self.judge.generate_report(result)
                
                # Save individual results
                output_dir = Path("./evaluation_results")
                output_dir.mkdir(exist_ok=True)
                
                with open(output_dir / f"{submission.project_name}_report.txt", 'w') as f:
                    f.write(report)
                
                with open(output_dir / f"{submission.project_name}_scores.json", 'w') as f:
                    json.dump(result, f, indent=2)
                    
            except Exception as e:
                print(f"Error evaluating {submission.project_name}: {e}")
        
        return self.results
    
    def generate_leaderboard(self) -> str:
        """Generate a leaderboard of all projects"""
        
        # Sort by final score
        sorted_results = sorted(
            self.results, 
            key=lambda x: x['final_score'], 
            reverse=True
        )
        
        leaderboard = f"""
{'='*80}
HACKATHON LEADERBOARD
{'='*80}

Rank | Project Name                          | Score | Percentage
{'='*80}
"""
        
        for idx, result in enumerate(sorted_results, 1):
            project_name = result['project_name'][:35].ljust(35)
            score = f"{result['final_score']}/10"
            percentage = f"{result['final_score_percentage']}%"
            
            leaderboard += f"{idx:3d}  | {project_name} | {score:>6} | {percentage:>7}\n"
        
        leaderboard += f"{'='*80}\n\n"
        
        # Add detailed breakdown
        leaderboard += "DETAILED SCORE BREAKDOWN\n"
        leaderboard += f"{'='*80}\n\n"
        
        for idx, result in enumerate(sorted_results, 1):
            leaderboard += f"{idx}. {result['project_name']} - {result['final_score']}/10\n"
            leaderboard += f"   • Originality: {result['scores'].get('originality', 'N/A')}/10\n"
            leaderboard += f"   • Technical Feasibility: {result['scores'].get('technical_feasibility', 'N/A')}/10\n"
            leaderboard += f"   • Impact: {result['scores'].get('impact', 'N/A')}/10\n"
            leaderboard += f"   • Presentation: {result['scores'].get('presentation_quality', 'N/A')}/10\n"
            leaderboard += f"   • Code Quality: {result['scores'].get('code_quality', 'N/A')}/10\n\n"
        
        return leaderboard
    
    def save_leaderboard(self, filename: str = "leaderboard.txt"):
        """Save leaderboard to file"""
        leaderboard = self.generate_leaderboard()
        
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w') as f:
            f.write(leaderboard)
        
        print(leaderboard)
        print(f"\n✓ Leaderboard saved to {output_dir / filename}")

# Configuration Examples

def example_config_1():
    """Standard hackathon criteria"""
    return {
        "originality": 0.30,
        "technical_feasibility": 0.25,
        "impact": 0.20,
        "presentation_quality": 0.15,
        "code_quality": 0.10
    }

def example_config_2():
    """Code-focused hackathon"""
    return {
        "originality": 0.20,
        "technical_feasibility": 0.25,
        "impact": 0.15,
        "presentation_quality": 0.10,
        "code_quality": 0.30
    }

def example_config_3():
    """Innovation-focused hackathon"""
    return {
        "originality": 0.40,
        "technical_feasibility": 0.20,
        "impact": 0.25,
        "presentation_quality": 0.10,
        "code_quality": 0.05
    }

def setup_project_structure():
    """Create necessary directory structure"""
    
    dirs = [
        "./submissions/team1/code",
        "./submissions/team2/code",
        "./submissions/team3/code",
        "./evaluation_results",
        "./templates"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✓ Project structure created")

def create_sample_readme():
    """Create a sample README for testing"""
    
    sample_readme = """# AI-Powered Mental Health Chatbot

## Problem Statement
Mental health support is often inaccessible due to cost, stigma, and availability constraints. Many people need immediate support but cannot access professional help 24/7.

## Solution
We've developed an AI-powered chatbot that provides:
- 24/7 emotional support and crisis intervention
- Evidence-based cognitive behavioral therapy (CBT) techniques
- Personalized coping strategies based on user history
- Crisis detection and emergency resource connection
- Privacy-focused design with end-to-end encryption

## Technical Implementation
- Frontend: React.js with real-time chat interface
- Backend: Python Flask API with PostgreSQL database
- AI Model: Fine-tuned GPT model on therapy transcripts
- Security: AES-256 encryption, HIPAA compliance
- Deployment: AWS with auto-scaling and load balancing

## Impact
- Provides immediate support to people in crisis
- Reduces barriers to mental health care
- Complements professional therapy, doesn't replace it
- Potential to reach millions of underserved individuals

## Future Enhancements
- Multi-language support
- Integration with wearable devices for mood tracking
- Connection to licensed therapists for escalation
- Community support groups feature
"""
    
    Path("./submissions/team1").mkdir(parents=True, exist_ok=True)
    with open("./submissions/team1/README.md", 'w') as f:
        f.write(sample_readme)
    
    print("✓ Sample README created at ./submissions/team1/README.md")

def create_sample_code():
    """Create sample code files for testing"""
    
    sample_python = """
import openai
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

class MentalHealthChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        self.conversation_history = []
    
    def detect_crisis(self, message):
        \"\"\"Detect if user is in crisis\"\"\"
        crisis_keywords = ['suicide', 'kill myself', 'want to die', 'end it all']
        return any(keyword in message.lower() for keyword in crisis_keywords)
    
    def get_response(self, user_message):
        \"\"\"Generate chatbot response\"\"\"
        if self.detect_crisis(user_message):
            return {
                'message': 'I sense you may be in crisis. Please contact emergency services or call the National Suicide Prevention Lifeline at 988.',
                'crisis': True
            }
        
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=self.conversation_history,
            temperature=0.7
        )
        
        bot_message = response.choices[0].message.content
        self.conversation_history.append({
            'role': 'assistant',
            'content': bot_message
        })
        
        return {'message': bot_message, 'crisis': False}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    chatbot = MentalHealthChatbot(api_key='your-key')
    response = chatbot.get_response(user_message)
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""
    
    Path("./submissions/team1/code").mkdir(parents=True, exist_ok=True)
    with open("./submissions/team1/code/chatbot.py", 'w') as f:
        f.write(sample_python)
    
    print("✓ Sample code created at ./submissions/team1/code/chatbot.py")

# Complete workflow example
def complete_evaluation_workflow():
    """
    Complete workflow for evaluating multiple hackathon projects
    """
    
    print("\n" + "="*70)
    print("HACKATHON JUDGE SYSTEM - COMPLETE WORKFLOW")
    print("="*70 + "\n")
    
    # Step 1: Setup
    print("Step 1: Setting up project structure...")
    setup_project_structure()
    
    # Step 2: Create sample data
    print("\nStep 2: Creating sample data...")
    create_sample_readme()
    create_sample_code()
    
    # Step 3: Initialize judge (uncomment when ready)
    print("\nStep 3: Initialize judge system...")
    print("   ⚠ Remember to set your ANTHROPIC_API_KEY environment variable")
    print("   Example: export ANTHROPIC_API_KEY='your-key-here'")
    
    """
    # Uncomment to run actual evaluation
    
    from hackathon_judge import HackathonJudge, JudgingCriteria, ProjectSubmission
    
    API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    criteria = JudgingCriteria(**example_config_1())
    judge = HackathonJudge(api_key=API_KEY, criteria=criteria)
    
    # Step 4: Define submissions
    submissions = [
        ProjectSubmission(
            project_name="AI Mental Health Chatbot",
            video_path="./submissions/team1/presentation.mp4",
            description_path="./submissions/team1/README.md",
            code_directory="./submissions/team1/code/"
        ),
        ProjectSubmission(
            project_name="Smart Agriculture System",
            video_path="./submissions/team2/presentation.mp4",
            description_path="./submissions/team2/README.md",
            code_directory="./submissions/team2/code/"
        ),
        ProjectSubmission(
            project_name="Blockchain Voting Platform",
            video_path="./submissions/team3/presentation.mp4",
            description_path="./submissions/team3/README.md",
            code_directory="./submissions/team3/code/"
        )
    ]
    
    # Step 5: Batch evaluate
    print("\nStep 4: Evaluating all projects...")
    batch_evaluator = BatchEvaluator(judge)
    results = batch_evaluator.evaluate_all_projects(submissions)
    
    # Step 6: Generate leaderboard
    print("\nStep 5: Generating leaderboard...")
    batch_evaluator.save_leaderboard()
    
    print("\n✓ Evaluation complete!")
    print(f"✓ Results saved in ./evaluation_results/")
    """

if __name__ == "__main__":
    complete_evaluation_workflow()

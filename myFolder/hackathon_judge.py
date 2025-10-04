"""
Batch Evaluator for Multiple Hackathon Projects
Evaluates multiple projects and generates leaderboard
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from hackathon_judge import HackathonJudge, JudgingCriteria, ProjectSubmission

class BatchEvaluator:
    """Evaluate multiple projects and rank them"""
    
    def __init__(self, judge: HackathonJudge):
        self.judge = judge
        self.results = []
    
    def evaluate_all_projects(self, submissions: List[ProjectSubmission]) -> List[Dict[str, Any]]:
        """Evaluate multiple projects"""
        
        print("\n" + "="*70)
        print("BATCH EVALUATION STARTED")
        print("="*70)
        print(f"Total Projects: {len(submissions)}\n")
        
        for idx, submission in enumerate(submissions, 1):
            try:
                print(f"\n[{idx}/{len(submissions)}] Processing: {submission.project_name}")
                print("-" * 70)
                
                result = self.judge.evaluate_project(submission)
                self.results.append(result)
                
                # Generate individual report
                report = self.judge.generate_report(result)
                
                # Save individual results
                output_dir = Path("./evaluation_results")
                output_dir.mkdir(exist_ok=True)
                
                # Sanitize filename
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                                   for c in submission.project_name)
                
                with open(output_dir / f"{safe_name}_report.txt", 'w', encoding='utf-8') as f:
                    f.write(report)
                
                with open(output_dir / f"{safe_name}_scores.json", 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                
                print(f"✅ Completed: {submission.project_name} - Score: {result['final_score']}/10")
                    
            except Exception as e:
                print(f"❌ Error evaluating {submission.project_name}: {e}")
        
        print("\n" + "="*70)
        print("BATCH EVALUATION COMPLETED")
        print("="*70 + "\n")
        
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

Total Projects Evaluated: {len(sorted_results)}

Rank | Project Name                          | Score | Percentage
{'='*80}
"""
        
        for idx, result in enumerate(sorted_results, 1):
            project_name = result['project_name'][:35].ljust(35)
            score = f"{result['final_score']}/10"
            percentage = f"{result['final_score_percentage']}%"
            
            # Add medal emoji for top 3
            medal = ""
            if idx == 1:
                medal = "🥇"
            elif idx == 2:
                medal = "🥈"
            elif idx == 3:
                medal = "🥉"
            
            leaderboard += f"{medal} {idx:2d}  | {project_name} | {score:>6} | {percentage:>7}\n"
        
        leaderboard += f"{'='*80}\n\n"
        
        # Add detailed breakdown
        leaderboard += "DETAILED SCORE BREAKDOWN\n"
        leaderboard += f"{'='*80}\n\n"
        
        for idx, result in enumerate(sorted_results, 1):
            medal = ""
            if idx == 1:
                medal = "🥇 "
            elif idx == 2:
                medal = "🥈 "
            elif idx == 3:
                medal = "🥉 "
            
            leaderboard += f"{medal}{idx}. {result['project_name']} - {result['final_score']}/10 ({result['final_score_percentage']}%)\n"
            leaderboard += f"   • Originality: {result['scores'].get('originality', 'N/A')}/10\n"
            leaderboard += f"   • Technical Feasibility: {result['scores'].get('technical_feasibility', 'N/A')}/10\n"
            leaderboard += f"   • Impact: {result['scores'].get('impact', 'N/A')}/10\n"
            leaderboard += f"   • Presentation: {result['scores'].get('presentation_quality', 'N/A')}/10\n"
            leaderboard += f"   • Code Quality: {result['scores'].get('code_quality', 'N/A')}/10\n\n"
        
        # Add statistics
        leaderboard += f"{'='*80}\n"
        leaderboard += "STATISTICS\n"
        leaderboard += f"{'='*80}\n\n"
        
        scores = [r['final_score'] for r in sorted_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        highest_score = max(scores) if scores else 0
        lowest_score = min(scores) if scores else 0
        
        leaderboard += f"Average Score: {avg_score:.2f}/10\n"
        leaderboard += f"Highest Score: {highest_score:.2f}/10\n"
        leaderboard += f"Lowest Score: {lowest_score:.2f}/10\n"
        leaderboard += f"Score Range: {highest_score - lowest_score:.2f}\n\n"
        
        return leaderboard
    
    def save_leaderboard(self, filename: str = "leaderboard.txt"):
        """Save leaderboard to file"""
        leaderboard = self.generate_leaderboard()
        
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(leaderboard)
        
        print(leaderboard)
        print(f"✓ Leaderboard saved to {output_dir / filename}")
    
    def export_to_csv(self, filename: str = "results.csv"):
        """Export results to CSV for analysis"""
        import csv
        
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Rank', 'Project Name', 'Final Score', 'Percentage',
                'Originality', 'Technical Feasibility', 'Impact',
                'Presentation Quality', 'Code Quality'
            ])
            
            # Sort by score
            sorted_results = sorted(self.results, key=lambda x: x['final_score'], reverse=True)
            
            # Write rows
            for idx, result in enumerate(sorted_results, 1):
                writer.writerow([
                    idx,
                    result['project_name'],
                    result['final_score'],
                    result['final_score_percentage'],
                    result['scores'].get('originality', 'N/A'),
                    result['scores'].get('technical_feasibility', 'N/A'),
                    result['scores'].get('impact', 'N/A'),
                    result['scores'].get('presentation_quality', 'N/A'),
                    result['scores'].get('code_quality', 'N/A')
                ])
        
        print(f"✓ CSV exported to {output_dir / filename}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all evaluations"""
        
        sorted_results = sorted(self.results, key=lambda x: x['final_score'], reverse=True)
        
        # Calculate category averages
        category_scores = {
            'originality': [],
            'technical_feasibility': [],
            'impact': [],
            'presentation_quality': [],
            'code_quality': []
        }
        
        for result in sorted_results:
            for category in category_scores.keys():
                score = result['scores'].get(category)
                if score and score != 'N/A':
                    category_scores[category].append(score)
        
        summary = f"""
{'='*80}
HACKATHON EVALUATION SUMMARY REPORT
{'='*80}

Total Projects: {len(self.results)}
Evaluation Date: {Path('./evaluation_results').stat().st_mtime if Path('./evaluation_results').exists() else 'N/A'}

{'='*80}
CATEGORY AVERAGES
{'='*80}

"""
        
        for category, scores in category_scores.items():
            if scores:
                avg = sum(scores) / len(scores)
                summary += f"{category.replace('_', ' ').title():.<40} {avg:.2f}/10\n"
        
        summary += f"\n{'='*80}\n"
        summary += "TOP 3 PROJECTS\n"
        summary += f"{'='*80}\n\n"
        
        for idx, result in enumerate(sorted_results[:3], 1):
            summary += f"{idx}. {result['project_name']} - {result['final_score']}/10\n"
            
            # Highlight strengths
            strengths = []
            for category, score in result['scores'].items():
                if isinstance(score, (int, float)) and score >= 8:
                    strengths.append(f"{category.replace('_', ' ').title()} ({score}/10)")
            
            if strengths:
                summary += f"   Strengths: {', '.join(strengths)}\n"
            summary += "\n"
        
        summary += f"{'='*80}\n"
        summary += "AREAS FOR IMPROVEMENT\n"
        summary += f"{'='*80}\n\n"
        
        # Find common weak areas
        weak_categories = {}
        for result in sorted_results:
            for category, score in result['scores'].items():
                if isinstance(score, (int, float)) and score < 6:
                    weak_categories[category] = weak_categories.get(category, 0) + 1
        
        if weak_categories:
            sorted_weak = sorted(weak_categories.items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_weak:
                summary += f"• {category.replace('_', ' ').title()}: {count} project(s) scored below 6/10\n"
        else:
            summary += "All projects performed well across all categories!\n"
        
        summary += f"\n{'='*80}\n"
        
        return summary
    
    def save_summary_report(self, filename: str = "summary_report.txt"):
        """Save summary report to file"""
        summary = self.generate_summary_report()
        
        output_dir = Path("./evaluation_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Summary report saved to {output_dir / filename}")


def main():
    """Example usage of BatchEvaluator"""
    
    API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    if not API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set!")
        return
    
    # Define criteria
    criteria = JudgingCriteria(
        originality=0.30,
        technical_feasibility=0.25,
        impact=0.20,
        presentation_quality=0.15,
        code_quality=0.10
    )
    
    # Initialize judge
    judge = HackathonJudge(api_key=API_KEY, criteria=criteria)
    
    # Define submissions
    submissions = [
        ProjectSubmission(
            project_name="Project Alpha",
            description_path="./submissions/team1/README.md",
            code_directory="./submissions/team1/code/"
        ),
        ProjectSubmission(
            project_name="Project Beta",
            description_path="./submissions/team2/README.md",
            code_directory="./submissions/team2/code/"
        ),
        ProjectSubmission(
            project_name="Project Gamma",
            description_path="./submissions/team3/README.md",
            code_directory="./submissions/team3/code/"
        )
    ]
    
    # Batch evaluate
    batch_evaluator = BatchEvaluator(judge)
    results = batch_evaluator.evaluate_all_projects(submissions)
    
    # Generate outputs
    batch_evaluator.save_leaderboard()
    batch_evaluator.export_to_csv()
    batch_evaluator.save_summary_report()
    
    print("\n✅ All evaluations completed!")
    print(f"📂 Check ./evaluation_results/ for all reports")


if __name__ == "__main__":
    main()

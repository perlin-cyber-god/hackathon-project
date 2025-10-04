# text_analyzer.py
from transformers import pipeline
from typing import Tuple, Dict, List
import torch
import google.generativeai as genai
from diff_match_patch import diff_match_patch

class TextAnalyzer:
    """
    A comprehensive text analysis class to evaluate grammar, sentiment,
    and AI-generated content, with added API-powered suggestions.
    """
    def __init__(self, api_key: str):
        """Initializes all the required AI models."""
        print("🔧 Initializing Text Analyzer...")
        
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')
            print("  ✅ Gemini API configured successfully.")
        except Exception as e:
            self.gemini_model = None
            print(f"  ❌ WARNING: Gemini API failed to configure: {e}")
            print("     AI suggestions will be disabled.")

        print("  Loading grammar model...")
        self.grammar_corrector = pipeline('text2text-generation', model='vennify/t5-base-grammar-correction')
        
        print("  Loading sentiment model...")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        print("  Loading AI content detector...")
        self.ai_text_detector = pipeline('text-classification', model='roberta-base-openai-detector')
        
        self.dmp = diff_match_patch()
        print("✅ Text Analyzer ready!\n")

    def _get_rating(self, score: float) -> str:
        """Converts a numeric score (0-100) to a rating label."""
        if score >= 90: return "Excellent"
        if score >= 80: return "Very Good"
        if score >= 70: return "Good"
        if score >= 60: return "Fair"
        if score >= 50: return "Average"
        return "Needs Improvement"

    # --- THIS FUNCTION IS UPGRADED ---
    def _find_differences(self, original_text: str, corrected_text: str) -> List[Dict]:
        """Finds and formats the differences between original and corrected text."""
        diffs = self.dmp.diff_main(original_text, corrected_text)
        self.dmp.diff_cleanupSemantic(diffs)
        
        changes = []
        i = 0
        while i < len(diffs):
            op, data = diffs[i]
            # If a deletion is followed by an insertion, it's a correction
            if op == self.dmp.DIFF_DELETE and i + 1 < len(diffs) and diffs[i+1][0] == self.dmp.DIFF_INSERT:
                mistake = data.strip()
                correction = diffs[i+1][1].strip()
                if mistake and correction: # Ensure neither is empty
                    changes.append({"mistake": mistake, "correction": correction})
                i += 2 # Skip the next item as it's part of the correction
            # If it's just a deletion
            elif op == self.dmp.DIFF_DELETE:
                mistake = data.strip()
                if mistake:
                    changes.append({"mistake": mistake, "correction": "[REMOVED]"})
                i += 1
            # If it's just an insertion
            elif op == self.dmp.DIFF_INSERT:
                correction = data.strip()
                if correction:
                    changes.append({"mistake": "[ADDED]", "correction": correction})
                i += 1
            else: # No change
                i += 1
        return changes[:5] # Return top 5 changes

    def analyze_grammar(self, text: str) -> Tuple[float, int, List[Dict]]:
        """Analyzes grammar, returning score, error count, and a list of changes."""
        if not text.strip():
            return 0.0, 0, []

        corrected_results = self.grammar_corrector(text, max_length=1024)
        corrected_text = corrected_results[0]['generated_text']
        
        changes = self._find_differences(text, corrected_text)
        num_errors = len(changes)

        grammar_score = max(0.0, 100.0 - (num_errors * 10)) # Increased penalty per error
        return grammar_score, num_errors, changes

    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        if not text.strip(): return 50.0, "Neutral"
        result = self.sentiment_analyzer(text[:512])[0]
        score, label = result['score'], result['label']
        return (50 + (score * 50)) if label == 'POSITIVE' else (50 - (score * 50)), label

    def analyze_ai_content(self, text: str) -> float:
        if not text.strip(): return 100.0
        results = self.ai_text_detector(text)
        real_prob = next((item['score'] for item in results if item['label'] == 'Real'), 0.0)
        return real_prob * 100

    def get_nature_suggestion_with_gemini(self, text: str) -> str:
        """Uses the Gemini API to get a suggestion about the nature of the text."""
        if not self.gemini_model or not text.strip():
            return "Gemini API not available or no text provided."

        prompt = f"""
        Analyze the "nature" of the following text. Consider its tone (e.g., formal, casual, persuasive), style, and clarity.
        Provide a concise, one-sentence suggestion for how the author could improve the text's overall impact.
        Text: "{text}"
        Suggestion:
        """
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Could not get suggestion from API: {e}"

    def analyze(self, text: str) -> Dict:
        """Performs a complete analysis and prints a detailed report."""
        print(f"\n{'='*70}\n📝 ANALYZING NEW TEXT...\n{'='*70}")
        
        if not text.strip():
            print("❌ Error: Empty text provided.")
            return {"error": "Empty text provided"}

        grammar_score, error_count, top_errors = self.analyze_grammar(text)
        sentiment_score, sentiment_label = self.analyze_sentiment(text)
        ai_content_score = self.analyze_ai_content(text)
        nature_suggestion = self.get_nature_suggestion_with_gemini(text)

        results = {
            'grammar_score': grammar_score,
            'top_grammatical_changes': top_errors,
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'human_written_score': ai_content_score,
            'ai_suggestion': nature_suggestion
        }
        
        print(f"📊 ANALYSIS REPORT FOR: \"{text[:70]}...\"")
        print("-" * 70)
        
        print("📝 GRAMMAR ANALYSIS:")
        print(f"  - Score: {results['grammar_score']:.2f}/100 ({self._get_rating(results['grammar_score'])})")
        if results['top_grammatical_changes']:
            print("  - Top Grammatical Changes:")
            # --- THIS PRINTOUT IS UPGRADED ---
            for change in results['top_grammatical_changes']:
                print(f"    - Mistake: '{change['mistake']}'  ->  Correction: '{change['correction']}'")
        
        print("\n💭 SENTIMENT ANALYSIS:")
        print(f"  - Score: {results['sentiment_score']:.2f}/100 ({self._get_rating(results['sentiment_score'])})")
        print(f"  - Overall Sentiment: {results['sentiment_label']}")
        
        print("\n🤖 AI CONTENT DETECTION:")
        print(f"  - Human-Written Probability: {results['human_written_score']:.2f}%")
        
        print("\n💡 AI SUGGESTION (Nature of Text):")
        print(f"  - {results['ai_suggestion']}")
        
        print(f"\n{'='*70}\n")
        return results

# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    MY_API_KEY = "AIzaSyAOr3JM9iPKTYED1P2RZCDfe5w7n-QZ6-Y"
    
    if MY_API_KEY == "YOUR_API_KEY_HERE" or not MY_API_KEY:
        print("🚨 WARNING: Add your Gemini API key to the 'MY_API_KEY' variable to enable all features.")
        analyzer = TextAnalyzer(api_key=None)
    else:
        analyzer = TextAnalyzer(api_key=MY_API_KEY)
    
    my_text = "This are a bad sentence with many mistake in grammer. the product is not good i hate it"
    analysis_result = analyzer.analyze(my_text)
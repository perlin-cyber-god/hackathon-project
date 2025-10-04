# analyzers/text_analyzer.py
import language_tool_python
from transformers import pipeline

# Initialize models once to save time
print("Loading text analysis models...")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
grammar_tool = language_tool_python.LanguageTool('en-US')
print("Text models loaded.")

def analyze_text_quality(text):
    """Analyzes text for sentiment and grammar."""
    # 1. Sentiment Analysis
    sentiment_result = sentiment_analyzer(text[:512])[0] # Truncate for model limit
    sentiment_score = sentiment_result['score']
    # Normalize sentiment score to 0-100 scale
    # Positive sentiment is good, negative is bad.
    if sentiment_result['label'] == 'POSITIVE':
        presentation_sentiment_score = 50 + (sentiment_score * 50)
    else:
        presentation_sentiment_score = 50 - (sentiment_score * 50)

    # 2. Grammar and Clarity
    matches = grammar_tool.check(text)
    num_errors = len(matches)
    # Score based on errors per 100 words. Fewer errors = higher score.
    word_count = len(text.split())
    errors_per_100_words = (num_errors / word_count) * 100 if word_count > 0 else 0
    grammar_clarity_score = max(0, 100 - (errors_per_100_words * 10)) # Penalize 10 points per error/100 words

    # Average the two scores for an overall presentation quality score
    final_score = (presentation_sentiment_score + grammar_clarity_score) / 2
    
    evidence = (
        f"Sentiment: {sentiment_result['label']} ({presentation_sentiment_score:.1f}/100). "
        f"Grammar: Found {num_errors} potential errors. ({grammar_clarity_score:.1f}/100)."
    )
    
    return final_score, evidence

if __name__ == '__main__':
    # Quick test
    sample_text = "This is a grate project. We are so excited to present our inovative solution that will definately change the world. Our progress was amazing."
    score, evidence = analyze_text_quality(sample_text)
    print(f"Presentation Quality Score: {score:.2f}/100")
    print(f"Evidence: {evidence}")

# analyzers/text_analyzer.py
from transformers import pipeline
import torch

print("Loading text analysis models...")
# Initialize sentiment analyzer as before
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Initialize a grammar correction pipeline directly from Hugging Face
# This will download the model on the first run.
grammar_corrector = pipeline('text2text-generation', model='vennify/t5-base-grammar-correction')
print("✅ Text models loaded.")


def analyze_text_quality(text):
    """Analyzes text for sentiment and grammar to produce a presentation quality score."""
    # 1. Sentiment Analysis (same as before)
    sentiment_result = sentiment_analyzer(text[:512])[0] 
    sentiment_score = sentiment_result['score']
    
    if sentiment_result['label'] == 'POSITIVE':
        presentation_sentiment_score = 50 + (sentiment_score * 50)
    else:
        presentation_sentiment_score = 50 - (sentiment_score * 50)

    # 2. Grammar and Clarity Analysis using the Hugging Face model
    corrected_results = grammar_corrector(text, max_length=256)
    corrected_text = corrected_results[0]['generated_text']
    
    # A simple way to count errors is to see how many words are different
    # We compare the sets of words to see what was added or removed.
    original_words = set(text.lower().split())
    corrected_words = set(corrected_text.lower().split())
    num_errors = len(original_words.symmetric_difference(corrected_words))

    # Score based on the number of corrections. Fewer corrections = higher score.
    grammar_clarity_score = max(0, 100 - (num_errors * 5)) # Penalize 5 points per error

    # Average the two scores for the final presentation quality score
    final_score = (presentation_sentiment_score + grammar_clarity_score) / 2
    
    evidence = (
        f"Sentiment: {sentiment_result['label']} ({presentation_sentiment_score:.1f}/100). "
        f"Grammar: Found and corrected approximately {num_errors} errors. ({grammar_clarity_score:.1f}/100)."
    )
    
    return final_score, evidence



# This block allows you to test the file directly
if __name__ == '__main__':
    print("\n--- Running a quick test ---")
    sample_text = " Project Name: Agri-Connect Problem: Small-scale farmers in rural regions often face asu duas dajsd uas dnaW USIXDASD O ASMNVURB7T7YUIGZXd NBYAUDIASZ significant crop losses due to diseases they cannot quickly identify. Access to agricultural experts is limited and expensive, leading to incorrect treatments and reduced yield"
    score, evidence = analyze_text_quality(sample_text)
    print(f"Sample Text: \"{sample_text}\"")
    print(f"\nPresentation Quality Score: {score:.2f}/100")
    print(f"Evidence: {evidence}")
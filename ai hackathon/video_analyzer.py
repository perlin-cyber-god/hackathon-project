# video_analyzer.py
import os
import whisper
from typing import Tuple # <--- CHANGE 1: Import Tuple

def transcribe_video(video_path: str) -> Tuple[str, str]: # <--- CHANGE 2: Update the return type hint
    """
    Transcribes the audio from a video file using OpenAI's Whisper model.

    Args:
        video_path (str): The path to the video file.

    Returns:
        A tuple containing the transcript text and an evidence string.
        Returns (None, error_message) if the transcription fails.
    """
    if not os.path.exists(video_path):
        # Return None for the first element to indicate failure
        return None, f"Error: Video file not found at '{video_path}'"
    
    try:
        print("Loading Whisper model (tiny.en)... This may download the model on first run.")
        model = whisper.load_model("tiny.en")
        
        print(f"Starting transcription for {video_path}... This may take a few moments.")
        # Set fp16=False if you are running on a CPU
        result = model.transcribe(video_path, fp16=False) 
        
        transcript = result['text']
        evidence = f"Successfully transcribed video. Found {len(transcript.split())} words."
        
        return transcript, evidence
    except Exception as e:
        return None, f"An error occurred during video processing: {e}"

# This block allows you to test the file directly
if __name__ == '__main__':
    print("\n--- Running a quick test on the video analyzer ---")
    
    sample_video_path = "hackathonsubmission\WhatsApp Video 2025-10-04 at 14.40.09.mp4"
    
    transcript_text, evidence_text = transcribe_video(sample_video_path)
    
    if transcript_text:
        print(f"\n✅ {evidence_text}")
        print("\n--- Transcript ---")
        print(transcript_text)
    else:
        print(f"\n❌ {evidence_text}")
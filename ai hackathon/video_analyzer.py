from moviepy import VideoFileClip
import speech_recognition as sr
import os

def video_to_text(video_path, output_txt_path=None):
    if output_txt_path is None:
        output_txt_path = os.path.splitext(video_path)[0] + ".txt"
    
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    
    try:
        print("Extracting audio from video...")
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec='pcm_s16le')
        video.close()
        
        print("Transcribing audio to text...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"✅ Transcription saved to {output_txt_path}")
        return text
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

# Example
if __name__ == "__main__":
    # Define the path to video_sample folder
    video_folder = os.path.join(os.path.dirname(__file__), "video_sample")
    
    # Check if the folder exists
    if not os.path.exists(video_folder):
        print(f"❌ Error: video_sample folder not found at {video_folder}")
        exit(1)
    
    # Get all video files from the folder
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    
    if not video_files:
        print("❌ No video files found in video_sample folder")
        exit(1)
    
    # Process each video file
    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        print(f"\nProcessing video: {video_file}")
        print(video_to_text(video_path))            

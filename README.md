🛰️ AI Hackathon Judge: Project Nebula
Project Nebula is a multi-modal AI system designed to act as a virtual judge for hackathon submissions. It leverages a suite of specialized analyzers and the power of the Gemini API to provide a comprehensive, objective, and evidence-based evaluation of projects, mimicking the workflow of a human judging panel.

✨ Core Features
Multi-Modal Analysis: Evaluates project submissions across multiple dimensions:

Code Quality: Static analysis for errors, complexity, and best practices.

Written Content: Analyzes project descriptions for grammar, sentiment, and originality.

Video Presentations: Transcribes video/audio to text for presentation quality analysis.

AI-Powered Intelligence: Uses the Google Gemini API for advanced, human-like reasoning to:

Score subjective criteria like Impact and Technical Feasibility.

Detect AI-generated content in project descriptions.

Verify technical claims made in the text against the provided codebase.

Provide conversational feedback and suggestions for improvement.

Interactive Frontend: A user-friendly web interface built with Streamlit, featuring a "Cosmic" theme, that allows for easy submission and displays a detailed, interactive report.

Weighted Scoring & Leaderboard: Computes a final weighted score based on customizable criteria and ranks all evaluated submissions.

🚀 Getting Started
Follow these steps to get the AI Judge running on your local machine.

1. Prerequisites
Python 3.9+

git installed on your system.

An active Google Gemini API key. You can get one from Google AI Studio.

2. Installation
First, clone the repository to your local machine:

git clone <your-repository-url>
cd <repository-folder-name>

Next, install all the required Python libraries using the requirements.txt file:

pip install -r requirements.txt

3. Configuration
Before running the application, you must add your Google Gemini API key.

Open the llm_analyzer.py file.

Find the line API_KEY = "YOUR_API_KEY_HERE".

Replace "YOUR_API_KEY_HERE" with your actual secret API key.

4. Running the Application
Launch the Streamlit web application with the following command in your terminal:

streamlit run app.py

Your web browser will automatically open with the AI Judge's "Mission Control" interface, ready for you to submit a project for evaluation.

📂 Project Structure
The project is organized into a modular structure for clarity and maintainability:

/ai-hackathon-judge/
|
|-- app.py              # The main Streamlit frontend application
|-- judge.py            # The master HackathonJudge class that orchestrates all analyzers
|
|-- code_analyzer.py    # Analyzes code for quality, complexity, and security
|-- text_analyzer.py    # Analyzes text for grammar, sentiment, and AI content
|-- video_analyzer.py   # Transcribes video/audio to text
|-- llm_analyzer.py     # Manages all calls to the Gemini API
|
|-- requirements.txt    # A list of all Python dependencies

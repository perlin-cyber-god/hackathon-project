# app.py - Flask API Server for Hackathon Judge
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename

# Import your judge system
from judge import HackathonJudge

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'py', 'txt', 'mp4', 'zip'}
API_KEY = "AIzaSyAOr3JM9iPKTYED1P2RZCDfe5w7n-QZ6-Y"  # Your Gemini API key

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize judge
judge = HackathonJudge(api_key=API_KEY)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the frontend HTML"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate_submission():
    """
    Main endpoint to evaluate a hackathon submission.
    Expects multipart/form-data with:
    - projectName: string
    - description: string
    - videoFile: file (mp4)
    - textFile: file (txt, optional)
    - codeSource: 'github' | 'manual' | 'file'
    - githubUrl: string (if codeSource=github)
    - manualCode: string (if codeSource=manual)
    - codeFiles: files (if codeSource=file)
    """
    try:
        # Extract form data
        project_name = request.form.get('projectName')
        description = request.form.get('description')
        code_source = request.form.get('codeSource')
        
        if not project_name or not description:
            return jsonify({'error': 'Project name and description are required'}), 400
        
        # Create temporary directory for this submission
        temp_dir = tempfile.mkdtemp(prefix='hackathon_')
        
        # Process video file
        video_path = None
        if 'videoFile' in request.files:
            video_file = request.files['videoFile']
            if video_file and allowed_file(video_file.filename):
                filename = secure_filename(video_file.filename)
                video_path = os.path.join(temp_dir, filename)
                video_file.save(video_path)
        
        if not video_path:
            return jsonify({'error': 'Valid video file (.mp4) is required'}), 400
        
        # Process additional text file (optional)
        additional_text = None
        if 'textFile' in request.files:
            text_file = request.files['textFile']
            if text_file and allowed_file(text_file.filename):
                additional_text = text_file.read().decode('utf-8')
        
        # Process code based on source
        code_data = None
        if code_source == 'github':
            code_data = request.form.get('githubUrl')
        elif code_source == 'manual':
            code_data = request.form.get('manualCode')
        elif code_source == 'file':
            code_files = request.files.getlist('codeFiles')
            code_data = []
            for code_file in code_files:
                if code_file and allowed_file(code_file.filename):
                    filename = secure_filename(code_file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    code_file.save(file_path)
                    code_data.append(file_path)
        
        if not code_data:
            return jsonify({'error': 'Code submission is required'}), 400
        
        # Run evaluation
        result = judge.evaluate_submission(
            project_name=project_name,
            description=description,
            video_path=video_path,
            code_source=code_source,
            code_data=code_data,
            additional_text=additional_text
        )
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Return results
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        # Clean up on error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the current leaderboard"""
    try:
        leaderboard_text = judge.generate_leaderboard()
        
        # Parse leaderboard into structured data
        submissions = sorted(
            judge.submissions,
            key=lambda x: x['final_score'],
            reverse=True
        )
        
        leaderboard_data = []
        for rank, submission in enumerate(submissions, 1):
            leaderboard_data.append({
                'rank': rank,
                'project_name': submission['project_name'],
                'final_score': submission['final_score'],
                'rating': submission['rating']
            })
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data,
            'total_submissions': len(submissions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<project_name>', methods=['GET'])
def get_report(project_name):
    """Get detailed report for a specific project"""
    try:
        # Find submission
        submission = next(
            (s for s in judge.submissions if s['project_name'] == project_name),
            None
        )
        
        if not submission:
            return jsonify({'error': 'Project not found'}), 404
        
        report = judge.generate_judge_report(submission)
        
        return jsonify({
            'success': True,
            'report': report,
            'submission': submission
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-results', methods=['POST'])
def save_results():
    """Save all results to files"""
    try:
        output_dir = request.json.get('output_dir', 'judge_results')
        judge.save_results(output_dir=output_dir)
        
        return jsonify({
            'success': True,
            'message': f'Results saved to {output_dir}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 80)
    print("STARTING HACKATHON JUDGE API SERVER")
    print("=" * 80)
    print(f"Server running at: http://localhost:5000")
    print(f"Frontend available at: http://localhost:5000")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from utils.ai_analyzer import analyze_evidence
from utils.firebase_storage import save_to_storage, save_metadata
from utils.pdf_generator import generate_pdf
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_evidence():
    # Check if file is present in request
    if 'evidence' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['evidence']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file temporarily
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Analyze evidence using Vertex AI
    analysis = analyze_evidence(file_path)
    
    # Save to Firebase Storage and get URL
    storage_url = save_to_storage(file_path)
    
    # Save metadata to Firestore and get report ID
    report_id = save_metadata(analysis, storage_url, file.filename)
    
    # Generate PDF report
    pdf_path = generate_pdf(analysis, report_id)
    
    # Return response with report details
    return jsonify({
        'message': 'Report generated successfully',
        'report_id': report_id,
        'pdf_url': pdf_path  # Assuming local path; in production, upload to storage
    })

if __name__ == '__main__':
    app.run(debug=True)

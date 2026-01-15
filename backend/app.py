# app.py
import os
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
import os
import sys
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import uuid
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Path Corrections Based on Folder Structure ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
sys.path.append(BASE_DIR)

from utils.ai_analyzer import analyze_evidence, analyze_evidence_advanced
from utils.firebase_storage import save_to_storage, save_metadata, get_pdf_from_firestore
from utils.firestore_manager import firestore_manager
from utils.pdf_generator import generate_pdf

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve index.html from the root
@app.route('/')
def serve_frontend():
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    else:
        return "frontend/index.html not found at " + app.static_folder, 404

# Serve other static files
@app.route('/frontend')
def static_files(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return "File not found", 404

# API route for standard upload
@app.route('/upload', methods=['POST'])
def upload_evidence():
    if 'evidence' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['evidence']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        # Get language preference
        language = request.form.get('language', 'en')
        
        # 1. Analyze
        analysis = analyze_evidence(file_path)
        if not analysis:
            raise Exception("AI analysis returned empty.")

        # 2. Upload to Storage
        storage_url = save_to_storage(file_path)

        # 3. Generate PDF with language support
        temp_report_id = str(uuid.uuid4())
        pdf_bytes = generate_pdf(analysis, temp_report_id, language=language)

        # 4. Save metadata and PDF to Firestore
        report_id = save_metadata(analysis, storage_url, file.filename, pdf_bytes)

        # 5. Return analysis text to frontend
        return jsonify({
            'message': 'Report generated successfully',
            'report_id': report_id,
            'pdf_url': f'/reports/{report_id}',
            'analysis': analysis
        })

    except Exception as e:
        logger.error(f"Upload process error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'An error occurred: {e}'}), 500

# Advanced analysis endpoint
# In your app.py, update the import section and advanced analysis endpoint:

# Remove this problematic import line:
# from utils.pdf_generator import generate_pdf

# Replace with direct import at the function level:
@app.route('/api/analyze-advanced', methods=['POST'])
def analyze_evidence_advanced_route():
    """Advanced analysis endpoint"""
    # Import here to avoid circular imports
    from utils.pdf_generator import generate_pdf
    
    if 'evidence' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['evidence']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        # Get language preference
        language = request.form.get('language', 'en')
        
        # Use enhanced analysis flow
        from utils.advanced_analyzer import advanced_analyzer
        basic_analysis = analyze_evidence(file_path)
        enhanced_analysis_data = advanced_analyzer.enhance_ai_analysis(file_path, basic_analysis)
        
        # Extract the actual analysis text
        if isinstance(enhanced_analysis_data, dict) and 'basic_analysis' in enhanced_analysis_data:
            analysis = enhanced_analysis_data['basic_analysis']
            advanced_features = enhanced_analysis_data.get('advanced_features', {})
        else:
            analysis = enhanced_analysis_data
            advanced_features = {}
        
        # Store in Firestore with new schema
        case_data = {
            'title': f"Case Analysis - {file.filename}",
            'officerId': request.form.get('officerId', 'default_officer'),
            'description': request.form.get('description', ''),
            'evidenceType': file.content_type,
            'language': language
        }
        
        case_id = firestore_manager.create_case_document(case_data)
        
        evidence_data = {
            'filename': file.filename,
            'filePath': file_path,
            'analysis': analysis,
            'advanced_features': advanced_features,
            'analysisType': 'advanced',
            'fileType': file.content_type,
            'language': language
        }
        
        evidence_id = firestore_manager.add_evidence_to_case(case_id, evidence_data)
        
        # Generate PDF report with language support - use imported function
        pdf_bytes = generate_pdf(analysis, evidence_id, language=language, enhanced_data=enhanced_analysis_data)
        
        # Store PDF in Firestore
        report_data = {
            'filename': file.filename,
            'evidence_url': f'/reports/{evidence_id}',
            'analysis': analysis,
            'advanced_features': advanced_features,
            'pdf_bytes': pdf_bytes,
            'timestamp': firestore_manager.get_server_timestamp(),
            'case_id': case_id,
            'evidence_id': evidence_id,
            'language': language
        }
        
        firestore_manager.db.collection('reports').document(evidence_id).set(report_data)
        
        return jsonify({
            'message': 'Advanced analysis completed',
            'case_id': case_id,
            'evidence_id': evidence_id,
            'analysis': analysis,
            'advanced_features': advanced_features,
            'pdf_url': f'/reports/{evidence_id}'
        })
        
    except Exception as e:
        logger.error(f"Advanced analysis error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

# Case management endpoints
@app.route('/api/cases', methods=['GET'])
def get_cases():
    """Get all cases with optional filtering"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('officerId'):
            filters['officerId'] = request.args.get('officerId')
        
        cases = firestore_manager.search_cases_by_metadata(filters)
        return jsonify({'cases': cases})
    
    except Exception as e:
        logger.error(f"Get cases error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cases/<case_id>/evidence', methods=['GET'])
def get_case_evidence(case_id):
    """Get all evidence for a specific case"""
    try:
        evidence = firestore_manager.get_case_evidence(case_id)
        return jsonify({'evidence': evidence})
    
    except Exception as e:
        logger.error(f"Get case evidence error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cases/create', methods=['POST'])
def create_case():
    """Create a new case"""
    try:
        case_data = request.json
        case_id = firestore_manager.create_case_document(case_data)
        return jsonify({'case_id': case_id, 'message': 'Case created successfully'})
    
    except Exception as e:
        logger.error(f"Create case error: {e}")
        return jsonify({'error': str(e)}), 500

# Evidence Q&A endpoint
@app.route('/api/evidence/<evidence_id>/ask', methods=['POST'])
def ask_evidence_question(evidence_id):
    """Ask questions about specific evidence"""
    try:
        question = request.json.get('question', '')
        
        # Get the evidence analysis from Firestore
        evidence_ref = firestore_manager.db.collection('reports').document(evidence_id)
        evidence_doc = evidence_ref.get()
        
        if not evidence_doc.exists:
            return jsonify({'error': 'Evidence not found'}), 404
            
        evidence_data = evidence_doc.to_dict()
        analysis_text = evidence_data.get('analysis', '')
        advanced_features = evidence_data.get('advanced_features', {})
        
        # Enhanced Q&A with advanced features
        answer = generate_enhanced_answer(question, analysis_text, advanced_features)
        
        return jsonify({
            'evidence_id': evidence_id,
            'question': question,
            'answer': answer,
            'confidence': 0.85
        })
    
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        return jsonify({'error': str(e)}), 500

def generate_enhanced_answer(question, analysis_text, advanced_features):
    """Generate enhanced answers using advanced features"""
    question_lower = question.lower()
    analysis_lower = analysis_text.lower()
    
    # Check advanced features first
    if 'detailed_timeline' in advanced_features:
        timeline = advanced_features['detailed_timeline']
        if any(keyword in question_lower for keyword in ['timeline', 'when', 'time', 'sequence']):
            timeline_summary = f"Advanced timeline analysis detected {len(timeline)} key events. "
            if timeline:
                timeline_summary += f"First event at {timeline[0].get('timestamp_formatted', 'unknown')}: {timeline[0].get('event', '')}"
            return timeline_summary + " Full timeline available in the detailed report."
    
    if 'objects_tracked' in advanced_features and advanced_features['objects_tracked'] > 0:
        if any(keyword in question_lower for keyword in ['object', 'item', 'thing', 'track']):
            return f"Object tracking detected {advanced_features['objects_tracked']} objects. Detailed object analysis available in the report."
    
    if 'scene_changes' in advanced_features and advanced_features['scene_changes'] > 0:
        if any(keyword in question_lower for keyword in ['scene', 'location', 'setting', 'background']):
            return f"Scene analysis identified {advanced_features['scene_changes']} scene changes. Environmental context available in detailed analysis."
    
    # Fallback to basic keyword matching
    if 'vehicle' in question_lower or 'car' in question_lower or 'plate' in question_lower:
        if 'tn' in analysis_lower:
            return "Vehicle information detected in the analysis. Tamil Nadu license plates and vehicle descriptions are available in the detailed report."
        return "Vehicle-related information may be present in the evidence. Check the detailed analysis for specific vehicle observations."
    
    elif 'time' in question_lower or 'when' in question_lower:
        return "Timestamps and temporal analysis are included in the evidence report. Refer to the chronological timeline section."
    
    elif 'person' in question_lower or 'people' in question_lower or 'face' in question_lower:
        return "Person and facial analysis details are available in the evidence report. Check the face analysis and object tracking sections."
    
    elif 'location' in question_lower or 'where' in question_lower:
        if 'chennai' in analysis_lower or 'tamil nadu' in analysis_lower:
            return "Location information specific to Tamil Nadu is mentioned in the analysis. Refer to the location details in the report."
        return "Geographic and location analysis is part of the evidence examination. Check the detailed report for specific location information."
    
    else:
        return "The evidence analysis contains detailed observations relevant to your investigation. For specific details, please refer to the comprehensive report sections covering scene analysis, object tracking, and key findings."

# Enhanced analysis flow
def enhanced_analysis_flow(file_path):
    """Enhanced analysis flow combining basic AI and advanced features"""
    try:
        # 1. Get basic AI analysis
        basic_analysis = analyze_evidence(file_path)
        
        # 2. Enhance with advanced features if available
        from utils.advanced_analyzer import advanced_analyzer
        enhanced_analysis = advanced_analyzer.enhance_ai_analysis(file_path, basic_analysis)
        
        return enhanced_analysis
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        # Fallback to basic analysis
        return analyze_evidence(file_path)

# Route to serve PDF from Firestore
@app.route('/reports/<report_id>', methods=['GET'])
def serve_pdf(report_id):
    pdf_bytes = get_pdf_from_firestore(report_id)
    if pdf_bytes:
        response = Response(pdf_bytes, mimetype='application/pdf')
        response.headers['Content-Disposition'] = f'inline; filename=report_{report_id}.pdf'
        return response
    else:
        return jsonify({'error': 'Report not found'}), 404

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Alfa Labs Evidence Analyzer',
        'version': '2.1.0',
        'features': ['basic_analysis', 'advanced_analysis', 'case_management', 'qa_system', 'multilingual_reports']
    })

if __name__ == '__main__':
    logger.info("Starting Alfa Labs Evidence Analyzer...")
    app.run(debug=True, port=5000)
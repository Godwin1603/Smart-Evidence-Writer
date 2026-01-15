# ai_analyzer.py
import mimetypes
import sys
import os
from datetime import datetime
import logging

# --- Path correction for config ---
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(UTILS_DIR)
sys.path.append(BACKEND_DIR)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Vertex AI with multiple fallbacks
VERTEX_AI_AVAILABLE = False
generative_ai_available = False

try:
    # Try new Vertex AI Gemini imports
    from vertexai.preview.generative_models import GenerativeModel, Part
    VERTEX_AI_AVAILABLE = True
    logger.info("✅ Vertex AI Generative Models imported successfully")
except ImportError as e:
    logger.warning(f"❌ Vertex AI Generative Models import failed: {e}")
    try:
        # Try alternative import path
        from vertexai.generative_models import GenerativeModel, Part
        VERTEX_AI_AVAILABLE = True
        logger.info("✅ Vertex AI Generative Models imported via alternative path")
    except ImportError as e2:
        logger.warning(f"❌ Alternative Vertex AI import failed: {e2}")
        try:
            # Try Google Generative AI as fallback
            import google.generativeai as genai
            generative_ai_available = True
            logger.info("✅ Google Generative AI available as fallback")
        except ImportError as e3:
            logger.warning(f"❌ Google Generative AI also unavailable: {e3}")

# Initialize if available
model = None
if VERTEX_AI_AVAILABLE:
    try:
        from config import VERTEX_AI_PROJECT_ID, VERTEX_AI_LOCATION, VERTEX_AI_MODEL
        import vertexai
        vertexai.init(project=VERTEX_AI_PROJECT_ID, location=VERTEX_AI_LOCATION)
        model = GenerativeModel(VERTEX_AI_MODEL)
        logger.info("✅ Vertex AI initialized successfully")
    except Exception as e:
        logger.error(f"❌ Vertex AI initialization failed: {e}")
        VERTEX_AI_AVAILABLE = False

elif generative_ai_available:
    try:
        from config import VERTEX_AI_MODEL
        import google.generativeai as genai
        # For generativeai, you might need to configure API key differently
        model = genai.GenerativeModel(VERTEX_AI_MODEL)
        logger.info("✅ Google Generative AI configured")
    except Exception as e:
        logger.error(f"❌ Google Generative AI configuration failed: {e}")
        generative_ai_available = False

def _get_file_metadata(file_path):
    """Extract basic file metadata"""
    try:
        stat_info = os.stat(file_path)
        file_size = stat_info.st_size
        created_time = datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
        
        return {
            'size_bytes': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'created': created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
            'filename': os.path.basename(file_path)
        }
    except Exception as e:
        logger.warning(f"Could not extract file metadata: {e}")
        return {}

# ai_analyzer.py - UPDATED PROMPTS SECTION
def _get_media_specific_prompt(mime_type, metadata):
    """Generate specialized prompts based on media type"""
    base_prompt = """
You are a Tamil Nadu Police evidence analyst. Generate a STRUCTURED police evidence report with SPECIFIC details.

CRITICAL REQUIREMENTS:
- Be SPECIFIC: Describe exact actions, appearances, timestamps
- Use STRUCTURED sections: Executive Summary, Detailed Analysis, Timeline, Key Findings
- Include TIMESTAMPS for video/audio analysis
- Identify VEHICLE plates (TN series), people descriptions, locations
- Focus on ACTIONABLE investigative leads

"""
    
    if mime_type.startswith('image/'):
        return base_prompt + """
IMAGE ANALYSIS - BE SPECIFIC:

1. EXECUTIVE SUMMARY:
   - Brief overview of what the image shows
   - Most critical evidence visible

2. DETAILED ANALYSIS:
   - SCENE: Exact location features, time of day, weather, lighting
   - PEOPLE: Count, gender, approximate age, height, build, clothing colors/types, distinctive features
   - VEHICLES: Make, model, color, TN plate numbers (be exact), modifications, damage
   - OBJECTS: Weapons, bags, phones, documents - describe precisely
   - ENVIRONMENT: Building types, road conditions, Tamil/English signage

3. CHRONOLOGICAL TIMELINE (if applicable):
   - Sequence of events visible in the image

4. KEY EVIDENCE FINDINGS:
   - Vehicle plates found: [list exact plates]
   - Suspicious activities: [describe exactly]
   - Identifiable features: [specific details]

EXAMPLE: "Male, approx 25-30 years, 5'8", wearing blue shirt and black pants, carrying black backpack. Vehicle: White Maruti Suzuki with TN-09-AB-1234 partially visible."

"""

    elif mime_type.startswith('video/'):
        return base_prompt + """
VIDEO ANALYSIS - INCLUDE TIMESTAMPS:

1. EXECUTIVE SUMMARY:
   - Total duration and key events overview

2. TEMPORAL ANALYSIS:
   - Total Duration: [exact duration]
   - Key Timestamps of Significant Events with EXACT times:
     * [00:00-00:03]: Describe exact initial actions
     * [00:03-00:06]: Describe specific physical interactions
     * Continue for all significant events...

3. DETAILED EVIDENCE ANALYSIS:
   - PEOPLE: Track each individual with descriptions and their specific actions
   - VEHICLES: Movements, plate visibility at specific timestamps, maneuvers
   - INTERACTIONS: Exact nature of interactions (verbal argument, physical fight, etc.)
   - BYSTANDERS: Count and their behaviors

4. CHRONOLOGICAL TIMELINE:
   - Event 1: [00:00-00:03] - Exact description of what happens
   - Event 2: [00:03-00:06] - Exact description of escalation
   - Continue sequentially...

5. KEY EVIDENCE FINDINGS:
   - Vehicles: [Describe parked/moving vehicles with plate info]
   - Vehicle Movements: [Specific maneuvers observed]
   - Number Plate Visibility: [Which plates are visible and when]
   - Critical Actions: [Specific violent or suspicious acts]

EXAMPLE: "At 00:03, individual in red shirt throws punch at individual in blue shirt. At 00:06, white car TN-09-XY-5678 enters frame from left."

"""

    elif mime_type.startswith('audio/'):
        return base_prompt + """
AUDIO ANALYSIS - INCLUDE TIMESTAMPS:

1. EXECUTIVE SUMMARY:
   - Main conversation topics and speakers

2. DETAILED ANALYSIS:
   - SPEAKERS: Number, gender, approximate age, emotional state
   - LANGUAGES: Tamil, English, mix - specify which parts
   - CONTENT: Exact key phrases, names, locations mentioned
   - BACKGROUND: Ambient sounds indicating location

3. CHRONOLOGICAL TIMELINE:
   - [00:00-00:30]: Conversation about [specific topic]
   - [00:30-01:15]: Argument about [specific issue]
   - Include exact timestamps for key statements

4. KEY EVIDENCE FINDINGS:
   - Critical statements made
   - Names/places mentioned
   - Potential criminal intent

"""
    
    else:
        return base_prompt + """
DOCUMENT ANALYSIS - BE SPECIFIC:

1. EXECUTIVE SUMMARY:
   - Document type and key findings

2. DETAILED ANALYSIS:
   - NAMES: Exact names mentioned
   - DATES: Specific dates and times
   - LOCATIONS: Exact addresses or places
   - FINANCIAL: Specific amounts, transactions
   - CONTACTS: Phone numbers, addresses

3. KEY EVIDENCE FINDINGS:
   - Critical identifiers found
   - Suspicious content
   - Investigative leads

"""
# Add this function to ai_analyzer.py
def analyze_evidence_with_language(file_path, language='en'):
    """
    Analyze evidence with language support
    """
    # Your existing analysis logic here
    analysis_result = analyze_evidence(file_path)
    
    # Return both analysis and language for PDF generation
    return {
        'analysis': analysis_result,
        'language': language
    }

def _validate_file(file_path):
    """Validate file before processing"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError("File is empty")
    
    MAX_SIZE = 100 * 1024 * 1024  # 100MB
    if file_size > MAX_SIZE:
        raise ValueError(f"File too large: {file_size} bytes (max: {MAX_SIZE} bytes)")
    
    return True

def analyze_evidence(file_path):
    """
    Analyze evidence with multiple fallback options
    """
    try:
        # Validate file
        _validate_file(file_path)
        
        # Get file metadata
        metadata = _get_file_metadata(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        logger.info(f"Processing file: {metadata.get('filename')}, Type: {mime_type}")

        # If no AI available, use fallback
        if not VERTEX_AI_AVAILABLE and not generative_ai_available:
            from utils.fallback_analyzer import fallback_analyzer
            return fallback_analyzer.analyze_evidence(file_path)

        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Get specialized prompt
        prompt = _get_media_specific_prompt(mime_type, metadata)
        
        # Add metadata context
        metadata_context = f"""
File Information:
- Name: {metadata.get('filename', 'Unknown')}
- Size: {metadata.get('size_mb', 'Unknown')} MB
- Type: {mime_type}

Analysis Context: Tamil Nadu Police Evidence Investigation
"""
        full_prompt = metadata_context + prompt

        # Try Vertex AI first
        if VERTEX_AI_AVAILABLE and model:
            try:
                # Prepare Part based on MIME type
                if mime_type.startswith('image/'):
                    part = Part.from_data(data=file_data, mime_type=mime_type)
                elif mime_type.startswith('video/'):
                    part = Part.from_data(data=file_data, mime_type=mime_type)
                elif mime_type.startswith('audio/'):
                    part = Part.from_data(data=file_data, mime_type=mime_type)
                else:
                    try:
                        text_content = file_data.decode('utf-8')
                    except UnicodeDecodeError:
                        text_content = "[Binary file - content not readable as text]"
                    part = Part.from_text(text=text_content)

                # Generate content
                response = model.generate_content(
                    [full_prompt, part],
                    generation_config={
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                
                media_type_note = f"\n\n--- Analysis of {mime_type.upper()} file: {metadata.get('filename', 'Unknown')} ---\n"
                return media_type_note + response.text

            except Exception as ai_error:
                logger.error(f"Vertex AI analysis failed: {ai_error}")
                # Fall through to fallback

        # If we reach here, use fallback
        from utils.fallback_analyzer import fallback_analyzer
        return fallback_analyzer.analyze_evidence(file_path)

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        from utils.fallback_analyzer import fallback_analyzer
        return fallback_analyzer.analyze_evidence(file_path)

def analyze_evidence_advanced(file_path):
    """
    Advanced evidence analysis - uses same as basic for now
    """
    return analyze_evidence(file_path)

def batch_analyze_evidence(file_paths):
    """
    Analyze multiple evidence files and return combined report
    """
    results = []
    for file_path in file_paths:
        try:
            logger.info(f"Analyzing {file_path}...")
            analysis = analyze_evidence(file_path)
            results.append({
                'file': os.path.basename(file_path),
                'analysis': analysis,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            results.append({
                'file': os.path.basename(file_path),
                'analysis': f"Analysis failed: {str(e)}",
                'status': 'error'
            })
    
    # Generate combined report
    combined_report = "COMBINED EVIDENCE ANALYSIS REPORT\n"
    combined_report += "=" * 50 + "\n\n"
    
    for result in results:
        combined_report += f"FILE: {result['file']}\n"
        combined_report += f"STATUS: {result['status'].upper()}\n"
        combined_report += f"ANALYSIS:\n{result['analysis']}\n"
        combined_report += "-" * 50 + "\n\n"
    
    return combined_report

# Example usage and testing
if __name__ == "__main__":
    test_file = "sample_evidence.jpg"
    if os.path.exists(test_file):
        print("Testing AI analyzer...")
        result = analyze_evidence(test_file)
        print("Analysis Result:")
        print(result)
    else:
        print("No test file found - system ready for uploads")
# Configuration for Firebase and Vertex AI
import os
from dotenv import load_dotenv
load_dotenv()

# Firebase settings
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase-key.json')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'your-project-id.appspot.com')

# Vertex AI settings
VERTEX_AI_PROJECT_ID = os.getenv('VERTEX_AI_PROJECT_ID', 'your-project-id')
VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
VERTEX_AI_MODEL = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-exp')

# Flask settings
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# utils/firestore_manager.py
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1 import ArrayUnion
import hashlib
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREBASE_CRED_PATH

# Initialize Firestore
cred = firebase_admin.credentials.Certificate(FIREBASE_CRED_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

class FirestoreManager:
    def __init__(self):
        self.db = db
    
    def get_server_timestamp(self):
        """Get server timestamp for Firestore"""
        return firestore.SERVER_TIMESTAMP
    
    def create_case_document(self, case_data):
        """Create a new case document"""
        case_ref = self.db.collection('cases').document()
        
        case_data.update({
            'createdAt': self.get_server_timestamp(),
            'updatedAt': self.get_server_timestamp(),
            'status': 'active',
            'evidenceCount': 0
        })
        
        case_ref.set(case_data)
        return case_ref.id
    
    def add_evidence_to_case(self, case_id, evidence_data):
        """Add evidence analysis to a case"""
        case_ref = self.db.collection('cases').document(case_id)
        evidence_ref = case_ref.collection('evidence').document()
        
        # Generate hash for chain of custody
        file_hash = self._generate_file_hash(evidence_data.get('file_path', ''))
        
        evidence_data.update({
            'evidenceId': evidence_ref.id,
            'addedAt': self.get_server_timestamp(),
            'fileHash': file_hash,
            'analysisStatus': 'completed'
        })
        
        evidence_ref.set(evidence_data)
        
        # Update case timestamp and evidence count
        case_ref.update({
            'updatedAt': self.get_server_timestamp(),
            'evidenceCount': firestore.Increment(1)
        })
        
        return evidence_ref.id
    
    def store_analysis_embeddings(self, case_id, evidence_id, analysis_text):
        """Store analysis embeddings for semantic search"""
        embeddings_ref = self.db.collection('cases').document(case_id)\
            .collection('evidence').document(evidence_id)\
            .collection('embeddings').document('analysis')
        
        embedding_data = {
            'rawText': analysis_text,
            'processedAt': self.get_server_timestamp(),
            'embeddingStatus': 'pending'
        }
        
        embeddings_ref.set(embedding_data)
        return True
    
    def _generate_file_hash(self, file_path):
        """Generate SHA-256 hash for chain of custody"""
        if not os.path.exists(file_path):
            return "file_not_found"
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def get_case_evidence(self, case_id):
        """Get all evidence for a case"""
        evidence_ref = self.db.collection('cases').document(case_id).collection('evidence')
        docs = evidence_ref.stream()
        
        evidence_list = []
        for doc in docs:
            evidence_data = doc.to_dict()
            evidence_data['id'] = doc.id
            evidence_list.append(evidence_data)
        
        return evidence_list
    
    def search_cases_by_metadata(self, filters):
        """Search cases by metadata filters"""
        cases_ref = self.db.collection('cases')
        
        # Build query based on filters
        query = cases_ref
        if 'status' in filters:
            query = query.where('status', '==', filters['status'])
        if 'officerId' in filters:
            query = query.where('officerId', '==', filters['officerId'])
        
        docs = query.stream()
        cases = []
        for doc in docs:
            case_data = doc.to_dict()
            case_data['id'] = doc.id
            cases.append(case_data)
        
        return cases

# Singleton instance
firestore_manager = FirestoreManager()
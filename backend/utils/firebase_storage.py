import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREBASE_CRED_PATH, FIREBASE_STORAGE_BUCKET

# Initialize Firebase
print(f"Using FIREBASE_CRED_PATH: {FIREBASE_CRED_PATH}")
cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred, {
    'storageBucket': FIREBASE_STORAGE_BUCKET
})
db = firestore.client()
bucket = storage.bucket()

def save_to_storage(file_path):
    """
    Uploads the file to Firebase Storage and returns the public URL.
    """
    blob_name = f"evidence/{os.path.basename(file_path)}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    blob.make_public()  # Make the file publicly accessible
    return blob.public_url

def save_metadata(analysis, storage_url, filename, pdf_bytes):
    """
    Saves report metadata including PDF bytes to Firestore and returns the document ID.
    """
    doc_ref = db.collection('reports').document()
    doc_ref.set({
        'filename': filename,
        'evidence_url': storage_url,
        'analysis': analysis,
        'pdf_bytes': pdf_bytes,  # Store PDF as bytes in Firestore
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    return doc_ref.id

def get_pdf_from_firestore(report_id):
    """
    Retrieves the PDF bytes from Firestore for the given report ID.
    """
    doc_ref = db.collection('reports').document(report_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get('pdf_bytes')
    return None

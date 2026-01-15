# Smart Evidence Report Writer

A web-based application for generating AI-powered police evidence reports using Google Vertex AI / Gemini.

## Features

- Upload images, videos, or text files as evidence
- AI analysis using Google Vertex AI / Gemini
- Generate structured police evidence reports
- Store evidence in Firebase Storage
- Save report metadata in Firestore
- Download reports as PDF
- Responsive web interface

## Project Structure

```
smart-evidence-writer/
├── backend/                    # Flask backend
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   └── utils/                  # Utility modules
│       ├── ai_analyzer.py      # Vertex AI integration
│       ├── firebase_storage.py # Firebase Storage/Firestore
│       └── pdf_generator.py    # PDF generation with ReportLab
├── frontend/                   # Static frontend
│   ├── index.html              # Main upload page
│   ├── styles.css              # CSS styling
│   ├── script.js               # JavaScript for form handling
│   └── assets/                 # Static assets
├── firebase.json               # Firebase hosting config
├── .env                        # Environment variables
└── README.md                   # This file
```

## Setup Instructions

1. **Clone or set up the project:**
   - Ensure you have Python 3.8+ installed
   - Install dependencies: `pip install -r backend/requirements.txt`

2. **Firebase Setup:**
   - Create a Firebase project
   - Enable Storage and Firestore
   - Download service account key and place it in the project root
   - Update `config.py` with your Firebase credentials

3. **Vertex AI Setup:**
   - Enable Vertex AI API in Google Cloud
   - Update `config.py` with your project ID and location

4. **Environment Variables:**
   - Create a `.env` file with necessary API keys and credentials

5. **Run the Backend:**
   - `cd backend`
   - `python app.py`

6. **Serve Frontend:**
   - Use a local server or deploy to Firebase Hosting
   - For local: `python -m http.server 8000` in frontend directory

## Usage

1. Open the frontend in a web browser
2. Select an evidence file (image, video, or text)
3. Click "Generate Report"
4. View the generated report and download PDF

## Optional Enhancements

- **Authentication:** Integrate Firebase Auth for user login
- **Batch Processing:** Use Celery + Redis for handling multiple uploads
- **Rich Text Editing:** Add a WYSIWYG editor for report customization
- **Dashboard:** View and manage past reports
- **Real-time Updates:** WebSocket integration for processing status
- **Advanced AI:** Custom prompts for different evidence types
- **Mobile App:** Convert to React Native or Flutter app

## Academic Project Notes

This project demonstrates:
- Integration of AI APIs (Vertex AI)
- Cloud storage solutions (Firebase)
- Web development (HTML/CSS/JS + Flask)
- PDF generation
- Asynchronous processing concepts
- Security considerations for file uploads

For academic evaluation, focus on:
- Code structure and documentation
- AI prompt engineering
- Error handling and user experience
- Scalability considerations

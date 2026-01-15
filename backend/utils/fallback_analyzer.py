# utils/fallback_analyzer.py
import os
import sys
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FallbackAnalyzer:
    def analyze_evidence(self, file_path):
        """Fallback analysis when Vertex AI is unavailable"""
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            return f"""
EVIDENCE ANALYSIS REPORT (FALLBACK MODE)
========================================

File Information:
- Filename: {filename}
- File Size: {file_size} bytes
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status: Vertex AI service temporarily unavailable due to network issues.

Basic File Analysis:
- File has been successfully uploaded and stored
- Basic metadata extracted
- Ready for manual review by investigators

Recommended Actions:
1. Check internet connection
2. Verify Google Cloud credentials
3. Try uploading the file again
4. Contact system administrator if issue persists

Note: This is a fallback analysis. For full AI-powered analysis, ensure:
- Stable internet connection
- Valid Google Cloud credentials
- Proper SSL configuration
"""
        except Exception as e:
            return f"Analysis Error: {str(e)}"

fallback_analyzer = FallbackAnalyzer()
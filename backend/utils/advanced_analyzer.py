# utils/advanced_analyzer.py
import vertexai
from google.cloud import videointelligence_v1 as vi
from google.cloud import vision
import os
import sys
import logging
from datetime import datetime
import json

# Path correction
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(UTILS_DIR)
sys.path.append(BACKEND_DIR)

from config import VERTEX_AI_PROJECT_ID, VERTEX_AI_LOCATION

# Initialize Vertex AI
vertexai.init(project=VERTEX_AI_PROJECT_ID, location=VERTEX_AI_LOCATION)

# Initialize clients with error handling
video_client = None
vision_client = None

try:
    video_client = vi.VideoIntelligenceServiceClient()
except Exception as e:
    logging.warning(f"Video Intelligence client initialization failed: {e}")

try:
    vision_client = vision.ImageAnnotatorClient()
except Exception as e:
    logging.warning(f"Vision client initialization failed: {e}")

logger = logging.getLogger(__name__)

class AdvancedEvidenceAnalyzer:
    def __init__(self):
        self.project_id = VERTEX_AI_PROJECT_ID
        self.location = VERTEX_AI_LOCATION
        
    def analyze_video_advanced(self, file_path):
        """Advanced video analysis with specialized features"""
        try:
            if not video_client:
                return self._fallback_video_analysis(file_path, "Video Intelligence API not configured")
                
            with open(file_path, "rb") as f:
                video_content = f.read()

            # Configure features for comprehensive analysis
            features = [
                vi.Feature.LABEL_DETECTION,
                vi.Feature.OBJECT_TRACKING,
                vi.Feature.SHOT_CHANGE_DETECTION,
                vi.Feature.EXPLICIT_CONTENT_DETECTION,
                vi.Feature.TEXT_DETECTION,
            ]

            # Run annotation
            operation = video_client.annotate_video(
                request={
                    "features": features,
                    "input_content": video_content,
                }
            )
            
            logger.info("Processing video analysis...")
            result = operation.result(timeout=300)
            
            return self._parse_video_analysis(result, file_path)
            
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
            return self._fallback_video_analysis(file_path, str(e))

    def _fallback_video_analysis(self, file_path, error_msg):
        """Fallback analysis when advanced features fail"""
        return {
            'file_info': {
                'filename': os.path.basename(file_path),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'basic_video_fallback'
            },
            'summary': {
                'status': 'basic_analysis',
                'message': f'Advanced video analysis unavailable: {error_msg}',
                'recommendation': 'Using standard Vertex AI analysis instead'
            }
        }

    def _parse_video_analysis(self, result, file_path):
        """Parse comprehensive video analysis results"""
        analysis = {
            'file_info': {
                'filename': os.path.basename(file_path),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'advanced_video'
            },
            'scene_analysis': [],
            'object_tracking': [],
            'key_events': [],
            'text_detections': [],
            'explicit_content': [],
            'summary': {}
        }

        try:
            # Process segment labels (scene classification)
            for annotation in result.segment_label_annotations:
                for segment in annotation.segments:
                    confidence = segment.confidence
                    if confidence > 0.5:
                        analysis['scene_analysis'].append({
                            'description': annotation.entity.description,
                            'confidence': round(confidence, 3),
                            'start_time': segment.segment.start_time_offset.total_seconds(),
                            'end_time': segment.segment.end_time_offset.total_seconds()
                        })

            # Process object tracking
            for annotation in result.object_annotations:
                analysis['object_tracking'].append({
                    'entity': annotation.entity.description,
                    'confidence': round(annotation.confidence, 3),
                    'track_id': annotation.track_id,
                    'timestamp': annotation.segment.start_time_offset.total_seconds()
                })

            # Process text detection
            for annotation in result.text_annotations:
                if hasattr(annotation, 'segments'):
                    for segment in annotation.segments:
                        analysis['text_detections'].append({
                            'text': annotation.text,
                            'confidence': round(segment.confidence, 3),
                            'timestamp': segment.segment.start_time_offset.total_seconds()
                        })

            # Process explicit content
            for frame in result.explicit_annotation.frames:
                analysis['explicit_content'].append({
                    'timestamp': frame.time_offset.total_seconds(),
                    'pornography_likelihood': vi.Likelihood(frame.pornography_likelihood).name
                })

        except Exception as e:
            logger.error(f"Error parsing video analysis: {e}")

        # Generate summary
        analysis['summary'] = self._generate_video_summary(analysis)
        
        return analysis

    def _generate_video_summary(self, analysis):
        """Generate a summary of video analysis"""
        try:
            unique_objects = set(obj['entity'] for obj in analysis['object_tracking'])
            scenes = set(scene['description'] for scene in analysis['scene_analysis'])
            text_found = len(analysis['text_detections']) > 0
            
            return {
                'total_objects_detected': len(unique_objects),
                'objects_list': list(unique_objects)[:10],
                'scenes_detected': len(scenes),
                'scene_types': list(scenes),
                'has_text': text_found,
                'key_events_count': len(analysis['key_events']),
                'analysis_confidence': 'high' if len(analysis['object_tracking']) > 5 else 'medium'
            }
        except Exception as e:
            logger.error(f"Error generating video summary: {e}")
            return {
                'status': 'summary_error',
                'message': 'Could not generate detailed summary'
            }

    def analyze_image_advanced(self, file_path):
        """Advanced image analysis with specialized features"""
        try:
            if not vision_client:
                return self._fallback_image_analysis(file_path, "Vision API not configured")
                
            with open(file_path, "rb") as f:
                image_content = f.read()

            image = vision.Image(content=image_content)
            
            # Multiple feature requests
            face_response = vision_client.face_detection(image=image)
            label_response = vision_client.label_detection(image=image)
            text_response = vision_client.text_detection(image=image)
            object_response = vision_client.object_localization(image=image)
            safe_search_response = vision_client.safe_search_detection(image=image)
            
            analysis = {
                'file_info': {
                    'filename': os.path.basename(file_path),
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'analysis_type': 'advanced_image'
                },
                'face_analysis': self._parse_face_detection(face_response),
                'object_detection': self._parse_object_detection(object_response),
                'text_detection': self._parse_text_detection(text_response),
                'label_analysis': self._parse_label_detection(label_response),
                'safe_search': self._parse_safe_search(safe_search_response),
                'summary': {}
            }
            
            analysis['summary'] = self._generate_image_summary(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return self._fallback_image_analysis(file_path, str(e))

    def _fallback_image_analysis(self, file_path, error_msg):
        """Fallback analysis when advanced features fail"""
        return {
            'file_info': {
                'filename': os.path.basename(file_path),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'basic_image_fallback'
            },
            'summary': {
                'status': 'basic_analysis',
                'message': f'Advanced image analysis unavailable: {error_msg}',
                'recommendation': 'Using standard Vertex AI analysis instead'
            }
        }

    def _parse_face_detection(self, response):
        """Parse face detection results"""
        faces = []
        try:
            for face in response.face_annotations:
                faces.append({
                    'joy_likelihood': vision.Likelihood(face.joy_likelihood).name,
                    'sorrow_likelihood': vision.Likelihood(face.sorrow_likelihood).name,
                    'anger_likelihood': vision.Likelihood(face.anger_likelihood).name,
                    'surprise_likelihood': vision.Likelihood(face.surprise_likelihood).name,
                    'headwear_likelihood': vision.Likelihood(face.headwear_likelihood).name,
                    'detection_confidence': round(face.detection_confidence, 3),
                    'bounding_poly': [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]
                })
        except Exception as e:
            logger.error(f"Error parsing face detection: {e}")
        return faces

    def _parse_object_detection(self, response):
        """Parse object detection results"""
        objects = []
        try:
            for obj in response.localized_object_annotations:
                objects.append({
                    'name': obj.name,
                    'confidence': round(obj.score, 3),
                    'bounding_poly': [(vertex.x, vertex.y) for vertex in obj.bounding_poly.normalized_vertices]
                })
        except Exception as e:
            logger.error(f"Error parsing object detection: {e}")
        return objects

    def _parse_text_detection(self, response):
        """Parse text detection results"""
        texts = []
        try:
            for text in response.text_annotations:
                texts.append({
                    'description': text.description,
                    'confidence': round(getattr(text, 'confidence', 0), 3),
                    'bounding_poly': [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
                })
        except Exception as e:
            logger.error(f"Error parsing text detection: {e}")
        return texts

    def _parse_label_detection(self, response):
        """Parse label detection results"""
        labels = []
        try:
            for label in response.label_annotations:
                if label.score > 0.7:
                    labels.append({
                        'description': label.description,
                        'confidence': round(label.score, 3),
                        'topicality': round(label.topicality, 3)
                    })
        except Exception as e:
            logger.error(f"Error parsing label detection: {e}")
        return labels

    def _parse_safe_search(self, response):
        """Parse safe search results"""
        try:
            safe_search = response.safe_search_annotation
            return {
                'adult': vision.Likelihood(safe_search.adult).name,
                'spoof': vision.Likelihood(safe_search.spoof).name,
                'medical': vision.Likelihood(safe_search.medical).name,
                'violence': vision.Likelihood(safe_search.violence).name,
                'racy': vision.Likelihood(safe_search.racy).name
            }
        except Exception as e:
            logger.error(f"Error parsing safe search: {e}")
            return {}

    def _generate_image_summary(self, analysis):
        """Generate summary of image analysis"""
        try:
            return {
                'faces_detected': len(analysis['face_analysis']),
                'objects_detected': len(analysis['object_detection']),
                'text_found': len(analysis['text_detection']) > 0,
                'labels_identified': len(analysis['label_analysis']),
                'content_safety': analysis['safe_search']
            }
        except Exception as e:
            logger.error(f"Error generating image summary: {e}")
            return {
                'status': 'summary_error',
                'message': 'Could not generate detailed summary'
            }

    def extract_key_frames(self, video_path, timestamps=None):
        """Extract key frames from video for evidence"""
        try:
            import cv2
            frames = []
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Cannot open video file: {video_path}")
                return []
            
            # If no specific timestamps, extract at regular intervals
            if not timestamps:
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0:
                    fps = 30  # Default assumption
                
                interval = max(1, total_frames // 8)  # 8 frames max
                
                for i in range(0, min(total_frames, 200), interval):  # Limit to 200 frames max
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        # Convert frame to base64 for storage
                        import base64
                        _, buffer = cv2.imencode('.jpg', frame)
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        frames.append({
                            'frame_number': i,
                            'timestamp': i / fps,
                            'timestamp_formatted': f"{int(i/fps/60):02d}:{int(i/fps%60):02d}",
                            'image_data': frame_base64
                        })
            else:
                # Extract at specific timestamps
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0:
                    fps = 30
                
                for timestamp in timestamps:
                    frame_number = int(timestamp * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = cap.read()
                    if ret:
                        import base64
                        _, buffer = cv2.imencode('.jpg', frame)
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        frames.append({
                            'frame_number': frame_number,
                            'timestamp': timestamp,
                            'timestamp_formatted': f"{int(timestamp/60):02d}:{int(timestamp%60):02d}",
                            'image_data': frame_base64
                        })
            
            cap.release()
            logger.info(f"Extracted {len(frames)} key frames from video")
            return frames
        except ImportError:
            logger.warning("OpenCV not available for frame extraction")
            return []
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return []

    def get_detailed_timeline(self, video_analysis):
        """Generate detailed chronological timeline from analysis"""
        try:
            timeline = []
            
            # Use object tracking for timeline events
            for obj in video_analysis.get('object_tracking', []):
                timeline.append({
                    'timestamp': obj['timestamp'],
                    'timestamp_formatted': f"{int(obj['timestamp']/60):02d}:{int(obj['timestamp']%60):02d}",
                    'event': f"{obj['entity']} detected",
                    'confidence': obj['confidence'],
                    'type': 'object'
                })
            
            # Use scene changes for timeline
            for scene in video_analysis.get('scene_analysis', []):
                timeline.append({
                    'timestamp': scene['start_time'],
                    'timestamp_formatted': f"{int(scene['start_time']/60):02d}:{int(scene['start_time']%60):02d}",
                    'event': f"Scene change: {scene['description']}",
                    'confidence': scene['confidence'],
                    'type': 'scene'
                })
            
            # Use text detections for timeline
            for text in video_analysis.get('text_detections', []):
                timeline.append({
                    'timestamp': text['timestamp'],
                    'timestamp_formatted': f"{int(text['timestamp']/60):02d}:{int(text['timestamp']%60):02d}",
                    'event': f"Text detected: {text['text'][:50]}...",
                    'confidence': text['confidence'],
                    'type': 'text'
                })
            
            # Sort by timestamp and remove duplicates
            timeline.sort(key=lambda x: x['timestamp'])
            
            # Remove near-duplicate events (within 1 second)
            unique_timeline = []
            last_timestamp = -10
            for event in timeline:
                if event['timestamp'] - last_timestamp > 1.0:  # 1 second threshold
                    unique_timeline.append(event)
                    last_timestamp = event['timestamp']
            
            return unique_timeline[:15]  # Limit to 15 most important events
        except Exception as e:
            logger.error(f"Timeline generation error: {e}")
            return []

    def enhance_ai_analysis(self, file_path, basic_analysis):
        """Enhance basic AI analysis with advanced features"""
        try:
            enhanced = {
                'basic_analysis': basic_analysis,
                'advanced_features': {},
                'file_info': {
                    'filename': os.path.basename(file_path),
                    'enhanced_at': datetime.utcnow().isoformat()
                }
            }
            
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                # Add video-specific enhancements
                video_analysis = self.analyze_video_advanced(file_path)
                
                enhanced['advanced_features'] = {
                    'scene_changes': len(video_analysis.get('scene_analysis', [])),
                    'objects_tracked': len(video_analysis.get('object_tracking', [])),
                    'text_detections': len(video_analysis.get('text_detections', [])),
                    'detailed_timeline': self.get_detailed_timeline(video_analysis),
                    'analysis_summary': video_analysis.get('summary', {})
                }
                
                # Extract key frames for important events
                important_timestamps = [event['timestamp'] for event in enhanced['advanced_features']['detailed_timeline'][:5]]
                enhanced['key_frames'] = self.extract_key_frames(file_path, important_timestamps)
            
            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                # Add image-specific enhancements
                image_analysis = self.analyze_image_advanced(file_path)
                enhanced['advanced_features'] = {
                    'faces_detected': len(image_analysis.get('face_analysis', [])),
                    'objects_detected': len(image_analysis.get('object_detection', [])),
                    'text_found': len(image_analysis.get('text_detection', [])) > 0,
                    'content_safety': image_analysis.get('safe_search', {}),
                    'analysis_summary': image_analysis.get('summary', {})
                }
            
            return enhanced
        except Exception as e:
            logger.error(f"Analysis enhancement error: {e}")
            # Return basic analysis if enhancement fails
            return {'basic_analysis': basic_analysis, 'enhancement_failed': str(e)}

# Singleton instance
advanced_analyzer = AdvancedEvidenceAnalyzer()
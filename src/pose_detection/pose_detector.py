"""
MediaPipe Pose Detection Module
Real-time human pose detection and landmark extraction
"""

import cv2
import mediapipe as mp
import numpy as np
import json
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PoseDetector:
    """MediaPipe-based pose detection class."""
    
    def __init__(self, 
                 model_complexity: int = 1,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 enable_segmentation: bool = True):
        """
        Initialize pose detector.
        
        Args:
            model_complexity: Complexity of the pose model (0, 1, or 2)
            min_detection_confidence: Minimum detection confidence
            min_tracking_confidence: Minimum tracking confidence
            enable_segmentation: Whether to enable segmentation
        """
        
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Key landmark indices for measurements
        self.key_landmarks = {
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28,
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 7,
            'right_ear': 8
        }
        
    def detect_pose(self, image: np.ndarray) -> Dict:
        """
        Detect pose landmarks in an image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary containing pose landmarks and metadata
        """
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.pose.process(rgb_image)
        
        pose_data = {
            'landmarks': None,
            'segmentation_mask': None,
            'pose_detected': False,
            'confidence': 0.0
        }
        
        if results.pose_landmarks:
            # Extract landmarks
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            pose_data['landmarks'] = landmarks
            pose_data['pose_detected'] = True
            pose_data['confidence'] = self._calculate_pose_confidence(landmarks)
            
            # Extract segmentation mask if available
            if results.segmentation_mask is not None:
                pose_data['segmentation_mask'] = results.segmentation_mask
                
        return pose_data
    
    def extract_key_points(self, landmarks: List[Dict]) -> Dict:
        """
        Extract key body measurement points.
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            Dictionary of key body points
        """
        
        if not landmarks or len(landmarks) < 33:
            return {}
        
        key_points = {}
        
        for name, index in self.key_landmarks.items():
            if index < len(landmarks):
                landmark = landmarks[index]
                if landmark['visibility'] > 0.5:  # Only include visible landmarks
                    key_points[name] = {
                        'x': landmark['x'],
                        'y': landmark['y'],
                        'z': landmark['z'],
                        'visibility': landmark['visibility']
                    }
        
        return key_points
    
    def calculate_body_measurements(self, key_points: Dict, image_shape: Tuple[int, int]) -> Dict:
        """
        Calculate body measurements from key points.
        
        Args:
            key_points: Dictionary of key body points
            image_shape: (height, width) of the image
            
        Returns:
            Dictionary of body measurements
        """
        
        measurements = {}
        height, width = image_shape
        
        try:
            # Shoulder width
            if 'left_shoulder' in key_points and 'right_shoulder' in key_points:
                left_shoulder = key_points['left_shoulder']
                right_shoulder = key_points['right_shoulder']
                
                shoulder_width_px = abs(left_shoulder['x'] - right_shoulder['x']) * width
                measurements['shoulder_width'] = shoulder_width_px
            
            # Hip width
            if 'left_hip' in key_points and 'right_hip' in key_points:
                left_hip = key_points['left_hip']
                right_hip = key_points['right_hip']
                
                hip_width_px = abs(left_hip['x'] - right_hip['x']) * width
                measurements['hip_width'] = hip_width_px
            
            # Torso length (shoulder to hip)
            if 'left_shoulder' in key_points and 'left_hip' in key_points:
                shoulder = key_points['left_shoulder']
                hip = key_points['left_hip']
                
                torso_length_px = abs(shoulder['y'] - hip['y']) * height
                measurements['torso_length'] = torso_length_px
            
            # Arm length (shoulder to wrist)
            if 'left_shoulder' in key_points and 'left_wrist' in key_points:
                shoulder = key_points['left_shoulder']
                wrist = key_points['left_wrist']
                
                arm_length_px = np.sqrt(
                    ((shoulder['x'] - wrist['x']) * width) ** 2 +
                    ((shoulder['y'] - wrist['y']) * height) ** 2
                )
                measurements['arm_length'] = arm_length_px
            
            # Waist width (estimated from torso proportions)
            if 'shoulder_width' in measurements and 'hip_width' in measurements:
                # Approximate waist as 0.75 of shoulder width
                measurements['waist_width'] = measurements['shoulder_width'] * 0.75
                
        except Exception as e:
            logger.error(f"Error calculating measurements: {e}")
            
        return measurements
    
    def draw_landmarks(self, image: np.ndarray, landmarks) -> np.ndarray:
        """
        Draw pose landmarks on image.
        
        Args:
            image: Input image
            landmarks: Pose landmarks from MediaPipe
            
        Returns:
            Image with drawn landmarks
        """
        
        if landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        return image
    
    def _calculate_pose_confidence(self, landmarks: List[Dict]) -> float:
        """
        Calculate overall pose confidence score.
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            Confidence score between 0 and 1
        """
        
        if not landmarks:
            return 0.0
        
        visible_landmarks = [lm for lm in landmarks if lm['visibility'] > 0.5]
        
        if len(visible_landmarks) == 0:
            return 0.0
        
        # Calculate average visibility of key landmarks
        key_visibility_scores = []
        for index in self.key_landmarks.values():
            if index < len(landmarks):
                key_visibility_scores.append(landmarks[index]['visibility'])
        
        if key_visibility_scores:
            return sum(key_visibility_scores) / len(key_visibility_scores)
        
        return 0.0
    
    def is_pose_stable(self, current_landmarks: List[Dict], 
                      previous_landmarks: List[Dict], 
                      threshold: float = 0.05) -> bool:
        """
        Check if pose is stable between frames.
        
        Args:
            current_landmarks: Current frame landmarks
            previous_landmarks: Previous frame landmarks
            threshold: Movement threshold for stability
            
        Returns:
            True if pose is stable
        """
        
        if not current_landmarks or not previous_landmarks:
            return False
        
        if len(current_landmarks) != len(previous_landmarks):
            return False
        
        total_movement = 0.0
        count = 0
        
        for i, (curr, prev) in enumerate(zip(current_landmarks, previous_landmarks)):
            if curr['visibility'] > 0.5 and prev['visibility'] > 0.5:
                movement = np.sqrt(
                    (curr['x'] - prev['x']) ** 2 +
                    (curr['y'] - prev['y']) ** 2
                )
                total_movement += movement
                count += 1
        
        if count > 0:
            avg_movement = total_movement / count
            return avg_movement < threshold
        
        return False
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'pose'):
            self.pose.close()

# Utility functions
def process_video_stream(detector: PoseDetector, video_source: int = 0):
    """
    Process video stream for real-time pose detection.
    
    Args:
        detector: PoseDetector instance
        video_source: Video source (0 for webcam)
    """
    
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        logger.error("Failed to open video source")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning("Failed to read frame")
                break
            
            # Detect pose
            pose_data = detector.detect_pose(frame)
            
            if pose_data['pose_detected']:
                # Draw landmarks
                frame = detector.draw_landmarks(frame, pose_data['landmarks'])
                
                # Extract measurements
                key_points = detector.extract_key_points(pose_data['landmarks'])
                measurements = detector.calculate_body_measurements(
                    key_points, frame.shape[:2]
                )
                
                # Display measurements
                y_offset = 30
                for measurement, value in measurements.items():
                    cv2.putText(frame, f"{measurement}: {value:.1f}px", 
                              (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.6, (0, 255, 0), 2)
                    y_offset += 25
            
            # Display frame
            cv2.imshow('Virtual Try-On - Pose Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()

if __name__ == "__main__":
    # Test pose detection
    detector = PoseDetector()
    process_video_stream(detector)

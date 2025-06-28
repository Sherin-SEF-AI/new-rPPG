"""
Face Detection Module using MediaPipe
Provides robust face detection and landmark extraction for rPPG processing.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional, List
import time


class FaceDetector:
    """Advanced face detector using MediaPipe for rPPG applications."""
    
    def __init__(self):
        """Initialize MediaPipe face detection."""
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range, 1 for full-range
            min_detection_confidence=0.5
        )
        
        # Initialize face mesh for landmarks
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.face_roi = None
        self.landmarks = None
        self.tracking_quality = 0.0
        self.last_detection_time = 0
        
    def detect_face(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], float]:
        """
        Detect face in the frame and return ROI and tracking quality.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (face_roi, tracking_quality)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face
        detection_results = self.face_detection.process(rgb_frame)
        
        if detection_results.detections:
            detection = detection_results.detections[0]  # Get first face
            
            # Get bounding box
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = frame.shape
            
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Ensure coordinates are within frame bounds
            x = max(0, x)
            y = max(0, y)
            width = min(width, w - x)
            height = min(height, h - y)
            
            # Extract face ROI
            face_roi = frame[y:y+height, x:x+width]
            
            # Calculate tracking quality based on confidence
            tracking_quality = detection.score[0]
            
            # Update landmarks
            self._update_landmarks(rgb_frame, (x, y, width, height))
            
            self.face_roi = face_roi
            self.tracking_quality = tracking_quality
            self.last_detection_time = time.time()
            
            return face_roi, tracking_quality
        
        return None, 0.0
    
    def _update_landmarks(self, rgb_frame: np.ndarray, bbox: Tuple[int, int, int, int]):
        """Update facial landmarks for signal extraction."""
        mesh_results = self.face_mesh.process(rgb_frame)
        
        if mesh_results.multi_face_landmarks:
            landmarks = mesh_results.multi_face_landmarks[0]
            self.landmarks = landmarks
        else:
            self.landmarks = None
    
    def get_forehead_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract forehead region for rPPG signal processing.
        
        Args:
            frame: Input frame
            
        Returns:
            Forehead ROI or None if landmarks not available
        """
        if self.landmarks is None:
            return None
        
        h, w, _ = frame.shape
        
        # Define forehead landmark indices (MediaPipe face mesh)
        # These are approximate indices for forehead region
        forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                           397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                           172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        # Extract forehead region
        forehead_points = []
        for idx in forehead_indices:
            if idx < len(self.landmarks.landmark):
                landmark = self.landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                forehead_points.append([x, y])
        
        if len(forehead_points) < 3:
            return None
        
        # Create mask for forehead region
        forehead_points = np.array(forehead_points, dtype=np.int32)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [forehead_points], 255)
        
        # Apply mask to frame
        forehead_roi = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Get bounding rectangle of forehead
        x, y, w_roi, h_roi = cv2.boundingRect(forehead_points)
        forehead_roi = forehead_roi[y:y+h_roi, x:x+w_roi]
        
        return forehead_roi
    
    def draw_face_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw face detection information on frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with face detection visualization
        """
        if self.face_roi is not None:
            # Draw face ROI rectangle
            h, w, _ = frame.shape
            roi_h, roi_w, _ = self.face_roi.shape
            
            # Calculate position (center the ROI)
            x = (w - roi_w) // 2
            y = (h - roi_h) // 2
            
            cv2.rectangle(frame, (x, y), (x + roi_w, y + roi_h), (0, 255, 0), 2)
            
            # Draw tracking quality
            quality_text = f"Quality: {self.tracking_quality:.2f}"
            cv2.putText(frame, quality_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw landmarks if available
            if self.landmarks is not None:
                self.mp_drawing.draw_landmarks(
                    frame, self.landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        color=(255, 0, 0), thickness=1, circle_radius=1
                    )
                )
        
        return frame
    
    def release(self):
        """Release resources."""
        self.face_detection.close()
        self.face_mesh.close() 
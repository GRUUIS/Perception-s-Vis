"""
Data Storage System
Handles saving and loading of audio recordings and visual outputs
"""

import json
import sqlite3
import os
import uuid
import datetime
import pickle
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pygame


@dataclass
class AudioRecord:
    """Represents a saved audio recording with metadata"""
    id: str
    timestamp: str
    duration: float
    sample_rate: int
    audio_metrics: Dict[str, List[float]]  # Time series of metrics
    visualization_settings: Dict[str, Any]
    user_name: str = "Anonymous"
    title: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class DatabaseManager:
    """Manages SQLite database for audio records"""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_records (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                duration REAL NOT NULL,
                sample_rate INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                title TEXT,
                tags TEXT,
                visualization_settings TEXT,
                file_path TEXT
            )
        ''')
        
        # Create metrics table for time series data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_metrics (
                record_id TEXT,
                metric_name TEXT,
                metric_data BLOB,
                FOREIGN KEY (record_id) REFERENCES audio_records (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_record(self, record: AudioRecord, audio_data: List[np.ndarray], 
                   visual_frames: List[pygame.Surface] = None) -> bool:
        """
        Save audio record to database and files
        
        Args:
            record: AudioRecord object
            audio_data: List of audio data arrays
            visual_frames: Optional list of pygame surfaces for video
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert record
            cursor.execute('''
                INSERT INTO audio_records 
                (id, timestamp, duration, sample_rate, user_name, title, tags, 
                 visualization_settings, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.id,
                record.timestamp,
                record.duration,
                record.sample_rate,
                record.user_name,
                record.title,
                json.dumps(record.tags),
                json.dumps(record.visualization_settings),
                f"recordings/{record.id}"
            ))
            
            # Insert metrics
            for metric_name, metric_data in record.audio_metrics.items():
                cursor.execute('''
                    INSERT INTO audio_metrics (record_id, metric_name, metric_data)
                    VALUES (?, ?, ?)
                ''', (record.id, metric_name, pickle.dumps(metric_data)))
                
            conn.commit()
            conn.close()
            
            # Save audio data to file
            self._save_audio_data(record.id, audio_data)
            
            # Save visual frames if provided
            if visual_frames:
                self._save_visual_frames(record.id, visual_frames)
                
            return True
            
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
            
    def load_record(self, record_id: str) -> Optional[Tuple[AudioRecord, List[np.ndarray]]]:
        """
        Load audio record from database
        
        Args:
            record_id: ID of the record to load
            
        Returns:
            Tuple of (AudioRecord, audio_data) or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get record
            cursor.execute('''
                SELECT id, timestamp, duration, sample_rate, user_name, title, 
                       tags, visualization_settings
                FROM audio_records WHERE id = ?
            ''', (record_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
                
            # Get metrics
            cursor.execute('''
                SELECT metric_name, metric_data FROM audio_metrics 
                WHERE record_id = ?
            ''', (record_id,))
            
            metrics_rows = cursor.fetchall()
            metrics = {}
            for metric_name, metric_data in metrics_rows:
                metrics[metric_name] = pickle.loads(metric_data)
                
            conn.close()
            
            # Create AudioRecord
            record = AudioRecord(
                id=row[0],
                timestamp=row[1],
                duration=row[2],
                sample_rate=row[3],
                user_name=row[4] or "Anonymous",
                title=row[5] or "",
                tags=json.loads(row[6]) if row[6] else [],
                visualization_settings=json.loads(row[7]) if row[7] else {},
                audio_metrics=metrics
            )
            
            # Load audio data
            audio_data = self._load_audio_data(record_id)
            
            return record, audio_data
            
        except Exception as e:
            print(f"Error loading record: {e}")
            return None
            
    def get_all_records(self, limit: int = 100) -> List[AudioRecord]:
        """
        Get all audio records from database
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of AudioRecord objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, duration, sample_rate, user_name, title, 
                       tags, visualization_settings
                FROM audio_records 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            records = []
            for row in rows:
                record = AudioRecord(
                    id=row[0],
                    timestamp=row[1],
                    duration=row[2],
                    sample_rate=row[3],
                    user_name=row[4] or "Anonymous",
                    title=row[5] or "",
                    tags=json.loads(row[6]) if row[6] else [],
                    visualization_settings=json.loads(row[7]) if row[7] else {},
                    audio_metrics={}  # Don't load full metrics for list view
                )
                records.append(record)
                
            return records
            
        except Exception as e:
            print(f"Error getting records: {e}")
            return []
            
    def delete_record(self, record_id: str) -> bool:
        """
        Delete record from database and files
        
        Args:
            record_id: ID of record to delete
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM audio_metrics WHERE record_id = ?', (record_id,))
            cursor.execute('DELETE FROM audio_records WHERE id = ?', (record_id,))
            
            conn.commit()
            conn.close()
            
            # Delete files
            self._delete_files(record_id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False
            
    def _save_audio_data(self, record_id: str, audio_data: List[np.ndarray]):
        """Save audio data to file"""
        recordings_dir = os.path.join(os.path.dirname(self.db_path), "recordings")
        os.makedirs(recordings_dir, exist_ok=True)
        
        file_path = os.path.join(recordings_dir, f"{record_id}_audio.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(audio_data, f)
            
    def _load_audio_data(self, record_id: str) -> List[np.ndarray]:
        """Load audio data from file"""
        recordings_dir = os.path.join(os.path.dirname(self.db_path), "recordings")
        file_path = os.path.join(recordings_dir, f"{record_id}_audio.pkl")
        
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []
            
    def _save_visual_frames(self, record_id: str, frames: List[pygame.Surface]):
        """Save visual frames as video or image sequence"""
        visualizations_dir = os.path.join(os.path.dirname(self.db_path), "visualizations")
        os.makedirs(visualizations_dir, exist_ok=True)
        
        # Save frames as individual images
        for i, frame in enumerate(frames):
            filename = f"{record_id}_frame_{i:04d}.png"
            file_path = os.path.join(visualizations_dir, filename)
            pygame.image.save(frame, file_path)
            
    def _delete_files(self, record_id: str):
        """Delete associated files"""
        recordings_dir = os.path.join(os.path.dirname(self.db_path), "recordings")
        visualizations_dir = os.path.join(os.path.dirname(self.db_path), "visualizations")
        
        # Delete audio file
        audio_file = os.path.join(recordings_dir, f"{record_id}_audio.pkl")
        if os.path.exists(audio_file):
            os.remove(audio_file)
            
        # Delete visualization frames
        for filename in os.listdir(visualizations_dir):
            if filename.startswith(f"{record_id}_frame_"):
                os.remove(os.path.join(visualizations_dir, filename))


class DataStorage:
    """Main data storage interface"""
    
    def __init__(self, data_dir: str):
        """
        Initialize data storage
        
        Args:
            data_dir: Directory for data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, "audio_perception.db")
        self.db_manager = DatabaseManager(db_path)
        
        # Recording state
        self.current_recording = None
        self.recorded_audio = []
        self.recorded_metrics = []
        self.visual_frames = []
        self.recording_start_time = None
        
    def start_recording_session(self, user_name: str = "Anonymous", title: str = ""):
        """
        Start a new recording session
        
        Args:
            user_name: Name of the user
            title: Title for the recording
        """
        self.current_recording = {
            'id': str(uuid.uuid4()),
            'user_name': user_name,
            'title': title,
            'start_time': datetime.datetime.now()
        }
        
        self.recorded_audio.clear()
        self.recorded_metrics.clear()
        self.visual_frames.clear()
        self.recording_start_time = datetime.datetime.now()
        
        print(f"Started recording session: {self.current_recording['id']}")
        
    def add_audio_data(self, audio_chunk: np.ndarray, metrics: Dict[str, float]):
        """
        Add audio data to current recording
        
        Args:
            audio_chunk: Audio data chunk
            metrics: Audio metrics for this chunk
        """
        if self.current_recording:
            self.recorded_audio.append(audio_chunk.copy())
            self.recorded_metrics.append(metrics.copy())
            
    def add_visual_frame(self, frame: pygame.Surface):
        """
        Add visual frame to current recording
        
        Args:
            frame: Pygame surface representing the frame
        """
        if self.current_recording:
            # Limit number of frames to save memory
            if len(self.visual_frames) < 300:  # ~10 seconds at 30fps
                self.visual_frames.append(frame.copy())
                
    def stop_recording_session(self, visualization_settings: Dict[str, Any] = None,
                              tags: List[str] = None) -> Optional[str]:
        """
        Stop current recording session and save data
        
        Args:
            visualization_settings: Settings used during visualization
            tags: Tags to associate with recording
            
        Returns:
            Recording ID if successful, None otherwise
        """
        if not self.current_recording or not self.recorded_audio:
            print("No active recording or no audio data")
            return None
            
        try:
            # Calculate duration
            duration = (datetime.datetime.now() - self.recording_start_time).total_seconds()
            
            # Organize metrics by type
            audio_metrics = {}
            for metric_name in ['amplitude', 'rms', 'peak', 'db', 'frequency']:
                audio_metrics[metric_name] = [
                    m.get(metric_name, 0.0) for m in self.recorded_metrics
                ]
                
            # Create AudioRecord
            record = AudioRecord(
                id=self.current_recording['id'],
                timestamp=self.current_recording['start_time'].isoformat(),
                duration=duration,
                sample_rate=44100,  # Default sample rate
                audio_metrics=audio_metrics,
                visualization_settings=visualization_settings or {},
                user_name=self.current_recording['user_name'],
                title=self.current_recording['title'],
                tags=tags or []
            )
            
            # Save to database
            success = self.db_manager.save_record(
                record, 
                self.recorded_audio, 
                self.visual_frames if self.visual_frames else None
            )
            
            if success:
                print(f"Recording saved: {record.id}")
                self.current_recording = None
                return record.id
            else:
                print("Failed to save recording")
                return None
                
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return None
            
    def get_all_recordings(self, limit: int = 100) -> List[AudioRecord]:
        """
        Get all saved recordings
        
        Args:
            limit: Maximum number of recordings to return
            
        Returns:
            List of AudioRecord objects
        """
        return self.db_manager.get_all_records(limit)
        
    def load_recording(self, record_id: str) -> Optional[Tuple[AudioRecord, List[np.ndarray]]]:
        """
        Load a specific recording
        
        Args:
            record_id: ID of recording to load
            
        Returns:
            Tuple of (AudioRecord, audio_data) or None
        """
        return self.db_manager.load_record(record_id)
        
    def delete_recording(self, record_id: str) -> bool:
        """
        Delete a recording
        
        Args:
            record_id: ID of recording to delete
            
        Returns:
            True if successful
        """
        return self.db_manager.delete_record(record_id)
        
    def get_recording_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored recordings
        
        Returns:
            Dictionary with statistics
        """
        records = self.get_all_recordings(1000)  # Get more for stats
        
        if not records:
            return {
                'total_recordings': 0,
                'total_duration': 0.0,
                'unique_users': 0,
                'most_active_user': 'None',
                'avg_duration': 0.0
            }
            
        total_duration = sum(r.duration for r in records)
        users = [r.user_name for r in records]
        unique_users = set(users)
        
        # Find most active user
        user_counts = {}
        for user in users:
            user_counts[user] = user_counts.get(user, 0) + 1
        most_active_user = max(user_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_recordings': len(records),
            'total_duration': total_duration,
            'unique_users': len(unique_users),
            'most_active_user': most_active_user,
            'avg_duration': total_duration / len(records) if records else 0.0
        }
    
    def save_recording(self, record_data: Dict[str, Any]) -> bool:
        """
        Save a recording with metadata
        
        Args:
            record_data: Dictionary containing recording information
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create AudioRecord from data
            record = AudioRecord(
                id=str(uuid.uuid4()),
                timestamp=datetime.datetime.now().isoformat(),
                duration=10.0,  # Default duration for live recordings
                sample_rate=44100,
                audio_metrics=record_data.get('audio_metrics', {}),
                visualization_settings=record_data.get('visualization_settings', {}),
                user_name=record_data.get('user_name', 'Anonymous'),
                title=record_data.get('title', 'Untitled'),
                tags=record_data.get('tags', [])
            )
            
            # Save to database with empty audio data for live recordings
            empty_audio_data = []  # Live recordings don't have stored audio chunks
            success = self.db_manager.save_record(record, empty_audio_data)
            
            if success:
                print(f"Recording saved: {record.title} by {record.user_name}")
            
            return success
            
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False
